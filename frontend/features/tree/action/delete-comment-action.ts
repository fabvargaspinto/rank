"use server";

import { deleteComment, type FetchDataResponse } from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

export async function deleteCommentAction(
    commentId: string,
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

    return deleteComment(session.accessToken, commentId);
}
