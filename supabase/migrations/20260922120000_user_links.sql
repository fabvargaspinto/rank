-- user_links: profile social / web links (max 6 per user via sort_index 0..5)

CREATE TABLE public.user_links (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL
        REFERENCES public.users (id)
        ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL
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
        ),
    url VARCHAR(2048) NOT NULL,
    sort_index SMALLINT NOT NULL
        CHECK (sort_index >= 0 AND sort_index <= 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_links_user_sort_unique UNIQUE (user_id, sort_index)
);

CREATE INDEX IF NOT EXISTS user_links_user_id_idx
    ON public.user_links (user_id);

CREATE INDEX IF NOT EXISTS user_links_user_id_sort_idx
    ON public.user_links (user_id, sort_index);

ALTER TABLE public.user_links ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.user_links FROM PUBLIC, anon;

GRANT ALL ON TABLE public.user_links TO service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.user_links TO authenticated;

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

CREATE POLICY user_links_insert_own
ON public.user_links
FOR INSERT
TO authenticated
WITH CHECK (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);

CREATE POLICY user_links_update_own
ON public.user_links
FOR UPDATE
TO authenticated
USING (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
)
WITH CHECK (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);

CREATE POLICY user_links_delete_own
ON public.user_links
FOR DELETE
TO authenticated
USING (
    user_id IN (
        SELECT user_id
        FROM public.auth
        WHERE id = auth.uid()
    )
);
