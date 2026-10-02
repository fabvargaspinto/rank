-- Reserve usernames that collide with app routes or planned legal pages.

ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_name_format;

ALTER TABLE public.users ADD CONSTRAINT users_name_format CHECK (
    name IS NULL
    OR (
        name ~ '^[a-z0-9][a-z0-9._-]{1,28}[a-z0-9]$'
        AND name NOT IN (
            'admin',
            'api',
            'assets',
            'auth',
            'ayuda',
            'contacto',
            'dashboard',
            'favicon.ico',
            'first',
            'forgot-password',
            'icon',
            'instagram',
            'legal',
            'login',
            'opengraph-image',
            'privacy',
            'privacidad',
            'register',
            'reset-password',
            'robots.txt',
            'settings',
            'sitemap.xml',
            'soporte',
            'static',
            'terms',
            'terminos',
            'www'
        )
    )
);
