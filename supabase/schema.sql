-- Schema completo de Sello Nómada.
-- Las migraciones en supabase/migrations/ quedan como historial.
-- Este archivo es la definición de una base nueva.

CREATE TABLE public.users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    display_name VARCHAR(50),
    avatar_url VARCHAR(2048),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_name_format CHECK (
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
    ),
    CONSTRAINT users_avatar_path CHECK (
        avatar_url IS NULL
        OR avatar_url ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.webp$'
        OR avatar_url ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/avatar\.(jpg|png|webp)$'
    )
);

CREATE UNIQUE INDEX users_name_lower_unique
    ON public.users (lower(name))
    WHERE name IS NOT NULL;

CREATE TABLE public.auth (
    id UUID PRIMARY KEY
        REFERENCES auth.users (id)
        ON DELETE CASCADE,
    user_id UUID NOT NULL UNIQUE
        REFERENCES public.users (id)
        ON DELETE CASCADE,
    email_encrypted TEXT NOT NULL,
    email_hmac TEXT UNIQUE NOT NULL,
    provider VARCHAR(32) NOT NULL
        CHECK (provider IN ('EMAIL', 'GOOGLE')),
    provider_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT auth_providers_shape CHECK (
        (
            provider = 'EMAIL'
            AND provider_id IS NULL
        )
        OR (
            provider <> 'EMAIL'
            AND provider_id IS NOT NULL
        )
    )
);

CREATE UNIQUE INDEX auth_provider_id_unique
    ON public.auth (provider, provider_id)
    WHERE provider_id IS NOT NULL;

CREATE TABLE public.user_links (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL
        REFERENCES public.users (id)
        ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    sort_index SMALLINT NOT NULL
        CHECK (sort_index >= 0 AND sort_index <= 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_links_user_sort_unique UNIQUE (user_id, sort_index),
    CONSTRAINT user_links_type_check CHECK (
        type IN (
            'youtube',
            'instagram',
            'spotify',
            'tiktok',
            'twitch',
            'kick',
            'facebook',
            'x',
            'default'
        )
    ),
    CONSTRAINT user_links_url_https CHECK (url ~ '^https://')
);

CREATE INDEX user_links_user_id_idx
    ON public.user_links (user_id);

CREATE INDEX user_links_user_id_sort_idx
    ON public.user_links (user_id, sort_index);

CREATE TABLE public.comments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL
        REFERENCES public.users (id)
        ON DELETE CASCADE,
    text VARCHAR(280) NOT NULL
        CHECK (char_length(text) >= 1 AND char_length(text) <= 280),
    link VARCHAR(2048),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT comments_link_https CHECK (
        link IS NULL OR link ~ '^https://'
    )
);

CREATE INDEX comments_user_created_at_id_idx
    ON public.comments (user_id, created_at DESC, id DESC);

CREATE OR REPLACE FUNCTION public.create_user_and_auth(
    p_user_id uuid,
    p_auth_id uuid,
    p_email_encrypted text,
    p_email_hmac text,
    p_provider text,
    p_provider_id text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.users (id)
    VALUES (p_user_id)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO public.auth (
        id,
        user_id,
        email_encrypted,
        email_hmac,
        provider,
        provider_id
    )
    VALUES (
        p_auth_id,
        p_user_id,
        p_email_encrypted,
        p_email_hmac,
        p_provider,
        p_provider_id
    )
    ON CONFLICT (id) DO NOTHING;

    DELETE FROM public.users AS leftover
    WHERE leftover.id = p_user_id
      AND NOT EXISTS (
          SELECT 1
          FROM public.auth
          WHERE user_id = leftover.id
      );
END;
$$;

REVOKE ALL ON FUNCTION public.create_user_and_auth(
    uuid, uuid, text, text, text, text
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.create_user_and_auth(
    uuid, uuid, text, text, text, text
) TO service_role;

CREATE OR REPLACE FUNCTION public.update_profile(
    p_user_id uuid,
    p_name text,
    p_display_name text,
    p_avatar_url text,
    p_description text,
    p_updated_at timestamptz,
    p_links jsonb
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    updated_count integer;
BEGIN
    UPDATE public.users
    SET
        name = p_name,
        display_name = p_display_name,
        avatar_url = p_avatar_url,
        description = p_description,
        updated_at = p_updated_at
    WHERE id = p_user_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;

    IF updated_count = 0 THEN
        RAISE EXCEPTION 'user_not_found'
            USING ERRCODE = 'P0002';
    END IF;

    DELETE FROM public.user_links
    WHERE user_id = p_user_id;

    INSERT INTO public.user_links (
        id,
        user_id,
        type,
        url,
        sort_index
    )
    SELECT
        (link->>'id')::uuid,
        p_user_id,
        link->>'type',
        link->>'url',
        (link->>'sort_index')::smallint
    FROM jsonb_array_elements(COALESCE(p_links, '[]'::jsonb)) AS link;
END;
$$;

REVOKE ALL ON FUNCTION public.update_profile(
    uuid, text, text, text, text, timestamptz, jsonb
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.update_profile(
    uuid, text, text, text, text, timestamptz, jsonb
) TO service_role;

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.users FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.auth FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.user_links FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.comments FROM PUBLIC, anon, authenticated;

GRANT ALL ON TABLE public.users TO service_role;
GRANT ALL ON TABLE public.auth TO service_role;
GRANT ALL ON TABLE public.user_links TO service_role;
GRANT ALL ON TABLE public.comments TO service_role;

GRANT SELECT ON TABLE public.users TO authenticated;
GRANT SELECT ON TABLE public.auth TO authenticated;
GRANT SELECT ON TABLE public.user_links TO authenticated;
GRANT SELECT ON TABLE public.comments TO authenticated;

CREATE POLICY users_select_own
ON public.users
FOR SELECT
TO authenticated
USING (
    id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);

CREATE POLICY auth_select_own
ON public.auth
FOR SELECT
TO authenticated
USING (id = auth.uid());

CREATE POLICY user_links_select_own
ON public.user_links
FOR SELECT
TO authenticated
USING (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);

CREATE POLICY comments_select_own
ON public.comments
FOR SELECT
TO authenticated
USING (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'avatars',
    'avatars',
    true,
    2097152,
    ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;
