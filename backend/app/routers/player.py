from fastapi import APIRouter, HTTPException
from app.models import Player
from app.database import get_rooms_db

router = APIRouter()

@router.get("/room/{room_code}/identity/{player_id}")
async def check_identity(room_code: str, player_id: str):
    """查看玩家身份"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    player = next((p for p in room.players if p.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    # 确定玩家队伍
    team = "A" if player.seat <= 5 else "B"
    
    # 获取队友
    if team == "A":
        teammates = [p for p in room.players if 1 <= p.seat <= 5 and p.id != player_id]
    else:
        teammates = [p for p in room.players if 6 <= p.seat <= 10 and p.id != player_id]
    
    return {
        "player_id": player_id,
        "name": player.name,
        "seat": player.seat,
        "team": team,
        "is_spy": player.is_spy,
        "teammates": [{"id": t.id, "name": t.name, "seat": t.seat} for t in teammates]
    }

@router.get("/room/{room_code}/players")
async def get_players(room_code: str):
    """获取房间所有玩家"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    return {
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "seat": p.seat,
                "team": "A" if p.seat <= 5 else "B"
            }
            for p in room.players
        ]
    }
