'use client';

import { useState } from 'react';

export function useRegisterSteps() {
    const [step, setStep] = useState(0);

    return {
        step,
        goToData: () => setStep(1),
        goToName: () => setStep(0),
    };
}
