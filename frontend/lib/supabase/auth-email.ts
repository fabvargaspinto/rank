import type { AuthError } from "@supabase/supabase-js";
import type { FetchDataResponse } from "@/lib/api/types";

/** Cupo de emails de Auth agotado (SMTP / rate_limit_email_sent). */
export const BETA_EMAIL_LIMIT_MESSAGE =
    "Estamos en beta y ya llegamos al límite de emails por hoy. Probá de nuevo mañana.";

export const LOGIN_RATE_LIMIT_MESSAGE =
    "Demasiados intentos, probá en unos minutos";

export const EMAIL_NOT_CONFIRMED_MESSAGE = "Confirmá tu email para entrar.";

export function isEmailSendRateLimited(
    error: Pick<AuthError, "code" | "status" | "message">,
): boolean {
    if (error.code === "over_email_send_rate_limit") {
        return true;
    }

    const message = error.message?.toLowerCase() ?? "";
    if (
        error.status === 429 &&
        (message.includes("email") || message.includes("mail"))
    ) {
        return true;
    }

    return (
        message.includes("email") &&
        (message.includes("rate limit") || message.includes("rate_limit"))
    );
}

/** Respuesta lista si el fallo es por cupo de emails; si no, null. */
export function emailRateLimitResponse(
    error: Pick<AuthError, "code" | "status" | "message">,
): FetchDataResponse | null {
    if (!isEmailSendRateLimited(error)) {
        return null;
    }

    return {
        data: null,
        isError: true,
        message: BETA_EMAIL_LIMIT_MESSAGE,
        status: 429,
        code: "over_email_send_rate_limit",
    };
}

export function loginAuthErrorResponse(
    error: Pick<AuthError, "code" | "status" | "message">,
): FetchDataResponse {
    if (error.code === "email_not_confirmed") {
        return {
            data: null,
            isError: true,
            message: EMAIL_NOT_CONFIRMED_MESSAGE,
            status: 401,
            code: "email_not_confirmed",
        };
    }

    if (error.status === 429 || error.code === "over_request_rate_limit") {
        return {
            data: null,
            isError: true,
            message: LOGIN_RATE_LIMIT_MESSAGE,
            status: 429,
            code: "over_request_rate_limit",
        };
    }

    return {
        data: null,
        isError: true,
        message: "Email o contraseña incorrectos",
        status: 401,
    };
}
