import type { EmailOtpType } from "@supabase/supabase-js";

export function otpType(value: string | null | undefined): EmailOtpType | null {
    if (
        value === "signup" ||
        value === "invite" ||
        value === "magiclink" ||
        value === "recovery" ||
        value === "email_change" ||
        value === "email"
    ) {
        return value;
    }

    return null;
}
