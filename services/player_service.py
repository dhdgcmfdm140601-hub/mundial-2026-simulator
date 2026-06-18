from repositories.player_repository import PlayerRepository
from repositories.team_repository import TeamRepository
from schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session

MAX_PLAYERS_PER_TEAM = 23


class PlayerService:
    def __init__(self, db: Session):
        self.repo = PlayerRepository(db)
        self.team_repo = TeamRepository(db)

    @staticmethod
    def _require_non_empty(value: str, field: str):
        if not value or not value.strip():
            raise HTTPException(status_code=400, detail=f"{field} must not be empty")

    def get_all(self, team_id: int | None = None) -> list[PlayerResponse]:
        return [PlayerResponse.model_validate(p) for p in self.repo.get_all(team_id)]

    def get_by_id(self, player_id: int) -> PlayerResponse:
        player = self.repo.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return PlayerResponse.model_validate(player)

    def create(self, data: PlayerCreate) -> PlayerResponse:
        self._require_non_empty(data.name, "Player name")
        team = self.team_repo.get_by_id(data.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if self.repo.count_by_team(data.team_id) >= MAX_PLAYERS_PER_TEAM:
            raise HTTPException(status_code=400, detail=f"Team cannot have more than {MAX_PLAYERS_PER_TEAM} players")
        valid_positions = {"GK", "DF", "MF", "FW"}
        if data.position.upper() not in valid_positions:
            raise HTTPException(status_code=400, detail=f"Position must be one of {valid_positions}")
        if self.repo.get_by_name_and_team(data.name, data.team_id):
            raise HTTPException(status_code=409, detail="Player already exists in this team")
        player_data = data.model_copy(update={"position": data.position.upper()})
        player = self.repo.create(player_data)
        return PlayerResponse.model_validate(player)

    def update(self, player_id: int, data: PlayerUpdate) -> PlayerResponse:
        player = self.repo.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if "name" in update_data:
            self._require_non_empty(update_data["name"], "Player name")
        if "team_id" in update_data:
            team = self.team_repo.get_by_id(update_data["team_id"])
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            if self.repo.count_by_team(update_data["team_id"]) >= MAX_PLAYERS_PER_TEAM:
                raise HTTPException(status_code=400, detail=f"Team cannot have more than {MAX_PLAYERS_PER_TEAM} players")
        if "position" in update_data:
            valid_positions = {"GK", "DF", "MF", "FW"}
            if update_data["position"].upper() not in valid_positions:
                raise HTTPException(status_code=400, detail=f"Position must be one of {valid_positions}")
            update_data["position"] = update_data["position"].upper()
        if "name" in update_data or "team_id" in update_data:
            final_name = update_data.get("name", player.name)
            final_team_id = update_data.get("team_id", player.team_id)
            existing = self.repo.get_by_name_and_team(final_name, final_team_id)
            if existing and existing.id != player_id:
                raise HTTPException(status_code=409, detail="Player already exists in this team")
        player = self.repo.update(player, update_data)
        return PlayerResponse.model_validate(player)

    def delete(self, player_id: int) -> None:
        player = self.repo.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        self.repo.delete(player)