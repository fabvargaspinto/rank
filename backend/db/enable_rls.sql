ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth ENABLE ROW LEVEL SECURITY;

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

REVOKE ALL ON TABLE public.users FROM PUBLIC, anon;
REVOKE ALL ON TABLE public.auth FROM PUBLIC, anon;

GRANT ALL ON TABLE public.users TO service_role;
GRANT ALL ON TABLE public.auth TO service_role;

GRANT SELECT, UPDATE ON TABLE public.users TO authenticated;
GRANT SELECT, UPDATE ON TABLE public.auth TO authenticated;

DROP POLICY IF EXISTS users_select_own ON public.users;
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

DROP POLICY IF EXISTS users_update_own ON public.users;
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

DROP POLICY IF EXISTS auth_select_own ON public.auth;
CREATE POLICY auth_select_own
ON public.auth
FOR SELECT
TO authenticated
USING (id = auth.uid());

DROP POLICY IF EXISTS auth_update_own ON public.auth;
CREATE POLICY auth_update_own
ON public.auth
FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (id = auth.uid());
