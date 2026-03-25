# Contexto de Identidad y Usuarios

Este contexto permite a los usuarios poder registrarse en los eventos y torneos que deseen.

## Responsabilidades

- Gestionar las solicitudes de participación de los usuarios en eventos y torneos
- Enviar notificaciones al usuario en caso de que el evento o torneo requiera informarle a este un dato importante

## Modelo del dominio

En este contexto, el modelo "usuario" solo tendrá el nombre, la contraseña y el correo del usuario. Esto es para poder tener un dato para poder identificarlo, uno para poder acceder a la cuenta y otro para poder comunicarse con este

```
Usuario {
    nombre,
    contrasena,
    correo
}
```

## Lo que el contexto no sabe

- Datos del usuario dependientes de un evento o un torneo

## Eventos

### Eventos emitidos

Este contexto no es un producto, solo consume funcionalidades de otros contextos.

### Eventos consumidos

| Evento                 | Descripción                           | Consumidores típicos |
| ---------------------- | ------------------------------------- | -------------------- |
| ParticipanteRegistrado | El usuario se registro a un evento    | Evento               |
| ParticipanteEliminado  | El usuario se eliminó de un evento    | Evento               |
| CompetidorRegistrado   | El usuario se registro a un torneo    | Torneo               |
| CompetidorEliminado    | El usuario se se eliminó de un torneo | Torneo               |
