import { redirect } from "next/navigation";
import UnavailablePage from "@/features/unavailable/unavailable-page";
import {
    DASHBOARD_UNAVAILABLE_PATH,
    getPostAuthPath,
} from "@/lib/post-auth-path";

export default async function page() {
    const path = await getPostAuthPath();

    if (path !== DASHBOARD_UNAVAILABLE_PATH) {
        redirect(path);
    }

    return <UnavailablePage />;
}
