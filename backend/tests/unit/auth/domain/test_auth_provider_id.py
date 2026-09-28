import pytest

from core.auth.domain.auth_error import InvalidAuthProviderIdError
from core.auth.domain.auth_provider_id import AuthProviderId


class TestAuthProviderId:
    def test_should_keep_provider_id(self):
        provider_id = AuthProviderId("  google-123  ")

        assert provider_id.value == "google-123"

    def test_should_reject_empty_provider_id(self):
        with pytest.raises(InvalidAuthProviderIdError):
            AuthProviderId("")

        with pytest.raises(InvalidAuthProviderIdError):
            AuthProviderId("   ")
