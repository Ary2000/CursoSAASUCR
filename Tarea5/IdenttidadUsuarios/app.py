from contextvars import ContextVar
import logging
import uuid

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv
import os

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

load_dotenv("config.env")

app = FastAPI(
    title="Identidad",
    description="Microservicios encargado de manejar las identidades de las personas registradas en la plataforma",
    version="1.0.0"
)

logging.getLogger("uvicorn.access").disabled = True

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

class Usuario(BaseModel):
    id: int = Field(..., description="Identificador único del usuario")
    nombre: str = Field(..., description="Nombre del participante")
    contrasena: str = Field(..., description="Contraseña de acceso del usuario")
    correo: str = Field(..., description="Correo del usuario")

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del participante")
    contrasena: str = Field(..., description="Contraseña de acceso del usuario")
    correo: str = Field(..., description="Correo del usuario")

class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, description="Nombre del participante")
    contrasena: str | None = Field(None, description="Contraseña de acceso del usuario")
    correo: str | None = Field(None, description="Correo del usuario")

class ErrorResponse(BaseModel):
    code: int
    message: str

USUARIOS: list[Usuario] = [
    Usuario(id=1, nombre="Ary El", contrasena="Ary", correo="correo@dominio.com"),
    Usuario(id=2, nombre="Sheyris", contrasena="SheyCa", correo="shey@ca.com"),
    Usuario(id=3, nombre="El hombre", contrasena="El hombre", correo="el@hombre.com")
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
    '/users',
    summary="Listar usuarios",
    description="Devuelve todos los usuarios registrados",
    tags=["Usuarios"]
)
def lsitarUsuarios() -> list[Usuario]:
    return USUARIOS

@app.get(
    '/users/{id}',
    summary="Informaciónde un usuario",
    description="Devuelve la información de un usuario en específico",
    tags=["Usuarios"]
)
def verUsuario(id: int = Path(..., description="Identificador del usuario a obtener")) -> Usuario:
    for usuario in USUARIOS:
        if usuario.id == id:
            return usuario
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post(
    "/users",
    response_model=Usuario,
    status_code=201,
    summary="Crear usuario",
    description="Crea un nuevo usuario",
    tags=["Usuarios"]
)
def crearUsuario(body: UsuarioCreate) -> Usuario:
    next_id = max((usuario.id for usuario in USUARIOS), default=0) + 1
    usuario = Usuario(id=next_id, nombre=body.nombre, contrasena=body.contrasena, correo=body.correo)
    USUARIOS.append(usuario)
    return usuario

@app.put(
    "/users/{item_id}",
    response_model=Usuario,
    summary="Actualizar usuario",
    description="Utiliza el identificador para modificar el contenido de un usuario",
    tags=["Usuarios"]
)
def actualizarUsuario(
    item_id: int = Path(...,
                        description="Identificador del usuario a actualizar"),
    body: UsuarioUpdate = ...,
) -> Usuario:
    for i, usuario in enumerate(USUARIOS):
        if usuario.id == item_id:
            data = usuario.model_dump()
            if body.nombre is not None:
                data["nombre"] = body.nombre
            if body.contrasena is not None:
                data["contrasena"] = body.contrasena
            if body.correo is not None:
                data["correo"] = body.correo
            USUARIOS[i] = Usuario(**data)
            return USUARIOS[i]
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete(
    "/users/{user_id}",
    status_code=204,
    response_model=None,
    summary="Eliminar usuario",
    description="Eliminar usuario por medio de su identificador.",
    responses={
        204: {"description": "Ítem borrado correctamente"},
        404: {"description": "Ítem no encontrado", "model": ErrorResponse},
    },
    tags=["Usuarios"]
)
def eliminarUsuario(
    user_id: int = Path(..., description="Identificador del usuario a eliminar"),
) -> Response | JSONResponse:
    for i, user in enumerate(USUARIOS):
        if user.id == user_id:
            USUARIOS.pop(i)
            return Response(status_code=204)
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(code=404, message="Item not found").model_dump(),
    )
@app.post(
    "/users/{user_id}/events/{event_id}",
    summary="Registrar participante en evento",
    description="Registra a un usuario como participante de un evento específico.",
    tags=["Eventos"]
)
def registrarParticipanteEvento(
        user_id: int = Path(..., description="Identificador del participante a registrar"),
        event_id: int = Path(..., description="Identificador del evento al que se registrará el participante")
    ) -> bool:
    url = f"{os.getenv('EVENTOS_URL')}/graphql"

    query = """
    mutation MyMutation {
      registrarParticipante(idEvento: %s, idUsuario: %s) 
    }
    """ % (event_id, user_id)

    response = requests.post(url, headers=downstream_headers(), json={"query": query})
    return response.status_code == 200

@app.delete(
    "/users/{user_id}/events/{event_id}",
    summary="Eliminar participante de evento",
    description="Elimina a un usuario como participante de un evento específico.",
    tags=["Eventos"]
)
def eliminarParticipanteEvento(
    user_id: int = Path(..., description="Identificador del participante a eliminar"),
    event_id: int = Path(..., description="Identificador del evento del que se eliminará el participante")
) -> bool:
    url = f"{os.getenv('EVENTOS_URL')}/graphql"

    query = """
    mutation MyMutation {
      eliminarParticipante(idEvento: %s, idUsuario: %s)
    }
    """ % (event_id, user_id)

    response = requests.post(url, headers=downstream_headers(), json={"query": query})
    return response.status_code == 200

@app.post(
    "/users/{user_id}/tournaments/{tournament_id}",
    summary="Registrar participante en torneo",
    description="Registra a un usuario como participante de un torneo específico.",
    tags=["Torneos"]
)
def registrarParticipanteTorneo(
    user_id: int = Path(..., description="Identificador del participante a registrar"),
    tournament_id: int = Path(..., description="Identificador del torneo al que se registrará el participante")
) -> bool:
    url = f"{os.getenv('TORNEOS_URL')}/users/{user_id}/tournaments/{tournament_id}"
    response = requests.post(url, headers=downstream_headers())
    return response.status_code == 200

@app.delete(
    "/users/{user_id}/tournaments/{tournament_id}",
    summary="Eliminar participante de torneo",
    description="Elimina a un usuario como participante de un torneo específico.",
    tags=["Torneos"]
)
def eliminarParticipanteTorneo(
    user_id: int = Path(..., description="Identificador del participante a eliminar"),
    tournament_id: int = Path(..., description="Identificador del torneo del que se eliminará el participante")
) -> bool:
    url = f"{os.getenv('TORNEOS_URL')}/users/{user_id}/tournaments/{tournament_id}"
    response = requests.delete(url, headers=downstream_headers())
    return response.status_code == 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_config=None)