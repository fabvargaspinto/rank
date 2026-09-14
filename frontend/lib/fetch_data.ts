const API_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export type FetchDataResponse<T = unknown> = {
    data: T | null;
    isError: boolean;
    message: string;
    status: number;
};

export const emptyFetchResponse: FetchDataResponse = {
    data: null,
    isError: false,
    message: "",
    status: 0,
};

function messageFromBackend(data: unknown): string {
    if (!data || typeof data !== "object" || !("detail" in data)) {
        return "Request failed";
    }

    const { detail } = data;

    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map((item) =>
                item && typeof item === "object" && "msg" in item
                    ? String(item.msg)
                    : JSON.stringify(item),
            )
            .join(", ");
    }

    return "Request failed";
}

export type SessionResponse = {
    provisioned: boolean;
};

export async function provisionSession(
    accessToken: string,
): Promise<FetchDataResponse<SessionResponse>> {
    return fetchData<SessionResponse>("/auth/session", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchData<T = unknown>(
    path: string,
    options: RequestInit = {},
): Promise<FetchDataResponse<T>> {
    const url = path.startsWith("http") ? path : `${API_URL}${path}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            return {
                data: null,
                isError: true,
                message: messageFromBackend(data),
                status: response.status,
            };
        }

        return {
            data: data as T,
            isError: false,
            message: "",
            status: response.status,
        };
    } catch (error) {
        return {
            data: null,
            isError: true,
            message: error instanceof Error ? error.message : "Request failed",
            status: 0,
        };
    }
}
