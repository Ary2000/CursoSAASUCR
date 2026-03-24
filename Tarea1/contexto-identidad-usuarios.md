# Contexto de Identidad y Usuarios

Este contexto permite a los usuarios poder registrarse en cuantos eventos y torneos quiera.

# Responsabilidades

- Gestionar la participación de los usuarios a eventos y torneos
- Enviar notificaciones al usuario en caso de que el evento o torneo requiera informarle a este un dato importante

# Modelo del dominio

En este contexto, el usuario se utilizará para poder enviar solicitudes para asegurar el registro del usuario en eventos y en los torneos que desea participar en.

```
Usuario {
    nombre,
    contrasena,
    correo
}
```

# Lo que el contexto no sabe

- Datos del usuario dependientes de un evento o un torneo
