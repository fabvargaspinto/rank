import LoginPage from "@/pages/login/login-page";

type HomeProps = {
    searchParams: Promise<{ error?: string }>;
};

export default async function Home({ searchParams }: HomeProps) {
    const params = await searchParams;

    return <LoginPage initialError={params.error} />;
}
