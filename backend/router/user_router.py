from fastapi import APIRouter
from dependencies import UserSupabaseRepoDep
from core.user.application.verify_user_name_use_case import VerifyUserNameUseCase
from fastapi.responses import JSONResponse
from pydantic import BaseModel
user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

class VerifyUserNameRequest(BaseModel):
    name: str


@user_router.post("/verify-name")
async def verify_user_name(
    data: VerifyUserNameRequest,
    user_supabase_repo: UserSupabaseRepoDep,
) -> JSONResponse:
    print(f"user_router: request received with data: {data}")
    try:
    
        verify_user_name_use_case = VerifyUserNameUseCase(user_supabase_repo=user_supabase_repo)
        verify_user_name_use_case.execute(data.name)
        
        print(f"user_router: VerifyUserNameUseCase executed successfully")
        return JSONResponse(content={"message": "nombre verificado correctamente", "isError": False}, status_code=200)
    except Exception as e:
        print(f"user_router: Error in verify user name: {e}")
        return JSONResponse(content={"message": str(e), "isError": True}, status_code=400)
