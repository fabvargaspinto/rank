-- When public.auth is removed (e.g. auth.users deleted from the dashboard),
-- delete the matching public.users row so the profile is not left orphaned.
-- user_links and posts cascade from users.

CREATE OR REPLACE FUNCTION public.delete_profile_after_identity()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    DELETE FROM public.users WHERE id = OLD.user_id;
    RETURN OLD;
END;
$$;

DROP TRIGGER IF EXISTS auth_delete_profile ON public.auth;

CREATE TRIGGER auth_delete_profile
AFTER DELETE ON public.auth
FOR EACH ROW
EXECUTE FUNCTION public.delete_profile_after_identity();

REVOKE SELECT ON TABLE public.users FROM authenticated;
REVOKE SELECT ON TABLE public.auth FROM authenticated;
REVOKE SELECT ON TABLE public.user_links FROM authenticated;
REVOKE SELECT ON TABLE public.posts FROM authenticated;

DROP POLICY IF EXISTS users_select_own ON public.users;
DROP POLICY IF EXISTS auth_select_own ON public.auth;
DROP POLICY IF EXISTS user_links_select_own ON public.user_links;
DROP POLICY IF EXISTS posts_select_own ON public.posts;
