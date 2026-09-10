-- public schema
DROP TABLE IF EXISTS public.auth;
DROP TABLE IF EXISTS public.users;
DROP FUNCTION IF EXISTS public.register_auth CASCADE;

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
    user_id UUID NOT NULL REFERENCES public.users (id) ON DELETE CASCADE,
    email_encrypted TEXT NOT NULL,
    email_hmac TEXT NOT NULL UNIQUE,
    provider VARCHAR(32) NOT NULL CHECK (provider IN ('EMAIL', 'OAUTH')),
    oauth_provider VARCHAR(32) CHECK (oauth_provider IS NULL OR oauth_provider IN ('GOOGLE')),
    provider_id VARCHAR(255),
    identity_key TEXT GENERATED ALWAYS AS (
        CASE
            WHEN provider = 'EMAIL' THEN 'EMAIL'
            ELSE oauth_provider
        END
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT auth_provider_shape CHECK (
        (
            provider = 'EMAIL'
            AND oauth_provider IS NULL
            AND provider_id IS NULL
        )
        OR (
            provider = 'OAUTH'
            AND oauth_provider IS NOT NULL
            AND provider_id IS NOT NULL
        )
    ),
    UNIQUE (user_id, identity_key)
);

-- Inserts auth.users + public.users + public.auth in a single transaction.
-- Call with the service role from the backend. Not for anon/authenticated.
CREATE OR REPLACE FUNCTION public.register_auth(
    p_user_id UUID,
    p_auth_id UUID,
    p_name TEXT,
    p_avatar_url TEXT,
    p_description TEXT,
    p_email TEXT,
    p_email_encrypted TEXT,
    p_email_hmac TEXT,
    p_provider TEXT,
    p_password TEXT DEFAULT NULL,
    p_oauth_provider TEXT DEFAULT NULL,
    p_provider_id TEXT DEFAULT NULL
)
RETURNS TABLE (user_id UUID, auth_id UUID)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_provider TEXT := upper(p_provider);
    v_oauth_provider TEXT := NULLIF(upper(COALESCE(p_oauth_provider, '')), '');
    v_gotrue_provider TEXT;
    v_encrypted_password TEXT;
    v_identity_provider_id TEXT;
BEGIN
    IF v_provider NOT IN ('EMAIL', 'OAUTH') THEN
        RAISE EXCEPTION 'provider must be EMAIL or OAUTH'
            USING ERRCODE = '22023';
    END IF;

    IF v_provider = 'EMAIL' THEN
        IF p_password IS NULL OR p_password = '' THEN
            RAISE EXCEPTION 'password is required for EMAIL provider'
                USING ERRCODE = '22023';
        END IF;
        IF v_oauth_provider IS NOT NULL OR (p_provider_id IS NOT NULL AND p_provider_id <> '') THEN
            RAISE EXCEPTION 'oauth_provider and provider_id must be empty for EMAIL provider'
                USING ERRCODE = '22023';
        END IF;

        v_gotrue_provider := 'email';
        v_encrypted_password := extensions.crypt(p_password, extensions.gen_salt('bf'));
        v_identity_provider_id := p_auth_id::TEXT;
        v_oauth_provider := NULL;
    ELSE
        IF v_oauth_provider IS NULL OR v_oauth_provider NOT IN ('GOOGLE') THEN
            RAISE EXCEPTION 'oauth_provider is required for OAUTH and must be GOOGLE'
                USING ERRCODE = '22023';
        END IF;
        IF p_provider_id IS NULL OR p_provider_id = '' THEN
            RAISE EXCEPTION 'provider_id is required for OAUTH provider'
                USING ERRCODE = '22023';
        END IF;

        v_gotrue_provider := lower(v_oauth_provider);
        v_encrypted_password := NULL;
        v_identity_provider_id := p_provider_id;
    END IF;

    INSERT INTO auth.users (
        instance_id,
        id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        raw_app_meta_data,
        raw_user_meta_data,
        created_at,
        updated_at,
        confirmation_token,
        recovery_token,
        email_change_token_new,
        email_change
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        p_auth_id,
        'authenticated',
        'authenticated',
        p_email,
        v_encrypted_password,
        NOW(),
        jsonb_build_object(
            'provider', v_gotrue_provider,
            'providers', jsonb_build_array(v_gotrue_provider)
        ),
        '{}'::JSONB,
        NOW(),
        NOW(),
        '',
        '',
        '',
        ''
    );

    INSERT INTO auth.identities (
        id,
        user_id,
        identity_data,
        provider,
        provider_id,
        last_sign_in_at,
        created_at,
        updated_at
    ) VALUES (
        gen_random_uuid(),
        p_auth_id,
        jsonb_build_object(
            'sub', v_identity_provider_id,
            'email', p_email,
            'email_verified', TRUE
        ),
        v_gotrue_provider,
        v_identity_provider_id,
        NOW(),
        NOW(),
        NOW()
    );

    INSERT INTO public.users (
        id,
        name,
        avatar_url,
        description
    ) VALUES (
        p_user_id,
        p_name,
        p_avatar_url,
        p_description
    );

    INSERT INTO public.auth (
        id,
        user_id,
        email_encrypted,
        email_hmac,
        provider,
        oauth_provider,
        provider_id
    ) VALUES (
        p_auth_id,
        p_user_id,
        p_email_encrypted,
        p_email_hmac,
        v_provider,
        v_oauth_provider,
        NULLIF(p_provider_id, '')
    );

    RETURN QUERY SELECT p_user_id, p_auth_id;
END;
$$;

REVOKE ALL ON FUNCTION public.register_auth FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.register_auth TO service_role;
