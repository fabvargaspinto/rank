import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import ExpiredResetLink from "@/features/account/component/expired-reset-link";
import ResetPasswordForm from "@/features/account/component/reset-password-form";
import { getAuthSession } from "@/lib/supabase/session";

export default async function page() {
    const session = await getAuthSession();

    return (
        <PageWrapper>
            {session ? <ResetPasswordForm /> : <ExpiredResetLink />}
        </PageWrapper>
    );
}
