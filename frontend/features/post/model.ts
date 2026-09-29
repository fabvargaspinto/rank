import { httpsUrlError, postTextError } from "@/lib/domain-limits";
import type { PostResponse } from "@/lib/api/types";
import type { Profile } from "@/features/profile/model";

export type PostView = {
    id: string;
    avatar: string;
    user: string;
    date: string;
    text: string;
    link?: string;
};

export function normalizeLink(value: string): string | undefined {
    const trimmed = value.trim();

    if (!trimmed) {
        return undefined;
    }

    try {
        return new URL(trimmed).toString();
    } catch {
        try {
            return new URL(`https://${trimmed}`).toString();
        } catch {
            return trimmed;
        }
    }
}

/** Devuelve el enlace https normalizado o `null` si está vacío. */
export function httpsLink(value: string | undefined | null): string | null {
    const trimmed = value?.trim() ?? "";

    if (!trimmed) {
        return null;
    }

    const normalized = normalizeLink(trimmed) ?? trimmed;
    return httpsUrlError(normalized) ? null : normalized;
}

export function formatPostDate(value: string): string {
    const date = value.includes("T")
        ? new Date(value)
        : new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(date);
}

export function hostnameFromUrl(url: string): string {
    try {
        return new URL(url).hostname.replace(/^www\./, "");
    } catch {
        return url;
    }
}

export function postViewFromResponse(
    created: PostResponse,
    profile: Profile,
): PostView {
    return {
        id: created.id,
        avatar: profile.photo,
        user: profile.displayName || profile.name,
        date: created.created_at,
        text: created.text,
        ...(created.link ? { link: created.link } : {}),
    };
}

export type CreatePostDraft = {
    text: string;
    link?: string | null;
};

export function parseCreatePostInput(
    input: CreatePostDraft,
):
    | { ok: true; payload: { text: string; link: string | null } }
    | { ok: false; message: string } {
    const textError = postTextError(input.text);

    if (textError) {
        return { ok: false, message: textError };
    }

    const rawLink = input.link?.trim() ?? "";

    if (!rawLink) {
        return {
            ok: true,
            payload: {
                text: input.text.trim(),
                link: null,
            },
        };
    }

    const normalized = normalizeLink(rawLink) ?? rawLink;
    const linkError = httpsUrlError(normalized);

    if (linkError) {
        return { ok: false, message: linkError };
    }

    return {
        ok: true,
        payload: {
            text: input.text.trim(),
            link: httpsLink(normalized),
        },
    };
}
