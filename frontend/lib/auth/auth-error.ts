export const AUTH_ERROR_MESSAGES = {
    oauth_failed: "No se pudo completar el acceso con Google",
    link_expired: "El enlace venció o no es válido",
    not_allowed: "No se pudo completar el registro con esta cuenta",
    session_expired: "Tu sesión expiró. Volvé a iniciar sesión",
    provision_failed: "No se pudo completar el acceso. Probá de nuevo",
} as const;

export type AuthErrorCode = keyof typeof AUTH_ERROR_MESSAGES;

export function isAuthErrorCode(value: string): value is AuthErrorCode {
    return value in AUTH_ERROR_MESSAGES;
}

/** Traduce `?error=` a texto propio; códigos desconocidos se ignoran. */
export function messageForAuthError(
    code: string | null | undefined,
): string {
    if (!code || !isAuthErrorCode(code)) {
        return "";
    }

    return AUTH_ERROR_MESSAGES[code];
}

export function authErrorQuery(code: AuthErrorCode): string {
    return `error=${code}`;
}
