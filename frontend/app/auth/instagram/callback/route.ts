import { redirect } from "next/navigation";
import { completeInstagramConnect } from "@/lib/api/instagram";
import { authErrorQuery } from "@/lib/auth/auth-error";
import { getAuthSession } from "@/lib/supabase/session";

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const session = await getAuthSession();

    if (!session) {
        redirect(`/login?${authErrorQuery("session_expired")}`);
    }

    const result = await completeInstagramConnect(session.accessToken, {
        code: searchParams.get("code"),
        state: searchParams.get("state"),
        error: searchParams.get("error"),
    });

    redirect(
        `/dashboard/tree?instagram=${result.isError ? "error" : "connected"}`,
    );
}
