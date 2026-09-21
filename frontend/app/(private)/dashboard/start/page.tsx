import { redirect } from "next/navigation";
import StartPage from "@/features/start/start-page";
import { DASHBOARD_START_PATH, getPostAuthPath } from "@/lib/post-auth-path";

export default async function page() {
    const path = await getPostAuthPath();

    if (path !== DASHBOARD_START_PATH) {
        redirect(path);
    }

    return <StartPage />;
}
