import { redirect } from "next/navigation";
import LoginPage from "@/features/login/login-page";
import { getAuthSession } from "@/lib/supabase/session";

type HomeProps = {
    searchParams: Promise<{ error?: string }>;
};

export default async function page({ searchParams }: HomeProps) {
    if (await getAuthSession()) {
        redirect("/tree");
    }

    const params = await searchParams;

    return <LoginPage initialError={params.error} />;
}
