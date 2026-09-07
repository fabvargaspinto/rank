'use client';

import { loginAuth } from '@/action/login_auth';
import { useFetchAction } from '@/lib/use_fetch_action';

export function useLogin() {
    const [state, action, pending] = useFetchAction(loginAuth);

    return {
        action,
        pending,
        isError: state.isError,
        errorMessage: state.isError ? state.message : '',
        isSuccess: !state.isError && Boolean(state.message),
        successMessage: !state.isError ? state.message : '',
    };
}
