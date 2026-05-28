import pathlib
import threading
import time

import pytest
import requests
from pact import Pact, Verifier, match

_PROJECT_ROOT = pathlib.Path(__file__).parents[2]

PACT_DIR = str(_PROJECT_ROOT / "pacts")

MOCK_PORT = 5200

PROVIDER_PORT = 5201

PACT_FILE = str(_PROJECT_ROOT / "pacts" / "CatalogoJuegosClient-FastAPICatalogoJuegosAPI.json")

pact = Pact("CatalogoJuegosClient", "FastAPICatalogoJuegosAPI")

@pytest.fixture(scope="module", autouse=True)
def pack_mock():
    (
        pact.upon_receiving("GET /games")
            .given("There are games in the database")
            .with_request("get", "/games")
            .will_respond_with(200)
            .with_body(
                match.each_like({
                    "id": match.like(1),
                    "nombre": match.like("Super Smash Bros")
            }),
            content_type="application/json"
            )
        .with_header("Content-Type", "application/json")
     )
    (
        pact.upon_receiving("GET /games/1")
            .given("Find game with id 1")
            .with_request("get", "/games/1")
            .will_respond_with(200)
            .with_body(
                {
                    "id": match.like(1),
                    "nombre": match.like("Super Smash Bros")
                },
                content_type="application/json"
            )
        .with_header("Content-Type", "application/json")
    )
    (
        pact.upon_receiving("GET /games/999")
            .given("Receive error when looking for game with id 999")
            .with_request("get", "/games/999")
            .will_respond_with(404)
            .with_body(
                {"detail": match.like("Item no encontrado")},
                content_type="application/json"
            )
        .with_header("Content-Type", "application/json")
    )

    with pact.serve(port=MOCK_PORT, raises=False) as mock:
        mock.write_file(PACT_DIR, overwrite=True)
        yield mock

class TestFastAPIConsumer:
    def test_list_games(self, pack_mock):
        response = requests.get(f"{pack_mock.url}/games")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_game_by_id(self, pack_mock):
        response = requests.get(f"{pack_mock.url}/games/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_game_by_id_not_found(self, pack_mock):
        response = requests.get(f"{pack_mock.url}/games/999")
        assert response.status_code == 404