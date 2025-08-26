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
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
    ):

    commits = (
        db.query(Commit)
        .filter(Commit.user_id == user_id)
        .order_by(Commit.created_at.desc())
        .limit(limit)
        .all()
    )

    if not commits:
        return CommitResponse(commits=[])

    response_commits = []
    for commit in commits:
      
        place = db.query(Place).filter(Place.pnu == commit.pnu).first()
        place_name = place.name if place else None
        pnu = place.pnu if place else None

        commit_data = CommitData(
            commit_id=commit.commit_id,
            created_at=commit.created_at,
            pnu=pnu,
            place_name=place_name
        )
        response_commits.append(commit_data)

    return CommitResponse(commits=response_commits)
