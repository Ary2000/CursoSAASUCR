# Contexto de catálogo de juegos

Este contexto se encargará de gestionar los juegos para los cuales es posible organizar un torneos. El propósito de esto es para facilitar búsquedas que permitan encontrar eventos con torneos asociados a un juego específico.

## Responsabilidades

- Gestionar todos los juegos sobre los cuales es posible organizar torneos.
- Proveer información en caso de querer realizar una búsqueda filtrada.

## Modelo del dominio

En este contexto, el juego únicamente mantendrá el nombre del juego y un identificador (id) para poder recuperar datos asociados a este, como la cantidad de eventos que tienen un torneo corriendo de dicho juego

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

| Evento        | Descripción                                                          | Consumidores típicos |
| ------------- | -------------------------------------------------------------------- | -------------------- |
| ListadoJuegos | Lista de todos los juegos sobre los que se puede organizar un torneo | Torneo               |

### Eventos consumidos

El catálogo de juegos no pide información a otro contexto; únicamente la provee a aquellos contextos que la requieren, aportando los juegos registrados en el sistema.
