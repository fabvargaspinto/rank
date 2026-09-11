-- public schema
DROP TABLE IF EXISTS public.auth_providers;
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
    id UUID PRIMARY KEY REFERENCES auth.users (id) ON DELETE CASCADE,
    user_id UUID NOT NULL UNIQUE REFERENCES public.users (id) ON DELETE CASCADE,
    email_encrypted TEXT NOT NULL,
    email_hmac TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.auth_providers (
    id UUID PRIMARY KEY,
    auth_id UUID NOT NULL REFERENCES public.auth (id) ON DELETE CASCADE,
    provider VARCHAR(32) NOT NULL CHECK (provider IN ('EMAIL', 'GOOGLE')),
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
    ),
    UNIQUE (auth_id, provider)
);


