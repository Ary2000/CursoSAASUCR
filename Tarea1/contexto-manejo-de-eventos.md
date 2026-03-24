# Contexto de evento

El evento es el contexto responsable de gestionar la participación de personas interesadas en el evento y en la cantidad de torneos que este va a tener

## Responsabilidades

- Gestionar participación al mismo evento
- Gestionar torneos que estarán presentes durante el evento
- Mantener datos descriptivos del evento como el nombre, fecha y hora del inicio y del fun de este y costo de inscripción al evento

## Modelo del dominio

En este contexto, un evento será la actividad que se realizará durante un cierto periodo de tiempo. Puede ser de un día a varios.

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

| Evento                 | Descripción | Consumidores típicos |
| ---------------------- | ----------- | -------------------- |
| ParticipanteRegistrado | -           | Identidad y Usuarios |
| ParticipanteEliminado  | -           | Identidad y Usuarios |

### Eventos consumidos

| Evento                  | Descripción | Consumidores típicos |
| ----------------------- | ----------- | -------------------- |
| TorneoCreado            | -           | Torneo               |
| TorneoEliminado         | -           | Torneo               |
| ActualizarParticipantes | -           | Torneo               |
