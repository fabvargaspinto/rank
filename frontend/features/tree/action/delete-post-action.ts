"use server";

import { deletePost } from "@/lib/api/posts";
import type { FetchDataResponse } from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export async function deletePostAction(
    postId: string,
): Promise<FetchDataResponse<null>> {
    const session = await getAuthSession();

    if (!session) {
        return {
            data: null,
            isError: true,
            message: "Tenés que iniciar sesión",
            status: 401,
        };
    }

    return deletePost(session.accessToken, postId);
}
