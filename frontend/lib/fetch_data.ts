const API_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export type FetchDataResponse<T = unknown> = {
    data: T | null;
    isError: boolean;
    message: string;
    status: number;
    requestId?: string;
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

export type UserResponse = {
    id: string;
    name: string | null;
    avatar: string | null;
    description: string | null;
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

export async function fetchUserByAuthId(
    authId: string,
    accessToken: string,
): Promise<FetchDataResponse<UserResponse>> {
    return fetchData<UserResponse>(`/users/${encodeURIComponent(authId)}`, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchUserByName(
    name: string,
): Promise<FetchDataResponse<UserResponse>> {
    return fetchData<UserResponse>(
        `/users/name/${encodeURIComponent(name)}`,
    );
}

export async function fetchData<T = unknown>(
    path: string,
    options: RequestInit = {},
): Promise<FetchDataResponse<T>> {
    const url = path.startsWith("http") ? path : `${API_URL}${path}`;

    const requestId = crypto.randomUUID();

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                "X-Request-ID": requestId,
                ...options.headers,
            },
        });

        const data = await response.json().catch(() => null);
        const echoedId =
            response.headers.get("X-Request-ID")?.trim() || requestId;

        if (!response.ok) {
            return {
                data: null,
                isError: true,
                message: messageFromBackend(data),
                status: response.status,
                requestId: echoedId,
            };
        }

        return {
            data: data as T,
            isError: false,
            message: "",
            status: response.status,
            requestId: echoedId,
        };
    } catch (error) {
        return {
            data: null,
            isError: true,
            message: error instanceof Error ? error.message : "Request failed",
            status: 0,
            requestId,
        };
    }
}
