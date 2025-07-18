from fastapi import APIRouter

router = APIRouter(
    prefix="/token",
    tags=["token"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)