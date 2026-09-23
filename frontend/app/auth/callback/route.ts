import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { provisionSession } from "@/lib/fetch_data";
import { postAuthPathForToken } from "@/lib/post-auth-path";

function fromPath(value: string | null) {
    return value === "register" ? "/register" : "/login";
}

export async function GET(request: Request) {
    // request.url carries the server bind host (0.0.0.0 in Docker), not the
    // browser's host, so redirects must stay relative to keep the session cookies.
    const { searchParams } = new URL(request.url);
    const code = searchParams.get("code");
    const from = fromPath(searchParams.get("from"));
    const supabase = await createClient();

    if (searchParams.get("error") || !code) {
        redirect(
            `${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const { data, error } = await supabase.auth.exchangeCodeForSession(code);

    if (error || !data.session) {
        redirect(
            `${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const response = await provisionSession(data.session.access_token);

    if (response.isError) {
        redirect(`${from}?error=${encodeURIComponent(response.message)}`);
    }

    redirect(
        await postAuthPathForToken(
            data.session.user.id,
            data.session.access_token,
        ),
    );
}
