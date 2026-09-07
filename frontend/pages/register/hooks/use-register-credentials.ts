'use client';

import { useRouter } from 'next/navigation';
import { registerCredentialsAuth } from '@/action/register_credentials_auth';
import { useFetchAction } from '@/lib/use_fetch_action';

export function useRegisterCredentials({ name }: { name: string }) {
    const router = useRouter();
    const [state, action, pending] = useFetchAction(registerCredentialsAuth, {
        onSuccess: () => {
            router.push('/home');
        },
    });

    return {
        name,
        action,
        pending,
        canSubmit: name.trim().length > 0,
        isError: state.isError,
        errorMessage: state.isError ? state.message : '',
    };
}
