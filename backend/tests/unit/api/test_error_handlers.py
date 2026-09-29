from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.errors import register_error_handlers
from api.request_id import REQUEST_ID_HEADER, register_request_id
from core.auth.application.application_error import (
    AuthAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    UnsupportedAuthProviderError,
)
from core.auth.domain.auth_error import (
    IdentityAlreadyExistsError,
    InvalidAuthProviderError,
    InvalidEmailError,
)
from core.auth.infrastructure.error_infrastructure import AuthCreationError
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user_error import UsernameAlreadyTakenError


class _Body(BaseModel):
    email: str


def _client() -> TestClient:
    app = FastAPI()
    register_request_id(app)
    register_error_handlers(app)

    @app.post("/raise/application")
    def raise_application(kind: str):
        errors = {
            "email": EmailAlreadyExistsError("El email ya está registrado"),
            "auth": AuthAlreadyExistsError("El usuario ya existe"),
            "credentials": InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            ),
            "provider": UnsupportedAuthProviderError(
                "El proveedor debe ser un proveedor OAuth"
            ),
            "user": UserNotFoundError("El usuario no existe"),
        }
        raise errors[kind]

    @app.post("/raise/domain")
    def raise_domain(kind: str):
        errors = {
            "email": InvalidEmailError("El email no es válido"),
            "identity": IdentityAlreadyExistsError("La identidad ya existe"),
            "username": UsernameAlreadyTakenError("Ese nombre ya está en uso"),
            "provider": InvalidAuthProviderError(
                "El proveedor de autenticación debe ser uno de los siguientes: EMAIL, GOOGLE"
            ),
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
        assert response.json()["detail"] == "El email ya está registrado"
        assert response.json()["code"] == "EMAIL_ALREADY_EXISTS"

    def test_auth_already_exists_is_409(self):
        response = _client().post("/raise/application?kind=auth")

        assert response.status_code == 409

    def test_invalid_credentials_are_401(self):
        response = _client().post("/raise/application?kind=credentials")

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

    def test_unsupported_provider_is_400(self):
        response = _client().post("/raise/application?kind=provider")

        assert response.status_code == 400

    def test_user_not_found_is_404(self):
        response = _client().post("/raise/application?kind=user")

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"

    def test_user_name_already_exists_is_409(self):
        response = _client().post("/raise/domain?kind=username")

        assert response.status_code == 409
        body = response.json()
        assert body.pop("request_id")
        assert body == {
            "detail": "Ese nombre ya está en uso",
            "code": "USERNAME_TAKEN",
            "field": "name",
        }

    def test_domain_error_is_400(self):
        response = _client().post("/raise/domain?kind=email")

        assert response.status_code == 400
        body = response.json()
        assert body.pop("request_id")
        assert body == {
            "detail": "El email no es válido",
            "code": "INVALID_EMAIL",
            "field": "email",
        }

    def test_domain_invalid_provider_is_400(self):
        response = _client().post("/raise/domain?kind=provider")

        assert response.status_code == 400

    def test_identity_already_exists_is_409(self):
        response = _client().post("/raise/domain?kind=identity")

        assert response.status_code == 409
        assert response.json()["detail"] == "La identidad ya existe"
        assert response.json()["code"] == "IDENTITY_ALREADY_EXISTS"

    def test_infrastructure_error_is_500(self, caplog):
        token = "secret-access-token"
        password = "Password123"
        request_id = "req-test-123"

        with caplog.at_level("ERROR", logger="ig.errors"):
            response = _client().post(
                "/raise/infrastructure",
                headers={
                    "Authorization": f"Bearer {token}",
                    REQUEST_ID_HEADER: request_id,
                },
                json={"password": password},
            )

        assert response.status_code == 500
        assert response.json()["detail"] == "Error al guardar el usuario"
        assert response.json()["code"] == "AUTH_CREATION"
        assert response.json()["request_id"] == request_id
        assert response.headers[REQUEST_ID_HEADER] == request_id
        assert any(
            getattr(record, "request_id", None) == request_id
            for record in caplog.records
        )
        assert "Traceback" in caplog.text
        assert "AuthCreationError" in caplog.text
        assert token not in caplog.text
        assert password not in caplog.text

    def test_invalid_body_is_422(self):
        response = _client().post("/raise/body", json={})

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "VALIDATION_ERROR"
        assert body["field"] == "email"
        assert body["detail"] == "Este campo es obligatorio"

    def test_unexpected_error_is_json(self):
        app = FastAPI()
        register_request_id(app)
        register_error_handlers(app)

        @app.get("/boom")
        def boom():
            raise TypeError("no debería verse")

        response = TestClient(app, raise_server_exceptions=False).get(
            "/boom",
            headers={REQUEST_ID_HEADER: "boom-1"},
        )

        assert response.status_code == 500
        assert response.headers[REQUEST_ID_HEADER] == "boom-1"
        assert response.json() == {
            "code": "INTERNAL_ERROR",
            "detail": "Error interno",
            "request_id": "boom-1",
        }
        assert "no debería verse" not in response.text
