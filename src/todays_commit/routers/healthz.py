from fastapi import APIRouter

router = APIRouter(
    prefix="/healthz",
    tags=["healthz"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def health_check():
    return {"ok": True}