# Contexto de torneo

El evento es el contexto responsable de gestionar los competidores, la ejecución del torneo como el seeding y los sets y proveer datos descriptivos el juego que se jugará, la hora y fecha que comenzará y terminará el torneo y el premio para los ganadores

## Lenguaje obliquo

Seeding: Predicción de los lugares que tendran los participantes en el torneo. Este ayudará la toma de decisión de quien va a jugar en contra de quien
Set: Partida entre dos jugadores. Este puede ser mejor de 3, mejor de 5 u otra cantidad definida por el organizador del torneo.

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
