from postgrest.exceptions import APIError

from core.auth.infrastructure.postgres_error import is_unique_violation


def test_postgres_unique_violation_is_duplicate():
    error = APIError({
        "code": "23505",
        "message": "llave duplicada viola restricción de unicidad",
    })

    assert is_unique_violation(error) is True


def test_message_with_already_registered_exists_is_not_duplicate():
    error = APIError({
        "code": "PGRST301",
        "message": "User already registered and the identity exists",
    })

    assert is_unique_violation(error) is False


def test_numeric_unique_violation_code_is_duplicate():
    error = APIError({
        "code": 23505,
        "message": "duplicate key value",
    })

    assert is_unique_violation(error) is True
