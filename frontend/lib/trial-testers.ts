// Periodo de prueba: borrar este archivo y los usos marcados "trial testers".
export const TRIAL_REGISTRATION_DENIED =
    "Esta cuenta no está habilitada para el periodo de prueba.";

export const TRIAL_TESTER_EMAILS: Record<string, string> = {
    "fabvargaspinto@gmail.com": "Fabian Vargas Pinto"
};

export function isTrialTester(email: string): boolean {
    return email.trim().toLowerCase() in TRIAL_TESTER_EMAILS;
}
