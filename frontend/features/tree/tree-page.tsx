import { redirect } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import { COMMENTS_PAGE_SIZE } from "./comment-constants";
import { getCommentsAction } from "./action/get-comments-action";
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

    const comments = await getCommentsAction(result.data.id, {
        limit: COMMENTS_PAGE_SIZE,
        offset: 0,
    });

    return (
        <PageWrapper>
            <Tree
                user={result.data}
                initialComments={comments.data?.items ?? []}
                editable
            />
        </PageWrapper>
    );
}
