# Tarea 4: Pruebas de contracto con Pact

Para esta tarea se crearon dos contenedores, **consumer_tests** y **provider_tests**, que se encargaran de realizar pruebas tipo de contracto a las comunicaciones entre los servicios **CatalogoJuegos** y **Torneos**.

Los dos recursos que se consultaran serán **/games** que devuelve la lista de juegos presentes en el catálogo y **/games/{id}** que devuelve la información de un juego específico.

## Pruebas a realizar

Las pruebas tipo consumidor se encontrarán en la ruta **/Torneos/tests/pact/test_fastapi_pact.py** y las tipo proveedor en **CatalogoJuegos/tests/pact/test_fastapi_pact.py**.

- GET /games: Debe devolver 200 con el primer resultado siendo {"id": 1, "nombre": "Super Smash Bros"}
- GET /games/1: Debe devolver 200 con el resultado siendo {"id": 1, "nombre": "Super Smash Bros"}
- GET /games/999: Debe devolver 404

## Pasos para realizar pruebas

- Correr docker compose build
- Correr docker compose up o docker compose up --build consumer-tests provider-tests catalogojuegos
