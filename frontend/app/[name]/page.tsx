import TreeViewPage from "@/features/tree/tree-view";

type PublicTreeProps = {
    params: Promise<{ name: string }>;
};

export default async function page({ params }: PublicTreeProps) {
    const { name } = await params;

    return <TreeViewPage username={name} />;
}
