import pytest

from core.user.domain.user_error import InvalidUserLinkSortIndexError
from core.user.domain.user_link_sort_index import UserLinkSortIndex


class TestUserLinkSortIndex:

    def test_should_create_valid_sort_index(self):
        sort_index = UserLinkSortIndex(2)

        assert sort_index.value == 2

    def test_should_accept_minimum_sort_index(self):
        sort_index = UserLinkSortIndex(0)

        assert sort_index.value == 0

    def test_should_accept_maximum_sort_index(self):
        sort_index = UserLinkSortIndex(5)

        assert sort_index.value == 5

    def test_should_reject_negative_sort_index(self):
        with pytest.raises(InvalidUserLinkSortIndexError):
            UserLinkSortIndex(-1)

    def test_should_reject_sort_index_greater_than_five(self):
        with pytest.raises(InvalidUserLinkSortIndexError):
            UserLinkSortIndex(6)

    def test_should_reject_boolean_sort_index(self):
        with pytest.raises(InvalidUserLinkSortIndexError):
            UserLinkSortIndex(True)

        with pytest.raises(InvalidUserLinkSortIndexError):
            UserLinkSortIndex(False)
