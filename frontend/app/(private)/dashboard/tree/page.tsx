import { redirect } from "next/navigation";
import TreePage from "@/features/tree/tree-page";
import { DASHBOARD_TREE_PATH, getPostAuthPath } from "@/lib/post-auth-path";

export default async function page() {
    const path = await getPostAuthPath();

    if (path !== DASHBOARD_TREE_PATH) {
        redirect(path);
    }

    return <TreePage />;
}
