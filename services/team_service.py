from repositories.team_repository import TeamRepository
from schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamWithPlayers
from schemas.player import PlayerResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session


class TeamService:
    def __init__(self, db: Session):
        self.repo = TeamRepository(db)

    def get_all(self) -> list[TeamResponse]:
        return [TeamResponse.model_validate(t) for t in self.repo.get_all()]

    def get_by_id(self, team_id: int) -> TeamWithPlayers:
        team = self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        result = TeamWithPlayers.model_validate(team)
        result.players = [PlayerResponse.model_validate(p) for p in team.players]
        return result

    def _validate_code(self, code: str) -> str:
        code = code.upper()
        if not code.isalpha() or len(code) != 3:
            raise HTTPException(status_code=400, detail="Team code must be exactly 3 letters")
        return code

    def _validate_name(self, name: str, field: str = "Name"):
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail=f"{field} must not be empty")

    def create(self, data: TeamCreate) -> TeamResponse:
        self._validate_name(data.name, "Team name")
        code = self._validate_code(data.code)
        if self.repo.get_by_code(code):
            raise HTTPException(status_code=409, detail="Team code already exists")
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="Team name already exists")
        team = self.repo.create(data)
        return TeamResponse.model_validate(team)

    def update(self, team_id: int, data: TeamUpdate) -> TeamResponse:
        team = self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if "code" in update_data:
            code = self._validate_code(update_data["code"])
            existing = self.repo.get_by_code(code)
            if existing and existing.id != team_id:
                raise HTTPException(status_code=409, detail="Team code already exists")
            update_data["code"] = code
        if "name" in update_data:
            self._validate_name(update_data["name"], "Team name")
            existing = self.repo.get_by_name(update_data["name"])
            if existing and existing.id != team_id:
                raise HTTPException(status_code=409, detail="Team name already exists")
        team = self.repo.update(team, update_data)
        return TeamResponse.model_validate(team)

    def delete(self, team_id: int) -> None:
        team = self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        self.repo.delete(team)