from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ggg.database import get_db
from ggg.exception import ExpiredTokenException, ValidTokenException, ForbiddenInvalidTokenException
from ggg.models import Token
from ggg.schemas.oauth import AuthHandler, AUTHORIZATION_HEADER

router = APIRouter(
    prefix="/token",
    tags=["token"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get('/update', response_model=str, include_in_schema=False)
async def auth(
    token: str = Depends(AUTHORIZATION_HEADER),
    db: Session = Depends(get_db)
):
    auth_handler = AuthHandler()
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        auth_handler.decode_token(token)
        raise ValidTokenException()
    except ValidTokenException as e:
        raise e
    except ExpiredTokenException:
        pass
    except Exception as e:
        raise ForbiddenInvalidTokenException()
    
    try:
        user_id = auth_handler.decode_token(token, verify_exp=False)
    except Exception:
        raise ForbiddenInvalidTokenException()
    
    token_row = Token.find_by_userid(db, user_id)
    if not token_row:
        raise ForbiddenInvalidTokenException()
    try:
        refresh_sub = auth_handler.decode_token(token_row.refresh_token)
        if refresh_sub != f"{user_id}.refresh":
            raise ForbiddenInvalidTokenException()
    except Exception as e:
        raise ForbiddenInvalidTokenException()

    new_access_token = auth_handler.create_access_token(user_id)
    return new_access_token