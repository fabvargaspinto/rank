import { redirect } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import getUserFromJwt from "./action/get-user-from-jwt";
import Tree from "./component/tree";

export default async function TreePage() {
    const result = await getUserFromJwt();

    if (result.status === 401) {
        redirect("/login");
    }

    if (result.isError || !result.data) {
        return (
            <PageWrapper>
                <p>{result.message || "No se pudo cargar tu perfil"}</p>
            </PageWrapper>
        );
    }

    return (
        <PageWrapper>
            <Tree user={result.data} editable />
        </PageWrapper>
    );
}
