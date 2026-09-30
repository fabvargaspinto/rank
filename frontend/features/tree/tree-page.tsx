import { redirect } from "next/navigation";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import AccountMenu from "@/features/account/component/account-menu";
import { getInstagramConnectionAction, getInstagramFollowersAction } from "@/features/instagram/actions";
import type { InstagramOAuthStatus } from "@/features/instagram/model";
import { getCurrentUser } from "@/lib/api/profile";
import { LOGIN_PATH } from "@/lib/post-auth-path";
import { getPostsAction } from "./action/get-posts-action";
import Tree from "./component/tree";
import { POSTS_PAGE_SIZE } from "./post-constants";

export default async function TreePage({
    instagramStatus,
}: {
    instagramStatus?: InstagramOAuthStatus;
}) {
    const result = await getCurrentUser();

    if (result.status === 401) {
        redirect(LOGIN_PATH);
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
    const instagram = await getInstagramConnectionAction();
    const history =
        instagram.data?.connected === true
            ? await getInstagramFollowersAction()
            : null;

    return (
        <PageWrapper>
            <AccountMenu />
            <Tree
                user={result.data}
                initialPosts={posts?.data?.items ?? []}
                initialNextCursor={posts?.data?.next_cursor ?? null}
                editable
                instagramStatus={instagramStatus}
                instagramConnection={instagram.data ?? undefined}
                instagramHistory={history?.data?.items ?? []}
            />
        </PageWrapper>
    );
}
