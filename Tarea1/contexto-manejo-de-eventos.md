# Contexto de evento

El evento es el contexto responsable de gestionar la participación de personas interesadas en el evento y en la cantidad de torneos que este va a tener

## Responsabilidades

- Gestionar participación del evento
- Gestionar torneos que estarán presentes durante el evento
- Mantener los datos descriptivos del evento, tales como su nombre, fecha y hora de inicio y fin, y el costo de inscripción.

## Modelo del dominio

En este contexto, un evento será la actividad que se realizará durante un cierto periodo de tiempo. Puede ser de un día a varios.

Se tendrán datos descriptivos para poder identificarlo y ayudar en búsquedas filtradas.

```
Evento {
    id,
    nombre,
    descripcion,
    icono,
    fechaInicio,
    fechaFin,
    horaInicio,
    horaFin,
    ubicacion,
    costoInscripcion
}
```

## Lo que este contexto NO sabe

- Como se va a correr el o los torneos asociados a este
- Quienes y cuantas personas se registraron a un torneo
- Cuales son los juegos que soporta la página

## Eventos

### Eventos emitidos

| Evento                 | Descripción                          | Consumidores típicos |
| ---------------------- | ------------------------------------ | -------------------- |
| ParticipanteRegistrado | Registra un participante a un evento | Identidad y Usuarios |
| ParticipanteEliminado  | Elimina un participante de un evento | Identidad y Usuarios |

### Eventos consumidos

| Evento                  | Descripción                                                    | Consumidores típicos |
| ----------------------- | -------------------------------------------------------------- | -------------------- |
| TorneoCreado            | Crea un torneo dentro de un evento                             | Torneo               |
| TorneoEliminado         | Elimina un torneo dentro de un evento                          | Torneo               |
| ActualizarParticipantes | Recibir cuantas personas están registradas dentro de un evento | Torneo               |
