'use client';

import { startTransition, useActionState, useRef, type SubmitEventHandler } from 'react';
import { ActionResponse } from '@/action/action-response';

type ActionFn<T> = (
    previousState: ActionResponse<T>,
    formData: FormData,
) => Promise<ActionResponse<T>>;

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

    const [state, dispatch, pending] = useActionState(
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

    const handleSubmit: SubmitEventHandler<HTMLFormElement> = (event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        startTransition(() => {
            dispatch(formData);
        });
    };

    return [state, handleSubmit, pending] as const;
}
