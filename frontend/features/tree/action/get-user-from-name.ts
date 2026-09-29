import { cache } from "react";
import { fetchUserByName } from "@/lib/api/profile";
import type { FetchDataResponse, PublicProfileResponse } from "@/lib/api/types";
import { POSTS_PAGE_SIZE } from "../post-constants";

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

        return fetchUserByName(username, { limit: POSTS_PAGE_SIZE });
    },
);

export default getUserFromName;
