import { notFound } from "next/navigation";
import { getUserByName } from "@/action/get_user_by_name";
import TreePage from "@/pages/tree/tree_page";

function isValidUserName(username: string) {
  return /^[a-zA-Z0-9-_]{3,32}$/.test(username);
}

export default async function Page({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = await params;

  if (!isValidUserName(username)) {
    notFound();
  }

  const {data, isError, message} = await getUserByName(username);
    
    if (isError) {
        return <div>Error: {message}</div>;
    }

    if (!data) {
        return <div>User not found</div>;
    }

  return (
    <TreePage userProfile={{ username: data.name, description: data.description, image: data.avatar_url }} />
  );
}