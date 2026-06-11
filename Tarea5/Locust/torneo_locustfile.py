import random
from faker import Faker
from locust import HttpUser, task, between

fake = Faker()

class TestAPITorneo(HttpUser):
    wait_time = between(1, 5)    
    
    def _get_tournament_id(self):
        return random.randint(1,3)
    
    def _get_event_id(self):
        return random.randint(1,3)
    
    def _get_user_identity_id(self):
        return random.randint(1,3)
    
    @task
    def _get_game_id(self):
        return random.randint(1,3)

    @task
    def list_tournaments(self):
        self.client.get("/tourneys/")

    @task
    def get_tournament(self):
        tournament_id = self._get_tournament_id()
        self.client.get(f"/tourneys/{tournament_id}")

    # @task
    # def get_user_identity(self):
    #     user_identity_id = self._user_identity_id()
    #     self.client.get(f"/api/user-identities/{user_identity_id}")

    @task
    def create_tournament(self):
        tournament_data = {
            "name": fake.word(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "tipo": random.randint(1, 3),
            "eventoId": random.randint(1, 3),
        }
        self.client.post("/tourneys/", json=tournament_data)
    
    @task
    def update_tournament(self):
        tournament_id = self._get_tournament_id()
        tournament_data = {
            "id": tournament_id,
            "name": fake.word(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "tipo": random.randint(1, 3),
            "eventoId": random.randint(1, 3),
        }
        self.client.put(f"/tourneys/{tournament_id}", json=tournament_data)
        
    @task
    def delete_tournament(self):
        tournament_id = self._get_tournament_id()
        self.client.delete(f"/tourneys/{tournament_id}")

    @task
    def get_event_tournamets(self):
        event_id = self._get_event_id()
        self.client.get(f"/evento/{event_id}")

    @task
    def get_tournament_participants(self):
        tournament_id = self._get_tournament_id()
        self.client.get(f"/tourneys/{tournament_id}/participants")

    @task
    def register_participant(self):
        tournament_id = self._get_tournament_id()
        user_identity_id = self._get_user_identity_id()
        self.client.post(f"/users/{user_identity_id}/tournaments/{tournament_id}")

    @task
    def unregister_participant(self):
        tournament_id = self._get_tournament_id()
        user_identity_id = self._get_user_identity_id()
        self.client.delete(f"/users/{user_identity_id}/tournaments/{tournament_id}")

    @task
    def get_game_tournaments(self):
        game_id = self._get_game_id()
        self.client.get(f"/games/{game_id}")

    @task
    def get_games(self):
        game_id = self._get_game_id()
        self.client.get(f"/games/{game_id}")