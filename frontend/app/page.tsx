import { redirect } from "next/navigation";
import { getPostAuthPath } from "@/lib/post-auth-path";

export default async function page() {
    redirect(await getPostAuthPath());
}
