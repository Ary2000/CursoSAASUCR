import uuid
import requests
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import logging
from contextvars import ContextVar

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

logging.getLogger("uvicorn.access").disabled = True

def downstream() -> dict[str, str]:
    return {"X-Correlation-ID": correlation_id_var.get()}

app = FastAPI(
    title="Servicio de Catalogo de Juegos", 
    description="Microservicio encargado de gestionar el catalogo de juegos disponibles en la plataforma",
    version="1.0.0"
)

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = correlation_id_var.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info('%s %s %s', request.method, request.url.path, response.status_code)
        return response
    finally:
        correlation_id_var.reset(token)
    

class Juego(BaseModel):
    id: int = Field(..., description="Identificador único del usuario")
    nombre: str = Field(..., description="Nombre del participante")

class JuegoCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del participante")

class JuegoUpdate(BaseModel):
    nombre: str | None = Field(None, description="Nombre del participante")

class ErrorResponse(BaseModel):
    code: int
    message: str

JUEGOS: list[Juego] = [
    Juego(id=1, nombre="Super Smash Bros"),
    Juego(id=2, nombre="Street Fighter"),
    Juego(id=3, nombre="Pokemon VGC")
]

@app.get(
        '/',
        summary="Raíz",
        description="Mensaje de bienvenida",
        tags=["General"]
)
def root() -> dict[str, str]:
    return  {"message": "Microservicios de catalogo de juegos"};

@app.get(
    '/games',
    summary="Listar juegos",
    description="Devuelve todos los juegos registrados",
    tags=["Juego"]
)
def listGames() -> list[Juego]:
    return JUEGOS

@app.get(
    '/games/{id}',
    summary="Informaciónde un juego",
    description="Devuelve la información de un juego en específico",
    tags=["Juego"]
)
def getGame(id: int = Path(..., description="Identificador del juego a obtener")) -> Juego:
    for juego in JUEGOS:
        logging.info(f"Checking game with id {juego.id} against requested id {id}")
        if juego.id == id:
            return juego
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post(
    "/games",
    response_model=Juego,
    status_code=201,
    summary="Crear juego",
    description="Crea un nuevo juego",
    tags=["Juego"]
)
def createGame(body: JuegoCreate) -> Juego:
    next_id = max((juego.id for juego in JUEGOS), default=0) + 1
    juego = Juego(id=next_id, nombre=body.nombre)
    JUEGOS.append(juego)
    return juego

@app.put(
    "/games/{id}",
    response_model=Juego,
    summary="Actualizar juego",
    description="Utiliza el identificador para modificar el contenido de un juego",
    tags=["Juego"]
)
def updateGame(
    id: int = Path(...,
                        description="Identificador del juego a actualizar"),
    body: JuegoUpdate = ...,
) -> Juego:
    for i, juego in enumerate(JUEGOS):
        if juego.id == id:
            data = juego.model_dump()
            if body.nombre is not None:
                data["nombre"] = body.nombre
            JUEGOS[i] = Juego(**data)
            return JUEGOS[i]
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete(
    "/games/{id}",
    status_code=204,
    response_model=None,
    summary="Eliminar juego",
    description="Eliminar juego por medio de su identificador.",
    responses={
        204: {"description": "Ítem borrado correctamente"},
        404: {"description": "Ítem no encontrado", "model": ErrorResponse},
    },
    tags=["Juego"]
)
def deleteGame(
    id: int = Path(..., description="Identificador del juego a eliminar"),
) -> Response | JSONResponse:
    for i, game in enumerate(JUEGOS):
        if game.id == id:
            JUEGOS.pop(i)
            return Response(status_code=204)
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(code=404, message="Item not found").model_dump(),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True, log_config=None)