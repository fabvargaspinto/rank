import { createCallbackClient } from "@/lib/supabase/server";
import { provisionSession } from "@/lib/fetch_data";
import { postAuthPathForToken } from "@/lib/post-auth-path";

function fromPath(value: string | null) {
    return value === "register" ? "/register" : "/login";
}

export async function GET(request: Request) {
    const { searchParams, origin } = new URL(request.url);
    const code = searchParams.get("code");
    const from = fromPath(searchParams.get("from"));
    const { supabase, redirect } = await createCallbackClient();

    if (searchParams.get("error") || !code) {
        return redirect(
            `${origin}${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const { data, error } = await supabase.auth.exchangeCodeForSession(code);

    if (error || !data.session) {
        return redirect(
            `${origin}${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const response = await provisionSession(data.session.access_token);

    if (response.isError) {
        return redirect(
            `${origin}${from}?error=${encodeURIComponent(response.message)}`,
        );
    }

    const destination = await postAuthPathForToken(
        data.session.user.id,
        data.session.access_token,
    );

    return redirect(`${origin}${destination}`);
}
