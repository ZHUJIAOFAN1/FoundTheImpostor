from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RoomStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    GAMING = "gaming"
    VOTING = "voting"
    FINISHED = "finished"

class Player(BaseModel):
    id: str
    name: str
    seat: int
    is_spy: bool = False
    is_ready: bool = False

class Room(BaseModel):
    room_code: str
    host_id: str
    host_name: str
    players: List[Player] = []
    status: RoomStatus = RoomStatus.WAITING
    team_a: List[int] = [1, 2, 3, 4, 5]
    team_b: List[int] = [6, 7, 8, 9, 10]
    spy_a: Optional[int] = None  # A队卧底座位号
    spy_b: Optional[int] = None  # B队卧底座位号
    winning_team: Optional[str] = None  # "A" or "B"
    final_result: Optional[str] = None  # "normal" or "loser_win"
    votes: dict = Field(default_factory=dict)  # 投票记录
    created_at: datetime = Field(default_factory=datetime.now)

class CreateRoomRequest(BaseModel):
    host_name: str

class JoinRoomRequest(BaseModel):
    player_name: str

class RoomResponse(BaseModel):
    room_code: str
    host_id: str
    status: RoomStatus
    players: List[Player]
    winning_team: Optional[str] = None
    final_result: Optional[str] = None
    votes: Optional[dict] = None

class JoinRoomResponse(BaseModel):
    player_id: str
    seat: int
    host_id: str

class SubmitResultRequest(BaseModel):
    winning_team: str  # "A" or "B"

class VoteRequest(BaseModel):
    player_id: str
    target_id: str

class SpyVoteRequest(BaseModel):
    player_id: str
    target_id: str

class VoteResultResponse(BaseModel):
    loser_vote: Optional[str] = None  # 失败方投出的卧底
    loser_correct: Optional[bool] = None
    winner_vote: Optional[str] = None  # 胜利方投出的卧底
    winner_correct: Optional[bool] = None
