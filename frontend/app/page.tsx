import { redirect } from "next/navigation";
import { getAuthSession } from "@/lib/supabase/session";

export default async function page() {
    const session = await getAuthSession();
    redirect(session ? "/dashboard" : "/login");
}
