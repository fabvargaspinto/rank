-- Nombres ya están en minúsculas (CHECK users_name_format). UNIQUE(name)
-- permite buscar con eq y usar el índice btree (antes: unique en lower(name)).

DROP INDEX IF EXISTS public.users_name_lower_unique;

CREATE UNIQUE INDEX users_name_unique
    ON public.users (name)
    WHERE name IS NOT NULL;
