'use client';

import { useActionState, useRef } from 'react';
import { ActionResponse } from '@/action/action-response';

type FetchActionOptions = {
    path: string,
    method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
    body?: unknown,
    fallbackMessage?: string,
};

type ActionFn<T> = (
    previousState: ActionResponse<T>,
    formData: FormData,
) => Promise<ActionResponse<T>>;

export async function fetchAction<T = void>({
    path,
    method = "POST",
    body,
    fallbackMessage = "no se pudo completar la acción",
}: FetchActionOptions): Promise<ActionResponse<T>> {
    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
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

export function useFetchAction<T = void>(
    action: ActionFn<T>,
    options?: {
        initialState?: ActionResponse<T>,
        onSuccess?: (state: ActionResponse<T>) => void,
        onError?: (state: ActionResponse<T>) => void,
    },
) {
    const onSuccessRef = useRef(options?.onSuccess);
    const onErrorRef = useRef(options?.onError);
    onSuccessRef.current = options?.onSuccess;
    onErrorRef.current = options?.onError;

    return useActionState(
        async (previousState: ActionResponse<T>, formData: FormData) => {
            const result = await action(previousState, formData);

            if (result.isError) {
                onErrorRef.current?.(result);
            } else {
                onSuccessRef.current?.(result);
            }

            return result;
        },
        options?.initialState ?? {
            message: "",
            isError: false,
        },
    );
}
