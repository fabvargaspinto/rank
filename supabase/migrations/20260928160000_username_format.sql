-- Same rule as UserName in backend/core/user/domain/user_name.py.
-- Values that cannot be a public URL are cleared so the constraint can
-- be added; those profiles choose a new username.

UPDATE public.users
SET name = lower(btrim(name))
WHERE name IS NOT NULL
  AND name <> lower(btrim(name));

UPDATE public.users
SET name = NULL
WHERE name IS NOT NULL
  AND (
      name !~ '^[a-z0-9][a-z0-9._-]{1,28}[a-z0-9]$'
      OR name IN (
          'admin',
          'api',
          'auth',
          'dashboard',
          'first',
          'login',
          'register',
          'settings',
          'robots.txt',
          'sitemap.xml',
          'favicon.ico'
      )
  );

WITH ranked AS (
    SELECT
        id,
        row_number() OVER (
            PARTITION BY lower(name)
            ORDER BY updated_at ASC, id ASC
        ) AS rn
    FROM public.users
    WHERE name IS NOT NULL
)
UPDATE public.users AS users
SET name = NULL
FROM ranked
WHERE users.id = ranked.id
  AND ranked.rn > 1;

DROP INDEX IF EXISTS public.users_name_unique;

CREATE UNIQUE INDEX IF NOT EXISTS users_name_lower_unique
    ON public.users (lower(name))
    WHERE name IS NOT NULL;

ALTER TABLE public.users
    DROP CONSTRAINT IF EXISTS users_name_format;

ALTER TABLE public.users
    ADD CONSTRAINT users_name_format
    CHECK (
        name IS NULL
        OR (
            name ~ '^[a-z0-9][a-z0-9._-]{1,28}[a-z0-9]$'
            AND name NOT IN (
                'admin',
                'api',
                'auth',
                'dashboard',
                'first',
                'login',
                'register',
                'settings',
                'robots.txt',
                'sitemap.xml',
                'favicon.ico'
            )
        )
    );
