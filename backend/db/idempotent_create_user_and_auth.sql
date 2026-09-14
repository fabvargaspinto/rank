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
