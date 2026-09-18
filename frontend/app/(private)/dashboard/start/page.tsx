import { redirect } from "next/navigation";
import StartPage from "@/features/start/start-page";
import { getAuthSession } from "@/lib/supabase/session";

export default async function page() {
    if (!(await getAuthSession())) {
        redirect("/login");
    }

    return <StartPage />;
}
