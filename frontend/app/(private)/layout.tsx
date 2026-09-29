import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { LOGIN_PATH } from "@/lib/post-auth-path";
import { getAuthSession } from "@/lib/supabase/session";

export default async function PrivateLayout({
    children,
}: {
    children: ReactNode;
}) {
    const session = await getAuthSession();

    if (!session) {
        redirect(LOGIN_PATH);
    }

    return children;
}
