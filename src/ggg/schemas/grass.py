from datetime import datetime

from ggg.schemas.base import GggBaseModel


class GrassBase(GggBaseModel):
    grass_id: int
    commit_id: int
    coord_id: int
    map_id: int

class CommitBase(GggBaseModel):
    commit_id: int
    pnu: int
    user_id: int
    created_at: datetime