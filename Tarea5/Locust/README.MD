# Comandos para probar los servicios

- locust -f torneo_locustfile.py -H http://127.0.0.1:8004

- locust -f juego_locustfile.py -H http://127.0.0.1:8004

- locust -f identity_locustfile.py -H http://127.0.0.1:8003

- locust -f evento_locustfile.py -H http://127.0.0.1:8000
