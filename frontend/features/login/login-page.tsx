import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import LoginForm from "./component/login-form";

type LoginPageProps = {
    initialError?: string;
};

export default function LoginPage({ initialError }: LoginPageProps) {
    return (
        <PageWrapper>
            <LoginForm initialError={initialError} />
        </PageWrapper>
    );
}
