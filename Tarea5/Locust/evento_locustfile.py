import random
from faker import Faker
from locust import HttpUser, task, between

fake = Faker()

class TestAPIEvento(HttpUser):
    wait_time = between(1, 5)

    def _event_id(self):
        return random.randint(1, 3)

    def _user_id(self):
        return random.randint(1, 3)

    def _tournament_id(self):
        return random.randint(1, 3)

    def _post(self, query, variables=None, name=None):
        payload = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        self.client.post("/graphql", json=payload, name=name)

    @task
    def list_events(self):
        query = """
        query {
          listarEventos {
            id
            nombre
            descripcion
            icono
            fechaHoraInicio
            fechaHoraFin
            ubicacion
            costoInscripcion
          }
        }
        """
        self._post(query, name="listarEventos")

    @task
    def get_event(self):
        event_id = self._event_id()
        query = """
        query VerEvento($id: Int!) {
          verEvento(id: $id) {
            id
            nombre
            descripcion
            icono
            fechaHoraInicio
            fechaHoraFin
            ubicacion
            costoInscripcion
          }
        }
        """
        self._post(query, {"id": event_id}, name="verEvento")

    @task
    def get_participant_events(self):
        user_id = self._user_id()
        query = """
        query EventosUsuario($idUsuario: Int!) {
          eventosUsuario(idUsuario: $idUsuario) {
            idEvento
            idUsuario
          }
        }
        """
        self._post(query, {"idUsuario": user_id}, name="eventosUsuario")

    @task
    def get_event_tournaments(self):
        event_id = self._event_id()
        query = """
        query ListarTorneosEvento($idEvento: Int!) {
          listarTorneosEvento(idEvento: $idEvento) {
            id
            nombre
            fechaHoraInicio
            fechaHoraFin
            tipo
            eventoId
            premio
          }
        }
        """
        self._post(query, {"idEvento": event_id}, name="listarTorneosEvento")

    @task
    def get_event_participants(self):
        event_id = self._event_id()
        query = """
        query ParticipantesEvento($idEvento: Int!) {
          participantesEvento(idEvento: $idEvento) {
            idEvento
            idUsuario
          }
        }
        """
        self._post(query, {"idEvento": event_id}, name="participantesEvento")

    @task
    def get_tournament_participants(self):
        tournament_id = self._tournament_id()
        query = """
        query TournamentParticipants($idTorneo: Int!) {
          tournamentParticipants(idTorneo: $idTorneo) {
            id
            torneoId
          }
        }
        """
        self._post(query, {"idTorneo": tournament_id}, name="tournament_participants")

    @task
    def create_event(self):
        query = """
        mutation CrearEvento(
          $nombre: String!
          $descripcion: String!
          $icono: String!
          $fechaHoraInicio: String!
          $fechaHoraFin: String!
          $ubicacion: String!
          $costoInscripcion: Float!
        ) {
          crearEvento(
            nombre: $nombre
            descripcion: $descripcion
            icono: $icono
            fechaHoraInicio: $fechaHoraInicio
            fechaHoraFin: $fechaHoraFin
            ubicacion: $ubicacion
            costoInscripcion: $costoInscripcion
          ) {
            id
            nombre
          }
        }
        """
        variables = {
            "nombre": fake.word(),
            "descripcion": fake.sentence(),
            "icono": fake.image_url(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "ubicacion": fake.address(),
            "costoInscripcion": round(random.uniform(10.0, 100.0), 2),
        }
        self._post(query, variables, name="crearEvento")

    @task
    def modify_event(self):
        event_id = self._event_id()
        query = """
        mutation ModificarEvento(
          $id: Int!
          $nombre: String
          $descripcion: String
          $icono: String
          $fechaHoraInicio: String
          $fechaHoraFin: String
          $ubicacion: String
          $costoInscripcion: Float
        ) {
          modificarEvento(
            id: $id
            nombre: $nombre
            descripcion: $descripcion
            icono: $icono
            fechaHoraInicio: $fechaHoraInicio
            fechaHoraFin: $fechaHoraFin
            ubicacion: $ubicacion
            costoInscripcion: $costoInscripcion
          ) {
            id
            nombre
          }
        }
        """
        variables = {
            "id": event_id,
            "nombre": fake.word(),
            "descripcion": fake.sentence(),
            "icono": fake.image_url(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "ubicacion": fake.address(),
            "costoInscripcion": round(random.uniform(10.0, 100.0), 2),
        }
        self._post(query, variables, name="modificarEvento")

    @task
    def delete_event(self):
        event_id = self._event_id()
        query = """
        mutation EliminarEvento($id: Int!) {
          eliminarEvento(id: $id)
        }
        """
        self._post(query, {"id": event_id}, name="eliminarEvento")

    @task
    def register_participant(self):
        user_id = self._user_id()
        event_id = self._event_id()
        query = """
        mutation RegistrarParticipante($idUsuario: Int!, $idEvento: Int!) {
          registrarParticipante(idUsuario: $idUsuario, idEvento: $idEvento)
        }
        """
        self._post(query, {"idUsuario": user_id, "idEvento": event_id}, name="registrarParticipante")

    @task
    def unregister_participant(self):
        user_id = self._user_id()
        event_id = self._event_id()
        query = """
        mutation EliminarParticipante($idUsuario: Int!, $idEvento: Int!) {
          eliminarParticipante(idUsuario: $idUsuario, idEvento: $idEvento)
        }
        """
        self._post(query, {"idUsuario": user_id, "idEvento": event_id}, name="eliminarParticipante")

    @task
    def register_tournament(self):
        event_id = self._event_id()
        query = """
        mutation CrearTorneo(
          $idEvento: Int!
          $nombre: String!
          $fechaHoraInicio: DateTime!
          $fechaHoraFin: DateTime!
          $tipo: Int!
          $premio: String!
        ) {
          crearTorneo(
            idEvento: $idEvento
            nombre: $nombre
            fechaHoraInicio: $fechaHoraInicio
            fechaHoraFin: $fechaHoraFin
            tipo: $tipo
            premio: $premio
          ) {
            id
            nombre
          }
        }
        """
        variables = {
            "idEvento": event_id,
            "nombre": fake.word(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "tipo": random.randint(1, 3),
            "premio": fake.sentence(),
        }
        self._post(query, variables, name="crearTorneo")

    @task
    def modify_tournament(self):
        tournament_id = self._tournament_id()
        query = """
        mutation ModificarTorneo(
          $idTorneo: Int!
          $nombre: String
          $fechaHoraInicio: DateTime
          $fechaHoraFin: DateTime
          $tipo: Int
          $premio: String
        ) {
          modificarTorneo(
            idTorneo: $idTorneo
            nombre: $nombre
            fechaHoraInicio: $fechaHoraInicio
            fechaHoraFin: $fechaHoraFin
            tipo: $tipo
            premio: $premio
          ) {
            id
            nombre
          }
        }
        """
        variables = {
            "idTorneo": tournament_id,
            "nombre": fake.word(),
            "fechaHoraInicio": fake.date_time_this_year().isoformat(),
            "fechaHoraFin": fake.date_time_this_year().isoformat(),
            "tipo": random.randint(1, 3),
            "premio": fake.sentence(),
        }
        self._post(query, variables, name="modificarTorneo")

    @task
    def unregister_tournament(self):
        tournament_id = self._tournament_id()
        query = """
        mutation EliminarTorneo($idTorneo: Int!) {
          eliminarTorneo(idTorneo: $idTorneo)
        }
        """
        self._post(query, {"idTorneo": tournament_id}, name="eliminarTorneo")