"use server";

import { redirect } from "next/navigation";
import type { FetchDataResponse } from "@/lib/api/types";
import { consumePasswordRecovery } from "@/lib/auth/password-recovery";
import { getPostAuthPath } from "@/lib/post-auth-path";
import { createAuthClient } from "@/lib/supabase/auth-client";
import { getAuthSession } from "@/lib/supabase/session";
import { invalidFormResponse, resetPasswordSchema } from "@/lib/validation/auth";

export async function resetPasswordAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const parsed = resetPasswordSchema.safeParse({
        password: String(formData.get("password") ?? ""),
        passwordConfirmation: String(formData.get("passwordConfirmation") ?? ""),
    });

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const session = await getAuthSession();
    const fromRecovery = await consumePasswordRecovery();

    if (!session || !fromRecovery) {
        return {
            data: null,
            isError: true,
            message: "El enlace venció. Pedí uno nuevo.",
            status: 401,
        };
    }

    const supabase = await createAuthClient();
    const { error } = await supabase.auth.updateUser({
        password: parsed.data.password,
    });

    if (error) {
        return {
            data: null,
            isError: true,
            message: "No se pudo guardar la contraseña.",
            status: 400,
        };
    }

    await supabase.auth.signOut({ scope: "others" });

    redirect(await getPostAuthPath());
}
