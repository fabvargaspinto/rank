-- public schema for local Supabase

CREATE TABLE public.users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    avatar_url VARCHAR(2048),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


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


CREATE UNIQUE INDEX IF NOT EXISTS auth_provider_id_unique
    ON public.auth (provider, provider_id)
    WHERE provider_id IS NOT NULL;


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
    uuid,
    uuid,
    text,
    text,
    text,
    text
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.create_user_and_auth(
    uuid,
    uuid,
    text,
    text,
    text,
    text
) TO service_role;


ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.users FROM PUBLIC, anon;
REVOKE ALL ON TABLE public.auth FROM PUBLIC, anon;

GRANT ALL ON TABLE public.users TO service_role;
GRANT ALL ON TABLE public.auth TO service_role;

GRANT SELECT, UPDATE ON TABLE public.users TO authenticated;
GRANT SELECT, UPDATE ON TABLE public.auth TO authenticated;

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

CREATE POLICY users_update_own
ON public.users
FOR UPDATE
TO authenticated
USING (
    id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
)
WITH CHECK (
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

CREATE POLICY auth_update_own
ON public.auth
FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (id = auth.uid());
