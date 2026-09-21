import { redirect } from "next/navigation";
import LoginPage from "@/features/login/login-page";
import { LOGIN_PATH, getPostAuthPath } from "@/lib/post-auth-path";

type HomeProps = {
    searchParams: Promise<{ error?: string }>;
};

export default async function page({ searchParams }: HomeProps) {
    const path = await getPostAuthPath();

    if (path !== LOGIN_PATH) {
        redirect(path);
    }

    const params = await searchParams;

    return <LoginPage initialError={params.error} />;
}
