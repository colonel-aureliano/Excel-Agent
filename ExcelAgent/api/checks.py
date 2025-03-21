from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", tags=["Health Check"])
async def health():
    return JSONResponse(content={"status": 200})
