-- One transaction for the profile row and its links.
-- A failed link insert rolls back the profile update.

ALTER TABLE public.user_links
    DROP CONSTRAINT IF EXISTS user_links_type_check;

ALTER TABLE public.user_links
    ADD CONSTRAINT user_links_type_check
    CHECK (
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
    );


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
    uuid,
    text,
    text,
    text,
    text,
    timestamptz,
    jsonb
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.update_profile(
    uuid,
    text,
    text,
    text,
    text,
    timestamptz,
    jsonb
) TO service_role;
