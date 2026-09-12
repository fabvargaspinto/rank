import RegisterPage from "@/pages/register/register-page"

type RegisterRouteProps = {
    searchParams: Promise<{ error?: string }>;
};

export default async function page({ searchParams }: RegisterRouteProps) {
    const params = await searchParams;

    return (
        <RegisterPage initialError={params.error} />
    );
}
