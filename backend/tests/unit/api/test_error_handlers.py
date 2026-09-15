from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from controller.error_handlers import register_error_handlers
from core.auth.application.application_error import (
    AuthAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
)
from core.auth.domain.auth_error import IdentityAlreadyExistsError, InvalidEmailError
from core.auth.infrastructure.error_infrastructure import AuthCreationError


class _Body(BaseModel):
    email: str


def _client() -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.post("/raise/application")
    def raise_application(kind: str):
        errors = {
            "email": EmailAlreadyExistsError("El email ya está registrado"),
            "auth": AuthAlreadyExistsError("El usuario ya existe"),
            "credentials": InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            ),
            "provider": InvalidAuthProviderError(
                "El proveedor debe ser un proveedor OAuth"
            ),
        }
        raise errors[kind]

    @app.post("/raise/domain")
    def raise_domain(kind: str):
        errors = {
            "email": InvalidEmailError("Invalid email address"),
            "identity": IdentityAlreadyExistsError("La identidad ya existe"),
        }
        raise errors[kind]

    @app.post("/raise/infrastructure")
    def raise_infrastructure():
        raise AuthCreationError("Error al guardar el usuario")

    @app.post("/raise/body")
    def raise_body(body: _Body):
        return body

    return TestClient(app)


class TestErrorHandlers:
    def test_duplicate_email_is_409(self):
        response = _client().post("/raise/application?kind=email")

        assert response.status_code == 409
        assert response.json() == {"detail": "El email ya está registrado"}

    def test_auth_already_exists_is_409(self):
        response = _client().post("/raise/application?kind=auth")

        assert response.status_code == 409

    def test_invalid_credentials_are_401(self):
        response = _client().post("/raise/application?kind=credentials")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "El token de autenticación no es válido"
        }

    def test_invalid_provider_is_400(self):
        response = _client().post("/raise/application?kind=provider")

        assert response.status_code == 400

    def test_domain_error_is_400(self):
        response = _client().post("/raise/domain?kind=email")

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid email address"}

    def test_identity_already_exists_is_409(self):
        response = _client().post("/raise/domain?kind=identity")

        assert response.status_code == 409
        assert response.json() == {"detail": "La identidad ya existe"}

    def test_infrastructure_error_is_500(self):
        response = _client().post("/raise/infrastructure")

        assert response.status_code == 500
        assert response.json() == {"detail": "Error al guardar el usuario"}

    def test_invalid_body_is_422(self):
        response = _client().post("/raise/body", json={})

        assert response.status_code == 422
        assert "detail" in response.json()
