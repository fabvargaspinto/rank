import { fetchAction } from "@/lib/fetch_action";
import { ActionResponse } from "./action-response";

interface User {
    id: string;
    name: string;
    description: string;
    avatar_url: string;
    created_at: string;
    updated_at: string;
}

export async function getUserByName(name: string) {
    const response: ActionResponse<User> = await fetchAction({
        path: `/user/name/${name}`,
        method: "GET",
    });
    if (response.isError) {
        return {
            message: response.message,
            isError: true,
            data: undefined,
        };
    }
    return {
        message: response.message,
        isError: false,
        data: response.data
    };
}

