import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import AuthShell from "@/features/legal/auth-shell";
import RegisterForm from "./component/register-form";

type RegisterPageProps = {
    initialError?: string;
};

export default function RegisterPage({ initialError }: RegisterPageProps) {
    return (
        <PageWrapper>
            <AuthShell>
                <RegisterForm initialError={initialError} />
            </AuthShell>
        </PageWrapper>
    );
}
