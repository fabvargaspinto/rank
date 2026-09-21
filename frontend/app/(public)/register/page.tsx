import { redirect } from "next/navigation";
import RegisterPage from "@/features/register/register-page";
import { LOGIN_PATH, getPostAuthPath } from "@/lib/post-auth-path";

type RegisterRouteProps = {
    searchParams: Promise<{ error?: string }>;
};

export default async function page({ searchParams }: RegisterRouteProps) {
    const path = await getPostAuthPath();

    if (path !== LOGIN_PATH) {
        redirect(path);
    }

    const params = await searchParams;

    return <RegisterPage initialError={params.error} />;
}
