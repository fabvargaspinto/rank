"use server";

import { redirect } from "next/navigation";
import type { FetchDataResponse } from "@/lib/api/types";
import { getPostAuthPath } from "@/lib/post-auth-path";
import { createClient } from "@/lib/supabase/server";
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

    if (!session) {
        return {
            data: null,
            isError: true,
            message: "El enlace venció. Pedí uno nuevo.",
            status: 401,
        };
    }

    const supabase = await createClient();
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

    redirect(await getPostAuthPath());
}
