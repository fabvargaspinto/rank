import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { provisionSession } from "@/lib/fetch_data";

function fromPath(value: string | null) {
    return value === "register" ? "/register" : "/";
}

export async function GET(request: Request) {
    const { searchParams, origin } = new URL(request.url);
    const code = searchParams.get("code");
    const from = fromPath(searchParams.get("from"));

    if (searchParams.get("error") || !code) {
        return NextResponse.redirect(
            `${origin}${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const supabase = await createClient();
    const { data, error } = await supabase.auth.exchangeCodeForSession(code);

    if (error || !data.session) {
        return NextResponse.redirect(
            `${origin}${from}?error=${encodeURIComponent("No se pudo completar el acceso con Google")}`,
        );
    }

    const response = await provisionSession(data.session.access_token);

    if (response.isError) {
        return NextResponse.redirect(
            `${origin}${from}?error=${encodeURIComponent(response.message)}`,
        );
    }

    return NextResponse.redirect(`${origin}/`);
}
