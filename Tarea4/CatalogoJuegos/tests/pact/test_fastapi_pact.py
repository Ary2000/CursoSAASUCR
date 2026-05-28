import pathlib

import pytest
from pact import Pact, Verifier, match

from app import app as fastapi_app
from pydantic import BaseModel, Field

class Juego(BaseModel):
    id: int = Field(..., description="Identificador único del usuario")
    nombre: str = Field(..., description="Nombre del participante")

_PROJECT_ROOT = pathlib.Path(__file__).parents[2]

PACT_DIR = str(_PROJECT_ROOT / "pacts")

PROVIDER_PORT = 5203

PACT_FILE = str(_PROJECT_ROOT / "pacts" / "CatalogoJuegosClient-FastAPICatalogoJuegosAPI.json")

pact = Pact("CatalogoJuegosClient", "FastAPICatalogoJuegosAPI")

@pytest.fixture(scope="class")
def fastapi_provider_url():
    return "http://catalogo-juegos:8000"


class TestFastAPIProvider:
    def test_provider_honour_pact(self, fastapi_provider_url):
        verifier = (
            Verifier("FastAPICatalogoJuegosAPI", host="catalogo-juegos")
            .add_transport(protocol="http", port=8000)
            .add_source(PACT_FILE)
        )
        verifier.verify()

        results = verifier.results
        failures = results.get("summary",{}).get("failureCount", 0)

        assert failures == 0, f"El proveedor FASTAPI no satisfizo {failures} interaccion(es): {results}"
