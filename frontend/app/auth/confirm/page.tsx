import { redirect } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import ConfirmEmailForm from "@/features/account/component/confirm-email-form";
import AuthShell from "@/features/legal/auth-shell";
import { authErrorQuery } from "@/lib/auth/auth-error";
import { otpType } from "@/lib/auth/email-otp-type";

const RESET_PATH = "/reset-password";
const EXPIRED_LINK = `/login?${authErrorQuery("link_expired")}`;

type ConfirmPageProps = {
    searchParams: Promise<{
        token_hash?: string;
        type?: string;
        code?: string;
        next?: string;
    }>;
};

export default async function ConfirmPage({ searchParams }: ConfirmPageProps) {
    const params = await searchParams;
    const tokenHash = params.token_hash?.trim() ?? "";
    const type = otpType(params.type?.trim() ?? null);
    const code = params.code?.trim() ?? "";
    const next = params.next === RESET_PATH ? RESET_PATH : "";

    const canConfirm = Boolean((tokenHash && type) || code);
    if (!canConfirm) {
        redirect(EXPIRED_LINK);
    }

    const isRecovery = type === "recovery" || next === RESET_PATH;

    return (
        <PageWrapper>
            <AuthShell>
                <ConfirmEmailForm
                    tokenHash={tokenHash}
                    type={type ?? ""}
                    code={code}
                    next={next}
                    submitLabel={isRecovery ? "Continuar" : "Confirmar email"}
                    description={
                        isRecovery
                            ? "Tocá el botón para seguir y elegir una contraseña nueva."
                            : "Tocá el botón para confirmar tu email."
                    }
                />
            </AuthShell>
        </PageWrapper>
    );
}
