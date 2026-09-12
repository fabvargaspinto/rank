"use server";

import { startGoogleOAuthAction } from "@/lib/google-oauth-action";

export async function registerGoogleAction(_formData?: FormData) {
    await startGoogleOAuthAction("/register");
}
