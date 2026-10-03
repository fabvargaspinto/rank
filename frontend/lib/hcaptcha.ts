import "server-only";

import { headers } from "next/headers";
import type { FetchDataResponse } from "@/lib/api/types";

const CAPTCHA_REQUIRED_MESSAGE = "Completá la verificación anti-bot.";
const CAPTCHA_FAILED_MESSAGE =
    "No se pudo verificar el anti-bot. Probá de nuevo.";

export function hcaptchaSiteKey(): string | null {
    const key = process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY?.trim();
    return key || null;
}

export function isHcaptchaEnabled(): boolean {
    return hcaptchaSiteKey() != null;
}

function clientIpFromForwardedFor(
    value: string | null | undefined,
): string | undefined {
    const ip = value?.split(",")[0]?.trim();
    return ip || undefined;
}

type CaptchaResult =
    | { ok: true; token: string }
    | { ok: false; response: FetchDataResponse };

function captchaError(message: string): CaptchaResult {
    return {
        ok: false,
        response: {
            data: null,
            isError: true,
            message,
            status: 400,
            code: "captcha_failed",
        },
    };
}

async function verifyHcaptchaToken(
    token: string,
    remoteIp: string | undefined,
): Promise<boolean> {
    const secret = process.env.HCAPTCHA_SECRET_KEY?.trim();
    if (!secret) {
        if (process.env.NODE_ENV === "production") {
            throw new Error("Falta HCAPTCHA_SECRET_KEY");
        }
        // En local alcanza con el widget; Auth hosted no está en juego.
        return true;
    }

    const body = new URLSearchParams({
        secret,
        response: token,
    });
    if (remoteIp) {
        body.set("remoteip", remoteIp);
    }

    const response = await fetch("https://api.hcaptcha.com/siteverify", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
        cache: "no-store",
    });

    if (!response.ok) {
        return false;
    }

    const payload = (await response.json()) as { success?: boolean };
    return payload.success === true;
}

/**
 * Lee y valida el token del formulario.
 * Si no hay site key (dev/CI), no exige CAPTCHA.
 * Con createAuthClient (secret key) Supabase no verifica el CAPTCHA;
 * por eso lo validamos acá antes de llamar a Auth.
 */
export async function resolveCaptchaToken(
    formData: FormData,
): Promise<CaptchaResult> {
    if (!isHcaptchaEnabled()) {
        return { ok: true, token: "" };
    }

    const token = String(
        formData.get("captchaToken") ??
            formData.get("h-captcha-response") ??
            "",
    ).trim();

    if (!token) {
        return captchaError(CAPTCHA_REQUIRED_MESSAGE);
    }

    const remoteIp = clientIpFromForwardedFor(
        (await headers()).get("x-forwarded-for"),
    );
    const valid = await verifyHcaptchaToken(token, remoteIp);
    if (!valid) {
        return captchaError(CAPTCHA_FAILED_MESSAGE);
    }

    return { ok: true, token };
}
