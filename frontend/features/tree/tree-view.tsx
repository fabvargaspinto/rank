import { notFound } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
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

    return (
        <PageWrapper>
            <Tree
                user={result.data}
                initialPosts={result.data.posts ?? []}
                initialNextCursor={result.data.next_cursor}
            />
        </PageWrapper>
    );
}
