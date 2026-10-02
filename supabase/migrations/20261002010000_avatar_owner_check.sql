-- Tie avatar_url folder to the owning users.id and drop legacy avatar.* names.

ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_avatar_path;

ALTER TABLE public.users ADD CONSTRAINT users_avatar_path CHECK (
    avatar_url IS NULL
    OR avatar_url ~ (
        '^'
        || id::text
        || '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.webp$'
    )
);
