import random
from faker import Faker
from locust import HttpUser, task, between

fake = Faker()

class TestAPIIdentity(HttpUser):
    wait_time = between(1, 5)

    def _user_identity_id(self):
        return random.randint(1,3)
    
    def _event_id(self):
        return random.randint(1,3)
    
    def _tournament_id(self):
        return random.randint(1,3)
    
    @task
    def list_user_identities(self):
        self.client.get("/users/")

    @task
    def get_user_identity(self):
        user_identity_id = self._user_identity_id()
        self.client.get(f"/users/{user_identity_id}")
    
    @task
    def create_user_identity(self):
        user_identity_data = {
            "nombre": fake.user_name(),
            "contrasena": fake.password(),
            "correo": fake.email(),
        }
        self.client.post("/users/", json=user_identity_data)

    @task
    def modify_user_identity(self):
        user_identity_id = self._user_identity_id()
        user_identity_data = {
            "id": user_identity_id,
            "nombre": fake.user_name(),
            "correo": fake.email(),
            "contrasena": fake.password(),
        }
        self.client.put(f"/users/{user_identity_id}", json=user_identity_data)

    @task
    def delete_user_identity(self):
        user_identity_id = self._user_identity_id()
        self.client.delete(f"/users/{user_identity_id}")

    @task
    def register_participant_event(self):
        user_identity_id = self._user_identity_id()
        event_id = self._event_id()
        self.client.post(f"/users/{user_identity_id}/events/{event_id}")

    @task
    def unregister_participant_event(self):
        user_identity_id = self._user_identity_id()
        event_id = self._event_id()
        self.client.delete(f"/users/{user_identity_id}/events/{event_id}")

    @task
    def register_participant_tournament(self):
        user_identity_id = self._user_identity_id()
        event_id = self._event_id()
        tournament_id = self._tournament_id()
        self.client.post(f"/users/{user_identity_id}/tournaments/{tournament_id}")

    @task
    def unregister_participant_tournament(self):
        user_identity_id = self._user_identity_id()
        event_id = self._event_id()
        tournament_id = self._tournament_id()
        self.client.delete(f"/users/{user_identity_id}/tournaments/{tournament_id}")