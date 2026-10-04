from api.dependencies.container import get_dependency_container


def main() -> int:
    result = get_dependency_container().capture_instagram_followers().execute_all()
    print(
        f"captured={result.captured} failed={result.failed} "
        f"needs_reconnect={result.needs_reconnect}"
    )
    return 1 if result.failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
