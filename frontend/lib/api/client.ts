import "server-only";

import type { FetchDataResponse } from "@/lib/api/types";

const REQUEST_TIMEOUT_MS = 10_000;
const NETWORK_ERROR_MESSAGE = "No se pudo conectar con el servidor";
const UNREADABLE_ERROR_MESSAGE = "No se pudo completar la solicitud";

let cachedBackendUrl: string | undefined;

export function backendUrl(): string {
    if (cachedBackendUrl) {
        return cachedBackendUrl;
    }

    const url = process.env.BACKEND_URL?.trim();

    if (!url) {
        throw new Error("Falta BACKEND_URL");
    }

    cachedBackendUrl = url.replace(/\/$/, "");
    return cachedBackendUrl;
}

function messageFromBackend(data: unknown): string {
    if (!data || typeof data !== "object" || !("detail" in data)) {
        return UNREADABLE_ERROR_MESSAGE;
    }

    const { detail } = data;

    if (typeof detail === "string" && detail.trim()) {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((item) =>
                item && typeof item === "object" && "msg" in item
                    ? String(item.msg)
                    : "",
            )
            .filter((item) => item.length > 0);

        if (messages.length > 0) {
            return messages.join(", ");
        }
    }

    return UNREADABLE_ERROR_MESSAGE;
}

function errorMeta(data: unknown): { code?: string; field?: string } {
    if (!data || typeof data !== "object") {
        return {};
    }

    const record = data as { code?: unknown; field?: unknown };

    return {
        ...(typeof record.code === "string" ? { code: record.code } : {}),
        ...(typeof record.field === "string" ? { field: record.field } : {}),
    };
}

export async function fetchData<T = unknown>(
    path: string,
    options: RequestInit = {},
): Promise<FetchDataResponse<T>> {
    const url = path.startsWith("http") ? path : `${backendUrl()}${path}`;
    const requestId = crypto.randomUUID();
    const { signal: callerSignal, headers, body, ...rest } = options;
    const timeout = AbortSignal.timeout(REQUEST_TIMEOUT_MS);
    const signal = callerSignal
        ? AbortSignal.any([callerSignal, timeout])
        : timeout;

    try {
        const response = await fetch(url, {
            ...rest,
            body,
            signal,
            headers: {
                ...(body instanceof FormData
                    ? {}
                    : { "Content-Type": "application/json" }),
                "X-Request-ID": requestId,
                ...headers,
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
                ...errorMeta(data),
            };
        }

        return {
            data: data as T,
            isError: false,
            message: "",
            status: response.status,
            requestId: echoedId,
        };
    } catch {
        return {
            data: null,
            isError: true,
            message: NETWORK_ERROR_MESSAGE,
            status: 0,
            requestId,
        };
    }
}
