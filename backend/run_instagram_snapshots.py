from api.dependencies.container import get_dependency_container


def main() -> None:
    result = get_dependency_container().capture_instagram_followers().execute_all()
    print(f"captured={result.captured} failed={result.failed}")


if __name__ == "__main__":
    main()
