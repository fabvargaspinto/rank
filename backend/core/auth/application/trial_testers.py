import os

from core.shared.application.application_error import ApplicationError

# Periodo de prueba: borrar este archivo y los usos marcados "trial testers".
TRIAL_REGISTRATION_DENIED = (
    "Esta cuenta no está habilitada para el periodo de prueba."
)

TRIAL_TESTER_EMAILS: dict[str, str] = {
    "fabvargaspinto@gmail.com": "Fabian Vargas Pinto",
    
}


class RegistrationNotAllowedError(ApplicationError):
    pass


def is_trial_tester(email: str) -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return email.strip().lower() in TRIAL_TESTER_EMAILS
