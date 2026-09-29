# Glosario

Criterio de nombres para el backend, el frontend y la interfaz. Una palabra de esta lista no se usa para otra cosa.

| Concepto | Término | En el código |
|---|---|---|
| Página pública de la artista | Perfil | `User`. La ruta es `/profiles/{username}` |
| Identificador de la URL | Usuario | `UserName`. En la interfaz, "Usuario" |
| Nombre que se muestra | Nombre | `UserDisplayName`. En la interfaz, "Nombre" |
| Texto que publica la dueña del perfil | Publicación | `Post`. La ruta es `/me/posts` |
| Cuenta de Supabase | Identidad | `Auth`, `auth_id`. El caso de uso es `ProvisionIdentity` |

Una publicación pertenece a un perfil. La crea y la borra solo la dueña, y se muestra con su nombre y su foto. No es un comentario de otra persona: no hay autor distinto del perfil, ni moderación, ni reportes.

El perfil (`User`) y la identidad (`Auth`) conservan esos identificadores. `Auth` también nombra la tabla y el esquema de Supabase; renombrarlo a `Identity` mezclaría la cuenta de la aplicación con `auth.users`.
