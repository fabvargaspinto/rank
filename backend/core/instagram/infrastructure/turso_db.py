from __future__ import annotations

from typing import Any

import httpx

from core.instagram.infrastructure.error_infrastructure import InstagramDbError
from core.instagram.infrastructure.sql import SCHEMA_STATEMENTS


def turso_pipeline_url(database_url: str) -> str:
    url = database_url.strip()
    if url.startswith("libsql://"):
        url = "https://" + url.removeprefix("libsql://")
    return url.rstrip("/") + "/v2/pipeline"


def _wire_value(value: object) -> dict[str, object]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        return {"type": "float", "value": str(value)}
    return {"type": "text", "value": str(value)}


def _unwrap_value(cell: object) -> object:
    if not isinstance(cell, dict):
        return cell
    cell_type = cell.get("type")
    if cell_type == "null":
        return None
    if cell_type == "integer":
        raw = cell.get("value")
        return int(raw) if raw is not None else None
    if cell_type == "float":
        raw = cell.get("value")
        return float(raw) if raw is not None else None
    return cell.get("value")


class TursoHttpDatabase:
    def __init__(
        self,
        database_url: str,
        auth_token: str,
        http: httpx.Client | None = None,
    ) -> None:
        self._url = turso_pipeline_url(database_url)
        self._token = auth_token
        self._http = http or httpx.Client(timeout=15.0)
        self._owns_http = http is None
        self.ensure_schema()

    def ensure_schema(self) -> None:
        requests = [
            {"type": "execute", "stmt": {"sql": statement.strip()}}
            for statement in SCHEMA_STATEMENTS
        ]
        requests.append({"type": "close"})
        self._pipeline(requests)

    def execute(
        self,
        sql: str,
        params: tuple[object, ...] = (),
    ) -> list[dict[str, object]]:
        stmt: dict[str, object] = {"sql": sql}
        if params:
            stmt["args"] = [_wire_value(param) for param in params]
        payload = self._pipeline(
            [
                {"type": "execute", "stmt": stmt},
                {"type": "close"},
            ]
        )
        return self._rows(payload)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def _pipeline(self, requests: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            response = self._http.post(
                self._url,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                json={"requests": requests},
            )
        except httpx.HTTPError as exc:
            raise InstagramDbError("No se pudo conectar con Turso") from exc

        if response.status_code >= 400:
            raise InstagramDbError("No se pudo guardar los datos de Instagram")

        try:
            payload = response.json()
        except ValueError as exc:
            raise InstagramDbError("No se pudo guardar los datos de Instagram") from exc

        if not isinstance(payload, dict):
            raise InstagramDbError("No se pudo guardar los datos de Instagram")

        for result in payload.get("results") or []:
            if isinstance(result, dict) and result.get("type") == "error":
                raise InstagramDbError("No se pudo guardar los datos de Instagram")
        return payload

    def _rows(self, payload: dict[str, Any]) -> list[dict[str, object]]:
        results = payload.get("results") or []
        if not results or not isinstance(results[0], dict):
            return []
        first = results[0]
        response = first.get("response") or {}
        if not isinstance(response, dict):
            return []
        result = response.get("result") or {}
        if not isinstance(result, dict):
            return []
        cols = result.get("cols") or []
        names = [
            str(col.get("name"))
            for col in cols
            if isinstance(col, dict) and col.get("name")
        ]
        rows: list[dict[str, object]] = []
        for raw_row in result.get("rows") or []:
            if not isinstance(raw_row, list):
                continue
            rows.append(
                {
                    name: _unwrap_value(raw_row[index] if index < len(raw_row) else None)
                    for index, name in enumerate(names)
                }
            )
        return rows
