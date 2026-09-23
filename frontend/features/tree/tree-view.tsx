import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import { COMMENTS_PAGE_SIZE } from "./comment-constants";
import { getCommentsAction } from "./action/get-comments-action";
import getUserFromName from "./action/get-user-from-name";
import Tree from "./component/tree";
import EmptyTree from "../empty-tree/empty-tree";

export default async function TreeViewPage({ username }: { username: string }) {
    const result = await getUserFromName(username);

    if (result.isError || !result.data) {
        return <EmptyTree />;
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
