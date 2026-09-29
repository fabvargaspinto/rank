import { cache } from "react";
import {
    fetchUserByName,
    type FetchDataResponse,
    type PublicProfileResponse,
} from "@/lib/fetch_data";
import { COMMENTS_PAGE_SIZE } from "../comment-constants";

const getUserFromName = cache(
    async function getUserFromName(
        name: string,
    ): Promise<FetchDataResponse<PublicProfileResponse>> {
        const username = name?.trim() ?? "";

        if (!username) {
            return {
                data: null,
                isError: true,
                message: "El usuario no existe",
                status: 404,
            };
        }

        return fetchUserByName(username, { limit: COMMENTS_PAGE_SIZE });
    },
);

export default getUserFromName;
