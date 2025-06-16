from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok", "message": "Yeaaaahhhh it's running !"})
