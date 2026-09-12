from db.db_client import DBClient


def test_service_role_can_call_auth_admin(db_client: DBClient) -> None:
    users = db_client.get_db().auth.admin.list_users(page=1, per_page=1)

    assert isinstance(users, list)
