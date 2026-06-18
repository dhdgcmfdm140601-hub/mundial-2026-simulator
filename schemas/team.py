from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TeamCreate(BaseModel):
    name: str
    code: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    code: str
    group_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamWithPlayers(TeamResponse):
    players: list["PlayerResponse"] = []

    model_config = ConfigDict(from_attributes=True)


from schemas.player import PlayerResponse
TeamWithPlayers.model_rebuild()
