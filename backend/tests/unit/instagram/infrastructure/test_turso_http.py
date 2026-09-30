import httpx

from core.instagram.infrastructure.turso_db import TursoHttpDatabase, turso_pipeline_url


def test_converts_libsql_url_to_https_pipeline():
    assert (
        turso_pipeline_url("libsql://socials-org.turso.io")
        == "https://socials-org.turso.io/v2/pipeline"
    )


def test_execute_maps_pipeline_rows():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "type": "ok",
                        "response": {
                            "type": "execute",
                            "result": {
                                "cols": [{"name": "id", "decltype": "TEXT"}],
                                "rows": [[{"type": "text", "value": "abc"}]],
                            },
                        },
                    },
                    {"type": "ok", "response": {"type": "close"}},
                ]
            },
        )

    db = TursoHttpDatabase(
        "https://example.turso.io",
        "token",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    rows = db.execute("SELECT id FROM instagram_connections")

    assert rows == [{"id": "abc"}]
