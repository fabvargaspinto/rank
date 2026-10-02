import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import AuthShell from "@/features/legal/auth-shell";
import LoginForm from "./component/login-form";

type LoginPageProps = {
    initialError?: string;
};

export default function LoginPage({ initialError }: LoginPageProps) {
    return (
        <PageWrapper>
            <AuthShell>
                <LoginForm initialError={initialError} />
            </AuthShell>
        </PageWrapper>
    );
}
