"""Borra conexiones de Instagram cuyo owner ya no existe en public.users.

Por defecto solo muestra qué borraría (dry-run). Para aplicar:

    docker compose exec backend python purge_orphan_instagram_connections.py --apply

Si más del 20 % de las conexiones parecen huérfanas, aborta: suele indicar
que Supabase y Turso no son del mismo entorno.
"""

from __future__ import annotations

import argparse
import sys

from api.dependencies.container import get_dependency_container
from config.turso_settings import TursoSettings, is_sqlite_url
from core.instagram.application.disconnect_instagram import DisconnectInstagram

ORPHAN_ABORT_RATIO = 0.20


def orphan_ratio_exceeds_limit(
    orphan_count: int,
    total: int,
    *,
    limit: float = ORPHAN_ABORT_RATIO,
) -> bool:
    if total <= 0:
        return False
    return (orphan_count / total) > limit


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Purga conexiones de Instagram huérfanas. "
            "Dry-run por defecto; pasá --apply para borrar."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ejecuta los borrados. Sin este flag solo informa.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    turso = TursoSettings()
    print(f"turso_url={turso.turso_database_url.strip()}")
    if not is_sqlite_url(turso.turso_database_url):
        print(
            "Aviso: Turso remoto. Confirmá que SUPABASE_URL es del mismo entorno.",
            file=sys.stderr,
        )

    container = get_dependency_container()
    wiring = container._instagram_wiring()  # noqa: SLF001
    disconnect = DisconnectInstagram(wiring.connections, wiring.snapshots)
    supabase = container.db_client.get_db()

    stored_all = list(wiring.connections.list_all())
    total = len(stored_all)
    orphan_ids: list[str] = []
    kept = 0

    for stored in stored_all:
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
        orphan_ids.append(owner_id)

    orphan_count = len(orphan_ids)
    ratio = (orphan_count / total) if total else 0.0
    mode = "apply" if args.apply else "dry-run"
    print(
        f"mode={mode} total={total} orphan={orphan_count} "
        f"kept={kept} orphan_ratio={ratio:.1%}"
    )

    if orphan_ratio_exceeds_limit(orphan_count, total):
        print(
            f"Abortado: {ratio:.1%} huérfanas supera el tope "
            f"({ORPHAN_ABORT_RATIO:.0%}). Revisá que Supabase y Turso "
            "sean del mismo entorno.",
            file=sys.stderr,
        )
        return 2

    if not args.apply:
        for owner_id in orphan_ids:
            print(f"would_remove owner_user_id={owner_id}")
        if orphan_count:
            print(
                "Dry-run: no se borró nada. "
                "Para aplicar: docker compose exec backend "
                "python purge_orphan_instagram_connections.py --apply"
            )
        return 0

    removed = 0
    for owner_id in orphan_ids:
        disconnect.execute(owner_id)
        removed += 1
        print(f"removed owner_user_id={owner_id}")

    print(f"removed={removed} kept={kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
