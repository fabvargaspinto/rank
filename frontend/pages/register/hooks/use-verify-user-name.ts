'use client';

import { useState } from 'react';
import { verifyUserName } from '@/action/verify_user_name';
import { useFetchAction } from '@/lib/use_fetch_action';

export function useVerifyUserName({ onSuccess }: { onSuccess: (name: string) => void }) {
    const [name, setName] = useState('');
    const canContinue = name.trim().length > 0;
    const [state, action, pending] = useFetchAction(verifyUserName, {
        onSuccess: () => onSuccess(name.trim()),
    });

    return {
        name,
        onNameChange: setName,
        canContinue,
        action,
        pending,
        isError: state.isError,
        errorMessage: state.isError ? state.message : "",
    };
}
