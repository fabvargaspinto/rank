import { httpsUrlError, MAX_LINKS } from "@/lib/domain-limits";
import type {
    UpdateProfileRequest,
    UserLinkResponse,
    UserResponse,
} from "@/lib/api/types";

export type ProfileLink = {
    id: string;
    url: string;
    type?: string;
};

export type Profile = {
    name: string;
    displayName: string;
    description: string;
    photo: string;
    links: ProfileLink[];
};

export function isObjectUrl(value: string): boolean {
    return value.startsWith("blob:") || value.startsWith("data:");
}

export function createEmptyLink(id = crypto.randomUUID()): ProfileLink {
    return { id, url: "" };
}

export function linksForEditor(links: ProfileLink[]): ProfileLink[] {
    if (links.length === 0) {
        return [createEmptyLink("link-0")];
    }

    return links.slice(0, MAX_LINKS).map((link, index) => ({
        id: link.id || `link-${index}`,
        url: link.url,
        type: link.type,
    }));
}

export function trimProfileText(value: string): string {
    return value.trim();
}

/** Usuario (URL): recorta espacios; el backend persiste en minúsculas. */
export function sanitizeUsername(value: string): string {
    return trimProfileText(value);
}

/** Nombre visible en el perfil. */
export function sanitizeName(value: string): string {
    return trimProfileText(value);
}

export type ProfileLinkPayload = { url: string };

export function profileLinkFromResponse(link: UserLinkResponse): ProfileLink {
    return {
        id: link.id,
        url: link.url,
        type: link.type,
    };
}

export function profileLinksFromResponse(
    links: UserLinkResponse[] | null | undefined,
): ProfileLink[] {
    return (links ?? []).map(profileLinkFromResponse);
}

export function profileFromUserResponse(
    user: UserResponse,
    options: { usernameFallback?: string } = {},
): Profile {
    const username =
        sanitizeUsername(user.name ?? "") ||
        options.usernameFallback ||
        "Sin nombre";

    return {
        name: username,
        displayName: sanitizeName(user.display_name ?? ""),
        description: user.description ?? "",
        photo: user.avatar ?? "",
        links: profileLinksFromResponse(user.links),
    };
}

export function linksPayload(links: ProfileLink[]): ProfileLinkPayload[] {
    return links
        .map((link) => ({ url: sanitizeName(link.url) }))
        .filter((link) => link.url.length > 0)
        .slice(0, MAX_LINKS);
}

export function firstLinkValidationError(
    links: ProfileLink[],
): string | null {
    const error = linksPayload(links)
        .map((link) => httpsUrlError(link.url))
        .find((message) => message != null);

    return error ?? null;
}

export function httpsAvatarUrl(value: string | null | undefined): string | null {
    const avatar = sanitizeName(value ?? "");
    return avatar.startsWith("https://") ? avatar : null;
}

export function hasProfilePhoto(photo: string): boolean {
    return sanitizeName(photo).length > 0;
}

export function isExternalProfilePhoto(photo: string): boolean {
    return isObjectUrl(photo) || /^https?:\/\//.test(photo);
}

export type UpdateProfileDraft = {
    name: string;
    displayName?: string | null;
    avatar?: string | null;
    description?: string | null;
    links?: ProfileLinkPayload[];
};

export type UpdateProfileFieldError = {
    message: string;
    status: number;
    field?: string;
};

export function parseUpdateProfileInput(
    input: UpdateProfileDraft,
):
    | { ok: true; body: UpdateProfileRequest }
    | { ok: false; error: UpdateProfileFieldError } {
    const name = sanitizeUsername(input.name);

    if (!name) {
        return {
            ok: false,
            error: {
                message: "El usuario es obligatorio",
                status: 400,
                field: "name",
            },
        };
    }

    const links =
        input.links === undefined
            ? undefined
            : input.links
                  .map((link) => ({ url: sanitizeName(link.url) }))
                  .filter((link) => link.url.length > 0);

    if (links !== undefined && links.length > MAX_LINKS) {
        return {
            ok: false,
            error: {
                message: `No se pueden agregar más de ${MAX_LINKS} links`,
                status: 400,
            },
        };
    }

    const linkError = links
        ?.map((link) => httpsUrlError(link.url))
        .find((error) => error != null);

    if (linkError) {
        return {
            ok: false,
            error: {
                message: linkError,
                status: 400,
            },
        };
    }

    return {
        ok: true,
        body: {
            name,
            ...(input.displayName !== undefined
                ? {
                      display_name: sanitizeName(input.displayName ?? "") || null,
                  }
                : {}),
            description: sanitizeName(input.description ?? "") || null,
            ...(input.avatar !== undefined
                ? { avatar: httpsAvatarUrl(input.avatar) }
                : {}),
            ...(links !== undefined ? { links } : {}),
        },
    };
}
