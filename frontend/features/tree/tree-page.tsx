import { redirect } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import AccountMenu from "@/features/account/component/account-menu";
import { POSTS_PAGE_SIZE } from "./post-constants";
import { getPostsAction } from "./action/get-posts-action";
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
                <AccountMenu />
                <p>{result.message || "No se pudo cargar tu perfil"}</p>
            </PageWrapper>
        );
    }

    const posts = result.data.name
        ? await getPostsAction(result.data.name, {
              limit: POSTS_PAGE_SIZE,
          })
        : null;

    return (
        <PageWrapper>
            <AccountMenu />
            <Tree
                user={result.data}
                initialPosts={posts?.data?.items ?? []}
                initialNextCursor={posts?.data?.next_cursor ?? null}
                editable
            />
        </PageWrapper>
    );
}
