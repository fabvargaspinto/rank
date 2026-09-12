import PageWrapper from "../ui/page-wrapper/page-wrapper";
import RegisterForm from "./component/register-form";

type RegisterPageProps = {
    initialError?: string;
};

export default function RegisterPage({ initialError }: RegisterPageProps) {
    return (
        <PageWrapper>
            <RegisterForm initialError={initialError} />
        </PageWrapper>
    );
}
