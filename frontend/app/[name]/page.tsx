import type { Metadata } from "next";
import TreeViewPage from "@/features/tree/tree-view";
import getUserFromName from "@/features/tree/action/get-user-from-name";

type PageProps = {
    params: Promise<{ name: string }>;
};

export async function generateMetadata({
    params,
}: PageProps): Promise<Metadata> {
    const { name } = await params;
    const result = await getUserFromName(name);

    const missing =
        result.status === 404 || result.code === "INVALID_USERNAME";

    if (missing || !result.data?.name) {
        return missing ? { title: "Perfil no encontrado" } : {};
    }

    const username = result.data.name.trim();
    const visibleName = result.data.display_name?.trim() || username;
    const description =
        result.data.description?.trim() || `Los links de ${visibleName}`;
    const avatar = result.data.avatar?.trim();

    return {
        title: visibleName,
        description,
        openGraph: {
            title: visibleName,
            description,
            ...(avatar ? { images: [avatar] } : {}),
        },
    };
}

export default async function page({ params }: PageProps) {
    const { name } = await params;

    return <TreeViewPage username={name} />;
}
