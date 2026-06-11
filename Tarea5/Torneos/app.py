from contextvars import ContextVar
import logging
import os
import uuid
# from flask.cli import load_dotenv
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from datetime import datetime
import requests
from dotenv import load_dotenv

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")

class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get()
        return True


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s cid=[%(correlation_id)s] %(levelname)s %(name)s - %(message)s",
)

for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    uv_logger = logging.getLogger(name)
    uv_logger.handlers = []
    uv_logger.propagate = True  

for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter())

logger = logging.getLogger(__name__)

def downstream_headers() -> dict[str, str]:
    return {"X-Correlation-ID": correlation_id_var.get()}

logging.getLogger("uvicorn.access").disabled = True

load_dotenv("config.env")

app = FastAPI(
    title="Torneos",
    description="Microservicio encargado de manejar los torneos dentro de la plataforma",
    version="1.0.0"
)

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get(
        "X-Correlation-ID") or str(uuid.uuid4())

    token = correlation_id_var.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        client_host = request.client.host if request.client else "-"
        logger.info(f'{client_host} - "{request.method} {request.url.path} HTTP/1.1" {response.status_code}')
        return response
    finally:
        correlation_id_var.reset(token)

class Torneo(BaseModel):
    id: int = Field(..., description="Identificador único del torneo")
    nombre: str = Field(..., description="Nombre del torneo")
    fechaHoraInicio: datetime = Field(..., description="Hora y fecha de inicio del torneo")
    fechaHoraFin: datetime = Field(..., description="Hora y fecha del fin del torneo")
    tipo: int = Field(..., description="Identificador del juego que se jugara en el torneo")
    eventoId: int = Field(..., description="Identificador del evento al que pertenece el torneo")
    premio: str | None = Field(None, description="Premio para los ganadores del torneo (Opcional)")

class TorneoCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del torneo")
    fechaHoraInicio: datetime = Field(..., description="Hora y fecha de inicio del torneo")
    fechaHoraFin: datetime = Field(..., description="Hora y fecha del fin del torneo")
    tipo: int = Field(..., description="Identificador del juego que se jugara en el torneo")
    eventoId: int = Field(..., description="Identificador del evento al que pertenece el torneo")
    premio: str | None = Field(None, description="Premio para los ganadores del torneo (Opcional)")

class TorneoUpdate(BaseModel):
    nombre: str | None = Field(None, description="Nombre del torneo")
    fechaHoraInicio: datetime | None = Field(None, description="Hora y fecha de inicio del torneo")
    fechaHoraFin: datetime | None = Field(None, description="Hora y fecha del fin del torneo")
    tipo: int | None = Field(None, description="Identificador del juego que se jugara en el torneo")
    # eventoId: int | None = Field(None, description="Identificador del evento al que pertenece el torneo")
    premio: str | None = Field(None, description="Premio para los ganadores del torneo (Opcional)")

class Juego(BaseModel):
    id: int = Field(..., description="Identificador único del usuario")
    nombre: str = Field(..., description="Nombre del participante")

class ErrorResponse(BaseModel):
    code: int
    message: str

TORNEOS: list[Torneo] = [
    Torneo(id=1, nombre="Starbits", fechaHoraInicio=datetime.strptime("2026-01-01 14:00:00", "%Y-%m-%d %H:%M:%S"), fechaHoraFin=datetime.strptime("2026-01-01 14:00:00", "%Y-%m-%d %H:%M:%S"), tipo=1, eventoId=1, premio="12 colones"),
    Torneo(id=2, nombre="Ryu from streets", fechaHoraInicio=datetime.strptime("2025-05-05 05:00:00", "%Y-%m-%d %H:%M:%S"), fechaHoraFin=datetime.strptime("2025-05-05 05:00:00", "%Y-%m-%d %H:%M:%S"), tipo=2, eventoId=2),
    Torneo(id=3, nombre="Wolfey bug month", fechaHoraInicio=datetime.strptime("2025-05-05 05:00:00", "%Y-%m-%d %H:%M:%S"), fechaHoraFin=datetime.strptime("2025-05-05 05:00:00", "%Y-%m-%d %H:%M:%S"), tipo=3, eventoId=3),
]

PARTICIPANTES: list[dict[str, int]] = [
    {"idTorneo": 1, "idUsuario": 1},
    {"idTorneo": 1, "idUsuario": 2},
    {"idTorneo": 2, "idUsuario": 3},
    {"idTorneo": 3, "idUsuario": 1},
    {"idTorneo": 3, "idUsuario": 2},
    {"idTorneo": 3, "idUsuario": 3},
]


@app.get(
        '/',
        summary="Raíz",
        description="Mensaje de bienvenida",
        tags=["General"]
)
def root() -> dict[str, str]:
    return  {"message": "Welcome to the Basic REST API"};

@app.get(
    '/tourneys',
    summary="Listar torneos",
    description="Devuelve todos los torneos registrados",
    tags=["Torneo"]
)
def lsitarTorneos() -> list[Torneo]:
    return TORNEOS

@app.get(
    '/tourneys/{id}',
    summary="Informaciónde un torneo",
    description="Devuelve la información de un torneo en específico",
    tags=["Torneo"]
)
def verTorneo(id: int = Path(..., description="Identificador del torneo a consultar")) -> Torneo:
    for torneo in TORNEOS:
        if torneo.id == id:
            return torneo
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post(
    "/tourneys",
    response_model=Torneo,
    status_code=201,
    summary="Crear torneo",
    description="Crea un nuevo torneo",
    tags=["Torneo"]
)
def crearTorneo(body: TorneoCreate) -> Torneo:
    next_id = max((torneo.id for torneo in TORNEOS), default=0) + 1
    torneo = Torneo(id=next_id, nombre=body.nombre, fechaHoraInicio=body.fechaHoraInicio, fechaHoraFin=body.fechaHoraFin, tipo=body.tipo, eventoId=body.eventoId, premio=body.premio if body.premio != None else None)
    TORNEOS.append(torneo)
    return torneo

@app.put(
    "/tourneys/{item_id}",
    response_model=Torneo,
    summary="Actualizar torneo",
    description="Utiliza el identificador para modificar el contenido de un torneo",
    tags=["Torneo"]
)
def actualizarTorneo(
    item_id: int = Path(...,
                        description="Identificador del torneo a actualizar"),
    body: TorneoUpdate = ...,
) -> Torneo:
    for i, torneo in enumerate(TORNEOS):
        if torneo.id == item_id:
            data = torneo.model_dump()
            if body.nombre is not None:
                data["nombre"] = body.nombre
            if body.fechaHoraInicio is not None:
                data["fechaHoraInicio"] = body.fechaHoraInicio
            if body.fechaHoraFin is not None:
                data["fechaHoraFin"] = body.fechaHoraFin
            if body.tipo is not None:
                data["tipo"] = body.tipo
            # if body.eventoId is not None:
            #     data["eventoId"] = body.eventoId
            if body.premio is not None:
                data["premio"] = body.premio
            TORNEOS[i] = Torneo(**data)
            return TORNEOS[i]
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete(
    "/tourneys/{user_id}",
    status_code=204,
    response_model=None,
    summary="Eliminar torneo",
    description="Eliminar torneo por medio de su identificador.",
    responses={
        204: {"description": "Ítem borrado correctamente"},
        404: {"description": "Ítem no encontrado", "model": ErrorResponse},
    },
    tags=["Torneo"]
)
def borrarTorneo(
    user_id: int = Path(..., description="Identificador del torneo a eliminar"),
) -> Response | JSONResponse:
    for i, user in enumerate(TORNEOS):
        if user.id == user_id:
            TORNEOS.pop(i)
            return Response(status_code=204)
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(code=404, message="Item not found").model_dump(),
    )

@app.get(
    "/evento/{idEvento}",
    summary="Listar torneos de un evento",
    description="Devuelve una lista con los identificadores de los torneos asociados a un evento específico",
    tags=["Evento"]
)
def listarTorneosEvento(idEvento: int = Path(..., description="Identificador del evento a consultar")) -> list[int]:
    torneos = []
    for torneo in TORNEOS:
        if torneo.eventoId == idEvento:
            torneos.append(torneo.id)
    return torneos


@app.get(
    "/tourneys/{id}/participants",
    summary="Listar participantes de un torneo",
    description="Devuelve una lista con los identificadores de los usuarios participantes de un torneo específico",
    tags=["Torneo"]
)
def listarParticipantes(id: int = Path(..., description="Identificador del torneo a consultar")) -> list[int]:
    participantes = []
    for participante in PARTICIPANTES:
        if participante["idTorneo"] == id:
            participantes.append(participante["idUsuario"])
    return participantes

@app.post(
    "/users/{user_id}/tournaments/{tournament_id}",
    summary="Registrar participante en torneo",
    description="Registra a un usuario como participante de un torneo específico.",
    tags=["Torneo"]
)
def registrarParticipanteTorneo(
        user_id: int = Path(..., description="Identificador del usuario a registrar"),
        tournament_id: int = Path(..., description="Identificador del torneo al que se desea registrar"),
) -> dict[str, str]:
    # Verificar que el torneo existe
    torneo_existe = any(torneo.id == tournament_id for torneo in TORNEOS)
    if not torneo_existe:
        raise HTTPException(status_code=404, detail="El torneo no existe.")
    PARTICIPANTES.append({"idTorneo": tournament_id, "idUsuario": user_id})
    return {"message": f"Usuario {user_id} registrado en el torneo {tournament_id} exitosamente."}

@app.delete(
    "/users/{user_id}/tournaments/{tournament_id}",
    summary="Eliminar participante de torneo",
    description="Elimina a un usuario como participante de un torneo específico.",
    tags=["Torneo"]
)
def eliminarParticipanteTorneo(
    user_id: int = Path(..., description="Identificador del usuario a eliminar"),
    tournament_id: int = Path(..., description="Identificador del torneo del que se desea eliminar al participante"),
):
    for i, participante in enumerate(PARTICIPANTES):
        if participante["idTorneo"] == tournament_id and participante["idUsuario"] == user_id:
            PARTICIPANTES.pop(i)
            return {"message": f"Usuario {user_id} eliminado del torneo {tournament_id} exitosamente."}
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(code=404, message="Participante no encontrado en el torneo").model_dump(),
    )

@app.get(
    "/games/{id}",
    summary="Información de un juego",
    description="Devuelve la información de un juego en específico",
    tags=["Juego"]
)
def verJuego(id: int = Path(..., description="Identificador del juego a obtener")) -> Juego:
    response = requests.get(f"{os.getenv('CATALOGO_JUEGOS_SERVICE')}/games/{id}", headers=downstream_headers())

    # Si el servicio externo responde 404, lo propagamos al cliente
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="El juego no existe.")
    
    data = response.json()
    return Juego(**data)

@app.get(
    "/games",
    summary="Listar juegos",
    description="Devuelve una lista con la información de todos los juegos disponibles",
    tags=["Juego"]
)
def listarJuegos() -> list[Juego]:
    response = requests.get(f"{os.getenv('CATALOGO_JUEGOS_SERVICE')}/games", headers=downstream_headers()).json()
    return [Juego(**game) for game in response]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
    # app.run(debug=True, port=8000, reload=True)