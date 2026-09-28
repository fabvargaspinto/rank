import type { Metadata } from "next";
import TreeViewPage from "@/features/tree/tree-view";
import getUserFromName from "@/features/tree/action/get-user-from-name";

export async function generateMetadata({
    params,
}: PageProps<"/[name]">): Promise<Metadata> {
    const { name } = await params;
    const result = await getUserFromName(name);

    const missing =
        result.status === 404 || result.code === "INVALID_USERNAME";

    if (missing || !result.data?.name) {
        return missing ? { title: "Perfil no encontrado" } : {};
    }

    const username = result.data.name.trim();
    const description =
        result.data.description?.trim() || `Los links de ${username}`;
    const avatar = result.data.avatar?.trim();

    return {
        title: username,
        description,
        openGraph: {
            title: username,
            description,
            ...(avatar ? { images: [avatar] } : {}),
        },
    };
}

export default async function page({ params }: PageProps<"/[name]">) {
    const { name } = await params;

    return <TreeViewPage username={name} />;
}
