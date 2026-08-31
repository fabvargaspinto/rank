'use client';

import { useState } from 'react';
import { verifyUserName } from '@/action/verify_user_name';
import { useFetchAction } from '@/lib/fetch_action';

export function useRegisterName({ onSuccess }: { onSuccess: () => void }) {
    const [name, setName] = useState('');
    const canContinue = name.trim().length > 0;
    const [state, action, pending] = useFetchAction(verifyUserName, {
        onSuccess,
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
