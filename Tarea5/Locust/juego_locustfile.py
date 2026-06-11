import random
from faker import Faker
from locust import HttpUser, task, between

fake = Faker()

class TestAPIJuego(HttpUser):
    wait_time = between(1, 5)

    def _game_id(self):
        return random.randint(1,3)
    
    @task
    def list_games(self):
        self.client.get("/games/")

    @task
    def get_game(self):
        game_id = self._game_id()
        self.client.get(f"/games/{game_id}")

    @task
    def create_game(self):
        game_data = {
            "nombre": fake.word(),
        }
        self.client.post("/games/", json=game_data)

    @task
    def modify_game(self):
        id = self._game_id()
        game_data = {
            "id": id,
            "nombre": fake.word(),
        }
        self.client.put(f"/games/{id}", json=game_data)

    @task
    def delete_game(self):
        id = self._game_id()
        self.client.delete(f"/games/{id}")