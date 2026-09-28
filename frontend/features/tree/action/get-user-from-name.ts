import { cache } from "react";
import {
    fetchUserByName,
    type FetchDataResponse,
    type UserResponse,
} from "@/lib/fetch_data";

const getUserFromName = cache(
    async function getUserFromName(
        name: string,
    ): Promise<FetchDataResponse<UserResponse>> {
        const username = name?.trim() ?? "";

        if (!username) {
            return {
                data: null,
                isError: true,
                message: "El usuario no existe",
                status: 404,
            };
        }

        return fetchUserByName(username);
    },
);

export default getUserFromName;
