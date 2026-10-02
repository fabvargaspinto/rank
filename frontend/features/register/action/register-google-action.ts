"use server";

import { startGoogleOAuthAction } from "@/lib/google-oauth-action";

export async function registerGoogleAction(formData?: FormData) {
    void formData;
    await startGoogleOAuthAction("/register");
}
