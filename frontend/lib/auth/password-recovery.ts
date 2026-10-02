import "server-only";

import { cookies } from "next/headers";

export const PASSWORD_RECOVERY_COOKIE = "sn_password_recovery";
const MAX_AGE_SECONDS = 10 * 60;

function recoveryCookieOptions(maxAge: number) {
    return {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax" as const,
        path: "/",
        maxAge,
    };
}

/** Marca que el usuario llegó por un enlace de recuperación (válido 10 min). */
export async function allowPasswordRecovery(): Promise<void> {
    const cookieStore = await cookies();
    cookieStore.set(
        PASSWORD_RECOVERY_COOKIE,
        "1",
        recoveryCookieOptions(MAX_AGE_SECONDS),
    );
}

/** Exige y consume la cookie de recuperación. */
export async function consumePasswordRecovery(): Promise<boolean> {
    const cookieStore = await cookies();
    const allowed = cookieStore.get(PASSWORD_RECOVERY_COOKIE)?.value === "1";
    cookieStore.set(PASSWORD_RECOVERY_COOKIE, "", recoveryCookieOptions(0));
    return allowed;
}
