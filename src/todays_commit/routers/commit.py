from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from todays_commit.database import get_db
from todays_commit.models import Commit, Place
from todays_commit.schemas.oauth import auth_check
from todays_commit.schemas.commit import CommitData, CommitResponse


router = APIRouter(
    prefix="/commit",
    tags=["commit"],
    dependencies=[Depends(auth_check)],
    responses={404: {"description": "Not found"}},
)


@router.get("/mycommit", response_model=CommitResponse)
async def get_my_commit( 
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db),
    cursor: int = Query(9_999_999_999_999, description="이전 페이지의 마지막 commit_id"),
    limit: int = Query(10, ge=1, le=100, description="한 페이지당 가져올 커밋 수"),
    ):

    rows = (
        db.query(
            Commit.commit_id,
            Commit.created_at,
            Commit.pnu,
            Place.name.label("place_name")
        )
        .outerjoin(Place, Place.pnu == Commit.pnu)
        .filter(Commit.user_id == user_id)
        .filter(Commit.commit_id < cursor)
        .order_by(Commit.commit_id.desc())
        .limit(limit)
        .all()
    )

    if not rows:
        return CommitResponse(commits=[], next_cursor=None)

    response_commits = [
        CommitData(
            commit_id=row.commit_id,
            created_at=row.created_at,
            pnu=row.pnu,
            place_name=row.place_name,
        )
        for row in rows
    ]

    next_cursor = rows[-1].commit_id if len(rows) == limit else None

    return CommitResponse(commits=response_commits, next_cursor=next_cursor)
