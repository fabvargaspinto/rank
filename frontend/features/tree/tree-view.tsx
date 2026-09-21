import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import getUserFromName from "./action/get-user-from-name";
import Tree from "./component/tree";
import EmptyTree from "../empty-tree/empty-tree";

export default async function TreeViewPage({ username }: { username: string }) {
    const result = await getUserFromName(username);

    if (result.isError || !result.data) {
        return (
            <EmptyTree />
        );
    }

    return (
        <PageWrapper>
            <Tree user={result.data} />
        </PageWrapper>
    );
}
