from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from dependencies import SupabaseClientDep
from core.share.infraestructure.infra_error import DatabaseError

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
def health(supabase_client: SupabaseClientDep):
    try:
        supabase_client.check_connection()
    except DatabaseError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "disconnected"},
        )

    return {"status": "ok", "database": "connected"}
