export const MAX_LINKS = 6;

export const MAX_AVATAR_BYTES = 2 * 1024 * 1024;

export const AVATAR_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
] as const;

export const AVATAR_ACCEPT = AVATAR_MIME_TYPES.join(",");

export const AVATAR_TYPE_MESSAGE = "La imagen debe ser JPEG, PNG o WebP";

export const AVATAR_TOO_LARGE_MESSAGE = "La imagen no puede superar 2 MB";

export const POST_TEXT_MAX_LENGTH = 280;

export const DESCRIPTION_MAX_LENGTH = 250;

export const DISPLAY_NAME_MAX_LENGTH = 50;

export const USERNAME_MAX_LENGTH = 30;

export const USERNAME_PATTERN = /^[a-z0-9][a-z0-9._-]{1,28}[a-z0-9]$/;

export const USERNAME_MESSAGE =
    "Usá entre 3 y 30 letras minúsculas, números, puntos, guiones o guiones bajos";

export const LINK_MAX_LENGTH = 2048;

export const PASSWORD_MIN_LENGTH = 8;

export const PASSWORD_MAX_LENGTH = 72;

const USERNAME_REQUIRED_MESSAGE = "El usuario es obligatorio";

const HTTPS_URL_MESSAGE = "La URL debe ser una URL válida";

export function isAvatarMimeType(type: string): boolean {
    return (AVATAR_MIME_TYPES as readonly string[]).includes(type);
}

export function usernameShapeError(value: string): string | null {
    const normalized = value.trim().toLowerCase();

    if (!normalized) {
        return USERNAME_REQUIRED_MESSAGE;
    }

    if (!USERNAME_PATTERN.test(normalized)) {
        return USERNAME_MESSAGE;
    }

    return null;
}

export function isHttpsUrl(value: string): boolean {
    if (/\s/.test(value)) {
        return false;
    }

    try {
        const url = new URL(value);
        return url.protocol === "https:" && url.hostname.length > 0;
    } catch {
        return false;
    }
}

export function httpsUrlError(value: string): string | null {
    const trimmed = value.trim();

    if (!trimmed) {
        return null;
    }

    if (trimmed.length > LINK_MAX_LENGTH) {
        return `La URL debe tener menos de ${LINK_MAX_LENGTH} caracteres`;
    }

    if (!isHttpsUrl(trimmed)) {
        return HTTPS_URL_MESSAGE;
    }

    return null;
}

export function postTextError(value: string): string | null {
    const text = value.trim();

    if (!text) {
        return "La publicación es obligatoria";
    }

    if (text.length > POST_TEXT_MAX_LENGTH) {
        return `La publicación debe tener entre 1 y ${POST_TEXT_MAX_LENGTH} caracteres`;
    }

    return null;
}
