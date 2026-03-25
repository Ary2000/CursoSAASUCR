# Contexto de torneo

El evento es el contexto responsable de gestionar los competidores, la ejecución del torneo, incluyendo, seeding y los sets. Asimismo, provee datos descriptivos como el juego, la fecha y hora de inicio y de fin del torneo, y el premio para los ganadores

## Lenguaje obliquo

Seeding: predicción de las posiciones que ocuparán los participantes en el torneo, la cual sirve de base para determinar los enfrentamientos entre competidores.
Set: Partida entre dos jugadores. Puede desarrollarse en formato de mejor de 3, mejor de 5, u otra modalidad definida por el organizador del torneo.

## Responsabilidades

- Gestionar los competidores inscritos en el torneo
- Gestionar el seeding del evento
- Gestionar los sets que se juegen en el torneo
- Proveer información descriptiva del torneo

## Modelo del dominio

Este entidad se encargará de salvar los datos descriptivos del torneo

```
Torneo {
    nombre,
    fechaHoraInicio,
    fechaHoraFin,
    tipo,
    premio
}
```

## Lo que este contexto NO sabe

- Cantidad de participantes de todos los torneos en el evento
- Características del competidor además de su ID y su nombre

## Eventos

### Eventos emitidos

| Evento                    | Descripción                                                    | Consumidores típicos |
| ------------------------- | -------------------------------------------------------------- | -------------------- |
| TorneoCreado              | Se creó un torneo asociado a un evento                         | Evento               |
| TorneoEliminado           | Se eliminó un torneo asocsiado a un evento                     | Evento               |
| CompetidorRegistrado      | Se registró a un usuario en un torneo                          | Identidad y Usuario  |
| CompetidorEliminado       | Se eliminó a un usuario dentro de un torneo                    | Identidad y Usuario  |
| ParticipantesActualizados | Recibir cuantas personas están registradas dentro de un evento | Evento               |

### Eventos consumidos

| Evento        | Descripción                               | Consumidores típicos |
| ------------- | ----------------------------------------- | -------------------- |
| ListadoJuegos | Listado de juegos presentes en el sistema | Catálogo de juegos   |
