-- Drop SoundCloud, Bandcamp and Apple Music. Existing rows become a generic link.

UPDATE public.user_links
SET type = 'default'
WHERE type IN ('soundcloud', 'bandcamp', 'apple_music');

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
