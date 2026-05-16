# Tarea 3: Comunicación asíncrona con mensajería

Para esta tarea se creó una mensajería asincrónica utilizando RabbitMQ.

Se realiza una cola de mensajería llamada "torneos_queue" y el servicio de "Torneos" le enviará mensajes de creación y eliminación de torneos al servicio de "Eventos".

El usuario y contraseña del RabbitMQ es _guest_

## Ejemplo de mensajes asincrónicos

- Mensaje recibido de RabbitMQ: {'id': 5, 'nombre': 'string', 'eventoId': 0, 'message': 'Torneo creado'}
- Mensaje recibido de RabbitMQ: {'id': 2, 'nombre': 'Ryu from streets', 'eventoId': 2, 'message': 'Torneo eliminado'}

## URLs de los servicios

- URL del servicio de RabbitMQ: [http://localhost:15672/](http://localhost:15672/)
- URL del servicio de Torneos: [http://localhost:8004/docs](http://localhost:8004/docs)
