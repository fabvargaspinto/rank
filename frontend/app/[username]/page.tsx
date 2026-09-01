import { getUserByName } from "@/action/get_user_by_name";
import TreePage from "@/pages/tree/tree_page";

export default async function Page({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = await params;
  const {data, isError, message} = await getUserByName(username);
   
    console.log(message,"message from getUserByName");
    console.log(data,"data from getUserByName");
    
    if (isError) {
        return <div>Error: {message}</div>;
    }

  return (
    <TreePage username={username} />
  );
}