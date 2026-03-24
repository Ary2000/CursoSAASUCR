# Tarea 1: Página de torneos

## Tabla de contenidos

- [Contextos y documentación](#contextos-y-documentación)
- [Diagrama: interacción entre contextos](#diagrama-interacción-entre-contextos)
- [Flujo de eventos (secuencia)](#flujo-de-eventos-secuencia)

## Contextos y documentación

| Contexto             | Responsabilidad                                    | Documentación |
| -------------------- | -------------------------------------------------- | ------------- |
| Eventos              | Gestionar el evento que se hará                    | futuro        |
| Torneos              | Gestionar los torneos que se realicen en un evento | futuro        |
| Catálogo de juegos   | Catálogo de juegos que se le puede hacer un evento | futuro        |
| Identidad y Usuarios | Usuario interesado a ingresar a un evento          | Futuro        |

## Diagrama: Interacción entre contextos

- **Líneas sólidas**: Consultas realizadas por API
- **Líneas punteadas**: Eventos

```mermaid
flowchart LR
 subgraph s1["Torneos"]
        n1["Eventos: CrearEvento, EliminarEvento, RegistrarCompetidor, EliminarCompetidor, OrganizarSeeding, TipoBracket, ActualizarSet, Standings"]
  end
 subgraph s3["Eventos"]
        n3["Eventos: CargarTorneo, CrearTorneo, EliminarTorneo, ModificarTorneo, RegistrarParticipante, EliminarParticipante, Busqueda"]
  end
 subgraph s4["Identidad y Usuarios"]
        n4["CrearUsuario, ModificarUsuario, BorrarUsuario, VerUsuario, Autenticar"]
  end
 subgraph s5["Catálogo de juegos"]
        n5["JuegoAñadido, JuegoEliminado, ListasJuegos"]
  end
    n1 -- API --> s5
    n3 -. suscrito .-> s1
    s4 -- API --> n1 & n3
```

## Flujo de eventos (secuencia)

```mermaid
sequenceDiagram
    participant Evento
    participant Torneo
    participant IdentidadUsuarios as Identidad y Usuarios
    participant CatalogoJuegos as Catálogo de juegos
    participant BusEventos as Bus de Eventos

    Torneo->>BusEventos: CrearTorneo, ModificarTorneo
    BusEventos->>Evento: (Subscripción de torneos presentes en el torneo)
    Torneo->>CatalogoJuegos: ListadoJuegos
    IdentidadUsuarios->>Evento: API: RegistrarParticipante
    IdentidadUsuarios->>Evento: API: EliminarParticipante
    Evento->>BusEventos: ActualizarParticipantes
    BusEventos->>Evento: (Subscripción de cantidad de participantes)
    IdentidadUsuarios->>Torneo: API: RegistrarCompetidor
    IdentidadUsuarios->>Torneo: API: EliminarCompetidor
```

## Eventos por contexto

| Contexto                   | Emite                                            | Consume                                                                                  |
| -------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **Catálogo juegos**        | JuegoCreado                                      | JuegoEliminado                                                                           |
| **Evento**                 | EventoCreado, EventoModificado, EventoModificado | TorneoCreado, TorneoEliminado                                                            |
| **Torneo**                 | TorneoCreado, TorneoModificado, TorneoEliminado  | -                                                                                        |
| ** Identidad y Usuarios ** | -                                                | ParticipanteRegistrado, ParticipanteEliminado, CompetidorRegistrado, CompetidorEliminado |
