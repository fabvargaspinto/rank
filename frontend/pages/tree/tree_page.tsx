import WrapPage from "@/ui/wrap-page/wrap-page";
import Tree from "./component/tree";
import { getUserByName } from "@/action/get_user_by_name";


export default  async function  TreePage({ username }: { username: string }) {
    
    
    return (
        <WrapPage>
            <Tree />
        </WrapPage>
    );
}