import WrapPage from "@/ui/wrap-page/wrap-page";
import Tree from "./component/tree";

export interface UserProfile {
    username: string;
    description: string;
    image: string;
}


export default  async function  TreePage({ userProfile }: { userProfile: UserProfile }) {
    
    
    return (
        <WrapPage>
            <Tree profile={userProfile} />
        </WrapPage>
    );
}