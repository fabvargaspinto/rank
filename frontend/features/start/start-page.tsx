import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import AccountMenu from "@/features/account/component/account-menu";
import StartForm from "./component/start-form";

export default function StartPage() {
    return (
        <PageWrapper>
            <AccountMenu />
            <StartForm />
        </PageWrapper>
    );
}
