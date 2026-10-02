"use server";

import { startGoogleOAuthAction } from "@/lib/google-oauth-action";

export async function loginGoogleAction(formData?: FormData) {
    void formData;
    await startGoogleOAuthAction("/login");
}
