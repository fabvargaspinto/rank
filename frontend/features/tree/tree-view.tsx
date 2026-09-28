import { notFound } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import { COMMENTS_PAGE_SIZE } from "./comment-constants";
import { getCommentsAction } from "./action/get-comments-action";
import getUserFromName from "./action/get-user-from-name";
import Tree from "./component/tree";

export default async function TreeViewPage({ username }: { username: string }) {
    const result = await getUserFromName(username);

    if (result.status === 404 || result.code === "INVALID_USERNAME") {
        notFound();
    }

    if (result.isError || !result.data) {
        throw new Error("No se pudo cargar el perfil");
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
            />
        </PageWrapper>
    );
}
