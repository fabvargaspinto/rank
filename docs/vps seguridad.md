Revisión para el VPS: seguridad y operación
Sello Nómada · commit 91ef358f · 2 de octubre de 2026 · “Verificado” significa que lo reproduje o lo confirmé en tu máquina. No modifiqué ningún archivo del repo.

Lo primero, antes del primer deploy
Subir Next a 16.3.6 y nginx a 1.30, limitar los píxeles de los avatares y la memoria de los contenedores, cookies de sesión con httpOnly y secure, y que el backend no arranque con secretos vacíos. Son cambios chicos y los diffs están al final. Lo que lleva más tiempo es el CAPTCHA en Auth y verificar el dominio en Resend.
8
Críticas o altas
0/24
Marcados como resueltos
Antes del primer deploy
Riesgos explotables desde internet o que rompen el registro en producción.


Next.js 16.3.4 tiene un RCE conocido en next/og
Crítica · Dependencias


La imagen de nginx no recibe parches desde abril de 2025
Alta · Docker


Un PNG de 435 KB lleva el backend a 1,1 GB de RAM
Alta · Backend


Las cookies de sesión son legibles desde JavaScript y viajan por HTTP
Alta · Auth


Con INSTAGRAM_APP_SECRET vacío, cualquiera puede borrar conexiones ajenas
Alta · Backend


Un script puede agotar el cupo de emails y frenar todos los registros
Alta · SMTP


Sin dominio verificado en Resend, el registro no funciona en producción
Alta · SMTP

Antes de tener usuarios reales
Pérdida de datos, avisos que no llegan y procesos manuales que van a fallar con el tiempo.


El script de purga puede borrar todas las conexiones de producción
Alta · Datos


Los escáneres de correo queman los links de confirmación
Media · SMTP


El CI no audita dependencias
Media · CI/CD


El deploy no verifica ni vuelve atrás, y el disco se va a llenar
Media · CI/CD


Nada asegura que las migraciones lleguen antes que el código
Media · Datos


Nadie se entera si falla la renovación del certificado
Media · Cron


El job de snapshots no avisa si deja de correr
Media · Cron


Las tablas nuevas nacen expuestas a la Data API
Media · Datos


Todavía no hay backups
Media · Datos


El .env de la laptop tiene una llave de toda tu cuenta de Supabase
Media · Secretos

Mejoras de operación
Endurecimiento y prolijidad; ninguno es urgente.


Contenedores sin endurecer
Baja · Docker


Las imágenes solo se reconstruyen cuando hay commits
Baja · CI/CD


Workflow con permisos amplios y versiones sin fijar
Baja · CI/CD


El optimizador de imágenes acepta cualquier proyecto de Supabase
Baja · Frontend


La misma secret key de Supabase en frontend y backend
Baja · Secretos


El token de Turso necesita permisos de esquema
Baja · Datos


Si ponés Cloudflare adelante, se rompen los rate limits
Baja · Docker

Cambios propuestos
Un archivo por tarjeta, como punto de partida para los arreglos de arriba. Ninguno está aplicado.


docker-compose.prod.yml
+12
-1

backend/core/user/application/avatar_image.py
+5
-1

frontend/lib/supabase/env.ts
+6

frontend/lib/supabase/server.ts
+2
-1

frontend/lib/supabase/auth-client.ts
+3
-1

backend/config/instagram_settings.py
+3
-1

backend/config/crypto_settings.py
+5
-2

deploy/nginx/nginx.conf
+3
-1

deploy/nginx/templates/default.conf.template
+1

.github/workflows/ci.yml
+26
-2

backend/pyproject.toml
+4
-2

deploy/deploy.sh (nuevo)
+26

crontab del usuario de despliegue (nuevo)
+2

supabase/migrations/20261003000000_default_privileges.sql (nuevo)
+7
Lo que ya está bien
Solo nginx publica puertos; del backend llegan a internet únicamente los tres callbacks de Meta.

Backend y frontend corren con usuario sin privilegios, y los logs rotan (10 MB × 5 por servicio).

RLS con `REVOKE ALL` en las cuatro tablas; las funciones `SECURITY DEFINER` fijan `search_path` y solo las ejecuta `service_role`.

El JWT se valida contra el JWKS solo con ES256/RS256, exigiendo `aud`, `iss` y `exp`.

Emails y tokens de Instagram cifrados con AES-GCM y AAD por fila; el `state` de OAuth va firmado con una clave derivada.

Los tests de integración solo corren contra Supabase local o el proyecto de desarrollo.

`/docs` y `/openapi.json` cerrados en producción, y límite de body en nginx, Next y el backend.

Los callbacks de auth no tienen open redirect: `next` solo acepta `/reset-password`.



/Users/fab/.cursor/projects/Users-fab-ig/canvases/revision-vps-seguridad.canvas.tsx