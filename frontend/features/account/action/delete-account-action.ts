"use server";

import { redirect } from "next/navigation";
import { deleteAccount, type FetchDataResponse } from "@/lib/fetch_data";
import { createClient } from "@/lib/supabase/server";
import { getAuthSession } from "@/lib/supabase/session";

export async function deleteAccountAction(
    _prev: FetchDataResponse,
    _formData: FormData,
): Promise<FetchDataResponse> {
    const session = await getAuthSession();

    if (!session) {
        redirect("/login");
    }

    const result = await deleteAccount(session.accessToken);

    if (result.isError) {
        return {
            ...result,
            message: "No se pudo borrar la cuenta.",
        };
    }

    const supabase = await createClient();
    await supabase.auth.signOut();
    redirect("/login");
}
