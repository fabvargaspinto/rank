import { redirect } from "next/navigation";
import TreePage from "@/features/tree/tree-page";
import { DASHBOARD_TREE_PATH, getPostAuthPath } from "@/lib/post-auth-path";

type PageProps = {
    searchParams: Promise<{ instagram?: string }>;
};

export default async function page({ searchParams }: PageProps) {
    const path = await getPostAuthPath();

    if (path !== DASHBOARD_TREE_PATH) {
        redirect(path);
    }

    const params = await searchParams;
    const instagramStatus =
        params.instagram === "connected" || params.instagram === "error"
            ? params.instagram
            : undefined;

    return <TreePage instagramStatus={instagramStatus} />;
}
