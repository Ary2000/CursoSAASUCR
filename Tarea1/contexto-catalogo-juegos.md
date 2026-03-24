# Contexto de catálogo de juegos

Este contexto se encargará de gestionar lo que serán los juegos que se pueden realizar torneos para. Esto es para poder realizar búsquedas donde se puedan encontrar eventos con especificamente torneos de un juego específico

## Responsabilidades

- Gestionar todos los juegos que se le pueden realizar torneos
- Proveer información en caso de querer realizar una búsqueda filtrada

## Modelo del dominio

En este contexto, el juego solo tendrá el nombre del juego, un id para poder encontrar datos asociados a este, como cantidad de eventos que tienen un torneo corriendo de este juego

```
Juego {
    id,
    nombre
}
```

## Lo que este contexto NO sabe

- Eventos que corren un torneo de este juego
- Torneos de este juego

## Eventos

### Eventos emitidos

| Evento        | Descripción | Consumidores típicos |
| ------------- | ----------- | -------------------- |
| ListadoJuegos | -           | Torneo               |

### Eventos consumidos

El catálogo de juegos no pide ninguna información a ningún contexto, esta solo provee a los contextos que necesiten, los juegos que se encuentrar registrados en el sistema
