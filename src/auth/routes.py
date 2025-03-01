from fastapi import APIRouter

auth_router = APIRouter()


@auth_router.get("/")
async def me_url():
    return "Success"
