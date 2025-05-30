from fastapi import APIRouter

router = APIRouter()

@router.get("/_status")
async def health_check():
    return {"status": "healthy"}
