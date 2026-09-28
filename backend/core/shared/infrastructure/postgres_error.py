from postgrest.exceptions import APIError

UNIQUE_VIOLATION = "23505"


def is_unique_violation(error: APIError) -> bool:
    return str(error.code) == UNIQUE_VIOLATION
