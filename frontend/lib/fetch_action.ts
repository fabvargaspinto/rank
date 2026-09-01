import { ActionResponse } from '@/action/action-response';

type FetchActionOptions = {
    path: string,
    method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
    body?: unknown,
    fallbackMessage?: string,
};

export async function fetchAction<T = void>({
    path,
    method = "POST",
    body,
    fallbackMessage = "no se pudo completar la acción",
}: FetchActionOptions): Promise<ActionResponse<T>> {
    try {
        const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
        const response = await fetch(`${apiUrl}${path}`, {
            method,
            headers: {
                Accept: "application/json",
                ...(body === undefined ? {} : { "Content-Type": "application/json" }),
            },
            body: body === undefined ? undefined : JSON.stringify(body),
        });

        const payload = await response.json().catch(() => null);
        const message = typeof payload?.message === "string"
            ? payload.message
            : response.statusText;

        if (!response.ok || payload?.isError) {
            return {
                message: message || fallbackMessage,
                isError: true,
            };
        }

        return {
            message: message || "",
            isError: false,
            data: payload?.data as T | undefined,
        };
    } catch {
        return {
            message: fallbackMessage,
            isError: true,
        };
    }
}
