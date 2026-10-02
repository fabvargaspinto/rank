"""Borra conexiones de Instagram cuyo owner ya no existe en public.users.

Uso (una vez, o como job de reconciliación):

    cd backend && uv run python purge_orphan_instagram_connections.py
"""

from __future__ import annotations

from api.dependencies.container import get_dependency_container
from core.instagram.application.disconnect_instagram import DisconnectInstagram


def main() -> None:
    container = get_dependency_container()
    wiring = container._instagram_wiring()  # noqa: SLF001
    disconnect = DisconnectInstagram(wiring.connections, wiring.snapshots)
    supabase = container.db_client.get_db()

    removed = 0
    kept = 0
    for stored in wiring.connections.list_all():
        owner_id = stored.connection.owner_user_id.value
        existing = (
            supabase.table("users")
            .select("id")
            .eq("id", owner_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            kept += 1
            continue
        disconnect.execute(owner_id)
        removed += 1
        print(f"removed owner_user_id={owner_id}")

    print(f"removed={removed} kept={kept}")


if __name__ == "__main__":
    main()
