from fastapi import FastAPI, HTTPException
from strawberry.fastapi import GraphQLRouter
import strawberry
from datetime import datetime
import time
import requests
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import pika
import logging
import threading

load_dotenv("config.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Ensure all loggers use our configuration
logging.getLogger().setLevel(logging.INFO)

@strawberry.type
class Evento:
    id: int
    nombre: str
    descripcion: str
    icono: str
    fechaHoraInicio: datetime  # Use datetime for better GraphQL support
    fechaHoraFin: datetime
    ubicacion: str
    costoInscripcion: float

@strawberry.type
class Usuario:
    id: int = strawberry.field(description="Identificador único del usuario")
    nombre: str = strawberry.field(description="Nombre del participante")
    contrasena: str = strawberry.field(description="Contraseña de acceso del usuario")
    correo: str = strawberry.field(description="Correo del usuario")

@strawberry.type
class Torneo:
    id: int = strawberry.field(description="Identificador único del torneo")
    nombre: str = strawberry.field(description="Nombre del torneo")
    fechaHoraInicio: datetime = strawberry.field(description="Hora y fecha de inicio del torneo")
    fechaHoraFin: datetime = strawberry.field(description="Hora y fecha del fin del torneo")
    tipo: int = strawberry.field(description="Identificador del juego que se jugara en el torneo")
    eventoId: int = strawberry.field(description="Identificador del evento al que pertenece el torneo")
    premio: str | None = strawberry.field(default=None, description="Premio para los ganadores del torneo (Opcional)")


# Strawberry GraphQL type for Evento
@strawberry.type(
    description="Representa un evento en el sistema (identificador, nombre, descripción y otros detalles)."
)
class EventoType:
    id: int = strawberry.field(description="Identificador único del evento.")
    nombre: str = strawberry.field(description="Nombre del evento.")
    descripcion: str = strawberry.field(description="Descripción del evento.")
    icono: str = strawberry.field(description="URL del icono del evento.")
    fechaHoraInicio: str = strawberry.field(description="Fecha y hora de inicio del evento.")
    fechaHoraFin: str = strawberry.field(description="Fecha y hora de fin del evento.")
    ubicacion: str = strawberry.field(description="Ubicación del evento.")
    costoInscripcion: float = strawberry.field(description="Costo de inscripción al evento.")

    @classmethod
    def from_pydantic(cls, e: Evento) -> "EventoType":
        return cls(
            id=e.id,
            nombre=e.nombre,
            descripcion=e.descripcion,
            icono=e.icono,
            fechaHoraInicio=e.fechaHoraInicio,
            fechaHoraFin=e.fechaHoraFin,
            ubicacion=e.ubicacion,
            costoInscripcion=e.costoInscripcion
        )


@strawberry.type(description="Representa la participación de un usuario en un evento.")
class Participante:
    idEvento: int = strawberry.field(description="Identificador del evento.")
    idUsuario: int = strawberry.field(description="Identificador del usuario.")


@strawberry.type(description="Representa un participante de un torneo.")
class TournamentParticipant:
    id: int = strawberry.field(description="Identificador del participante.")
    torneoId: int = strawberry.field(description="Identificador del torneo.")


# In-memory demo data
EVENTOS: list[Evento] = [
    Evento(id=1, nombre="Connecturday", descripcion="La conveción más grande de videojuegos en Costa Rica",
           icono="https://cdn.eticket.cr/imagenes/artistas/220912135900342_performer_img2_550x385connecturday.jpg", fechaHoraInicio="2023-10-15T09:00:00", fechaHoraFin="2023-10-15T17:00:00",
           ubicacion="Centro de convenciones", costoInscripcion=15000.0),
    Evento(id=2, nombre="Haru", descripcion="Convención de anime, manga y cultura japonesa en Costa Rica",
           icono="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7EyUbDuZf5eC8rlYbyZos5hpeRxLwKvea2A&s", fechaHoraInicio="2023-10-16T10:00:00", fechaHoraFin="2023-10-16T16:00:00",
           ubicacion="Casta de Cristal", costoInscripcion=8000.0),
    Evento(id=3, nombre="K-Festival", descripcion="Feria gastronómica y cultural coreana en Costa Rica",
           icono="https://scontent.fsyq10-1.fna.fbcdn.net/v/t39.30808-6/631369211_1247371374252586_6149536669367943497_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=1d70fc&_nc_ohc=F7HFBRZ0XWkQ7kNvwH24tT8&_nc_oc=Adq47eJBVcCflSgtDaXJALBIpWpVlBxDjjaW2XdmBFTHIwMKNNyXxrO5zSC_OAgsUrE&_nc_zt=23&_nc_ht=scontent.fsyq10-1.fna&_nc_gid=uSehkt8HIbgx1JuUmD_g3g&_nc_ss=7a3a8&oh=00_Af3SxJMrl8VJyX6bK35UlkGMhZEo_sfofYQgSDWYRg1T2w&oe=69EA007D", fechaHoraInicio="2023-10-17T14:00:00", fechaHoraFin="2023-10-17T18:00:00",
           ubicacion="Sala de Conferencias B", costoInscripcion=60.0),
]

PARTICIPANTES: list[dict[str, int]] = [
    {"idEvento": 1, "idUsuario": 1},
    {"idEvento": 1, "idUsuario": 2},
    {"idEvento": 2, "idUsuario": 3},
    {"idEvento": 3, "idUsuario": 1},
    {"idEvento": 3, "idUsuario": 2},
    {"idEvento": 3, "idUsuario": 3},
]


@strawberry.type(description="Consulta de un evento y listado de los eventos registrados en el sistema.")
class Query:
    @strawberry.field(description="Devuelve la lista de todos los eventos.")
    def listarEventos(self) -> list[EventoType]:
        return [EventoType.from_pydantic(e) for e in EVENTOS]

    @strawberry.field(
        description="Devuelve un evento por su identificador. Retorna null si no existe."
    )
    def verEvento(self, id: int) -> EventoType | None:
        for e in EVENTOS:
            if e.id == id:
                return EventoType.from_pydantic(e)
        return None    
    
    @strawberry.field(description="Consulta de todos los eventos en los que participa un usuario.")
    def eventosUsuario(self, idUsuario: int) -> list[Participante]:
        lista_eventos = []
        for p in PARTICIPANTES:
            if p["idUsuario"] == idUsuario:
                lista_eventos.append(Participante(idEvento=p["idEvento"], idUsuario=p["idUsuario"]))
        return lista_eventos
    
    @strawberry.field(description="Consulta de todos los torneos dentro de un evento.")
    def listarTorneosEvento(self, idEvento: int) -> list[Torneo]:        
        response = requests.get(f"{os.getenv('TORNEOS_SERVICE')}/evento/{idEvento}")
        if response.status_code != 200:
            return []
        data = response.json()  # list of tournament IDs
        torneos = []
        for torneo_id in data:
            response2 = requests.get(f"{os.getenv('TORNEOS_SERVICE')}/tourneys/{torneo_id}")
            if response2.status_code == 200:
                torneo_data = response2.json()
                torneos.append(Torneo(**torneo_data))
        return torneos
        
    @strawberry.field(description="Consulta de participantes de un torneo.")
    def tournament_participants(self, idTorneo: int) -> list[TournamentParticipant]:
        response = requests.get(f"{os.getenv('TORNEOS_SERVICE')}/tourneys/{idTorneo}/participants").json()
        return [TournamentParticipant(id=user_id, torneoId=idTorneo) for user_id in response]
    
    @strawberry.field(description="Consultar los identificadores de los participantes inscritos en un evento.")
    def participantesEvento(self, idEvento: int) -> list[Participante]:
        return [Participante(idEvento=idEvento, idUsuario=p["idUsuario"]) for p in PARTICIPANTES if p["idEvento"] == idEvento]


@strawberry.type(description="Operaciones de escritura: crear, actualizar y eliminar eventos.")
class Mutation:
    @strawberry.mutation(
        description="Crea un nuevo evento. El ID se asigna automáticamente. Devuelve el evento creado."
    )
    def crearEvento(
        self,
        nombre: str,
        descripcion: str,
        icono: str,
        fechaHoraInicio: str,
        fechaHoraFin: str,
        ubicacion: str,
        costoInscripcion: float
    ) -> EventoType:
        new_id = max((e.id for e in EVENTOS), default=0) + 1
        evento = Evento(
            id=new_id,
            nombre=nombre,
            descripcion=descripcion,
            icono=icono,
            fechaHoraInicio=fechaHoraInicio,
            fechaHoraFin=fechaHoraFin,
            ubicacion=ubicacion,
            costoInscripcion=costoInscripcion
        )
        EVENTOS.append(evento)
        return EventoType.from_pydantic(evento)

    @strawberry.mutation(
        description="Actualiza un evento por ID. Solo se modifican los campos que envíes (el resto se mantiene). Devuelve null si no existe."
    )
    def modificarEvento(
        self,
        id: int,
        nombre: str | None = None,
        descripcion: str | None = None,
        icono: str | None = None,
        fechaHoraInicio: str | None = None,
        fechaHoraFin: str | None = None,
        ubicacion: str | None = None,
        costoInscripcion: float | None = None,
    ) -> EventoType | None:
        for i, e in enumerate(EVENTOS):
            if e.id == id:
                updated = Evento(
                    id=e.id,
                    nombre=nombre if nombre is not None else e.nombre,
                    descripcion=descripcion if descripcion is not None else e.descripcion,
                    icono=icono if icono is not None else e.icono,
                    fechaHoraInicio=fechaHoraInicio if fechaHoraInicio is not None else e.fechaHoraInicio,
                    fechaHoraFin=fechaHoraFin if fechaHoraFin is not None else e.fechaHoraFin,
                    ubicacion=ubicacion if ubicacion is not None else e.ubicacion,
                    costoInscripcion=costoInscripcion if costoInscripcion is not None else e.costoInscripcion,
                )
                EVENTOS[i] = updated
                return EventoType.from_pydantic(updated)
        return None

    @strawberry.mutation(
        description="Elimina un evento por ID. Devuelve true si se eliminó, false si no existía."
    )
    def eliminarEvento(self, id: int) -> bool:
        for i, e in enumerate(EVENTOS):
            if e.id == id:
                EVENTOS.pop(i)
                return True
        return False
    
    @strawberry.mutation(description="Ingresa un participante al evento.")
    def registrarParticipante(self, idUsuario: int, idEvento: int) -> str:
        for p in PARTICIPANTES:
            if p["idUsuario"] == idUsuario and p["idEvento"] == idEvento:
                return "El usuario ya está inscrito en el evento."
        PARTICIPANTES.append({"idUsuario": idUsuario, "idEvento": idEvento})
        return "Usuario inscrito exitosamente."
    
    @strawberry.mutation(description="Elimina un participante del evento.")
    def eliminarParticipante(self, idUsuario: int, idEvento: int) -> str:
        for i, p in enumerate(PARTICIPANTES):
            if p["idUsuario"] == idUsuario and p["idEvento"] == idEvento:
                PARTICIPANTES.pop(i)
                return "Usuario removido del evento exitosamente."
        return "El usuario no estaba inscrito en el evento."
    
    @strawberry.mutation(description="Crear un torneo asociado al evento.")
    def crearTorneo(self, idEvento: int, nombre: str, fechaHoraInicio: datetime, fechaHoraFin: datetime, tipo: int, premio: str) -> Torneo:
        response = requests.post(f"{os.getenv('TORNEOS_SERVICE')}/tourneys", json={
            "eventoId": idEvento,
            "nombre": nombre,
            "fechaHoraInicio": fechaHoraInicio.strftime("%Y-%m-%d %H:%M:%S") if fechaHoraInicio else None,
            "fechaHoraFin": fechaHoraFin.strftime("%Y-%m-%d %H:%M:%S") if fechaHoraFin else None,
            "tipo": tipo,
            "premio": premio
        })
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="El evento no existe.")
        data = response.json()
        return Torneo(**data)
    
    @strawberry.mutation(description="Actualizar un torneo asociado al evento.")
    def modificarTorneo(self, idTorneo: int, nombre: str | None = None, fechaHoraInicio: datetime | None = None, fechaHoraFin: datetime | None = None, tipo: int | None = None, premio: str | None = None) -> Torneo:
        response = requests.put(f"{os.getenv('TORNEOS_SERVICE')}/tourneys/{idTorneo}", json={
            "nombre": nombre,
            "fechaHoraInicio": fechaHoraInicio.isoformat() if fechaHoraInicio else None,
            "fechaHoraFin": fechaHoraFin.isoformat() if fechaHoraFin else None,
            "tipo": tipo,
            "premio": premio
        })
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="El torneo no existe.")
        data = response.json()
        # Parse ISO strings back to datetime
        if 'fechaHoraInicio' in data and data['fechaHoraInicio']:
            data['fechaHoraInicio'] = datetime.fromisoformat(data['fechaHoraInicio'].replace('Z', '+00:00'))
        if 'fechaHoraFin' in data and data['fechaHoraFin']:
            data['fechaHoraFin'] = datetime.fromisoformat(data['fechaHoraFin'].replace('Z', '+00:00'))
        return Torneo(**data)
    
    @strawberry.mutation(description="Eliminar un torneo asociado al evento.")
    def eliminarTorneo(self, idTorneo: int) -> str:
        response = requests.delete(f"{os.getenv('TORNEOS_SERVICE')}/tourneys/{idTorneo}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="El torneo no existe.")
        return "Torneo eliminado exitosamente."

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Event GraphQL API")
app.include_router(graphql_app, prefix="/graphql")

def callback_rabbitmq(ch, method, properties, body):
    try:
        message = body.decode('utf-8')
        logging.info(f"Mensaje recibido de RabbitMQ: {message}")
    except UnicodeDecodeError as e:
        logging.error(f"Error decodificando mensaje de RabbitMQ: {e}")
    except Exception as e:
        logging.error(f"Error procesando mensaje de RabbitMQ: {e}")


rabbitmq_host = os.getenv("RABBITMQ_HOST")

def rabbitmq_consumer():
    logging.info("Iniciando consumidor RabbitMQ...")
    while True:
        try:
            logging.info(f"Intentando conectar a RabbitMQ en {rabbitmq_host}")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue='torneos_queue', durable=True)
            channel.basic_consume(
                queue='torneos_queue', on_message_callback=callback_rabbitmq, auto_ack=True)
            logging.info("Esperando mensajes...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logging.warning(
                f"No se pudo conectar a RabbitMQ: {e}. Reintentando en 5 segundos...")
            time.sleep(5)
        except Exception as e:
            logging.error(f"Error inesperado en consumidor RabbitMQ: {e}")
            time.sleep(5)

@app.on_event("startup")
async def startup_event() -> None:
    logging.info("Iniciando el servidor de Eventos...")
    logging.info(f"RABBITMQ_HOST configurado como: {rabbitmq_host}")
    consumer_thread = threading.Thread(target=rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    logging.info("Hilo del consumidor RabbitMQ iniciado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)