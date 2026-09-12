-- public schema

DROP TABLE IF EXISTS public.auth;
DROP TABLE IF EXISTS public.users;


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

    email_hmac TEXT UNIQUE,

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


DROP FUNCTION IF EXISTS public.create_user_and_auth(
    uuid,
    uuid,
    text,
    text,
    text,
    text
);


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
    VALUES (p_user_id);

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
    );
END;
$$;


GRANT EXECUTE ON FUNCTION public.create_user_and_auth(
    uuid,
    uuid,
    text,
    text,
    text,
    text
) TO service_role;
