-- Las publicaciones del perfil dejan de llamarse comments.
-- En una base nueva, supabase/schema.sql ya crea public.posts.

DO $$
BEGIN
    IF to_regclass('public.comments') IS NOT NULL THEN
        ALTER TABLE public.comments RENAME TO posts;
    END IF;

    IF to_regclass('public.posts') IS NULL THEN
        RETURN;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pg_class
        WHERE relname = 'comments_user_created_at_id_idx'
    ) THEN
        ALTER INDEX public.comments_user_created_at_id_idx
            RENAME TO posts_user_created_at_id_idx;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'comments_link_https'
    ) THEN
        ALTER TABLE public.posts
            RENAME CONSTRAINT comments_link_https TO posts_link_https;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pg_policy
        WHERE polname = 'comments_select_own'
          AND polrelid = 'public.posts'::regclass
    ) THEN
        ALTER POLICY comments_select_own ON public.posts
            RENAME TO posts_select_own;
    END IF;
END $$;
