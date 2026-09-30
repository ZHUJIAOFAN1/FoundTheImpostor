from fastapi import APIRouter, HTTPException
from app.models import (
    CreateRoomRequest, JoinRoomRequest, RoomResponse, JoinRoomResponse,
    SubmitResultRequest, RoomStatus, Player, Room
)
from app.database import get_rooms_db
import random
import string
import uuid

router = APIRouter()

def generate_room_code():
    """生成6位房间码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_player_id():
    """生成玩家ID"""
    return str(uuid.uuid4())[:8]

@router.post("/room", response_model=RoomResponse)
async def create_room(request: CreateRoomRequest):
    """创建房间"""
    rooms_db = get_rooms_db()
    
    room_code = generate_room_code()
    host_id = generate_player_id()
    
    # 创建房主玩家
    host_player = Player(
        id=host_id,
        name=request.host_name,
        seat=1,  # 房主默认1号位
        is_spy=False,
        is_ready=True
    )
    
    # 创建房间
    room = Room(
        room_code=room_code,
        host_id=host_id,
        host_name=request.host_name,
        players=[host_player],
        status=RoomStatus.WAITING
    )
    
    rooms_db[room_code] = room
    
    return RoomResponse(
        room_code=room.room_code,
        host_id=room.host_id,
        status=room.status,
        players=room.players
    )

@router.get("/room/{room_code}", response_model=RoomResponse)
async def get_room(room_code: str):
    """获取房间信息"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    return RoomResponse(
        room_code=room.room_code,
        host_id=room.host_id,
        status=room.status,
        players=room.players,
        winning_team=room.winning_team,
        final_result=room.final_result,
        votes=room.votes
    )

@router.post("/room/{room_code}/join", response_model=JoinRoomResponse)
async def join_room(room_code: str, request: JoinRoomRequest):
    """加入房间"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    if room.status != RoomStatus.WAITING:
        raise HTTPException(status_code=400, detail="游戏已开始，无法加入")
    
    if len(room.players) >= 10:
        raise HTTPException(status_code=400, detail="房间已满")
    
    # 分配座位
    taken_seats = {p.seat for p in room.players}
    available_seats = [s for s in range(1, 11) if s not in taken_seats]
    
    if not available_seats:
        raise HTTPException(status_code=400, detail="没有可用座位")
    
    seat = random.choice(available_seats)
    player_id = generate_player_id()
    
    new_player = Player(
        id=player_id,
        name=request.player_name,
        seat=seat,
        is_spy=False,
        is_ready=True
    )
    
    room.players.append(new_player)
    
    return JoinRoomResponse(player_id=player_id, seat=seat, host_id=room.host_id)

@router.post("/room/{room_code}/swap-seat")
async def swap_seat(room_code: str, request: dict):
    """换位"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    if room.status != RoomStatus.WAITING:
        raise HTTPException(status_code=400, detail="游戏已开始，无法换位")
    
    player_id = request.get("player_id")
    target_seat = request.get("target_seat")
    
    # 获取当前玩家
    player = next((p for p in room.players if p.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    # 检查目标座位是否有效
    if target_seat < 1 or target_seat > 10:
        raise HTTPException(status_code=400, detail="座位号无效")
    
    # 获取目标座位的玩家
    target_player = next((p for p in room.players if p.seat == target_seat), None)
    
    if target_player:
        # 和目标座位的玩家换位
        player.seat, target_player.seat = target_player.seat, player.seat
    else:
        # 目标座位为空，直接移动
        player.seat = target_seat
    
    return {"message": "换位成功", "player_id": player_id, "new_seat": player.seat}

@router.post("/room/{room_code}/leave")
async def leave_room(room_code: str, request: dict):
    """离开房间 - 房主离开则关闭房间"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    player_id = request.get("player_id")
    
    # 如果是房主，删除整个房间
    if player_id == room.host_id:
        del rooms_db[room_code]
        return {"message": "房间已关闭", "closed": True}
    
    # 普通玩家离开
    room.players = [p for p in room.players if p.id != player_id]
    return {"message": "已离开房间", "closed": False}

@router.post("/room/{room_code}/start")
async def start_game(room_code: str):
    """开始游戏 - 分配卧底"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    if room.status != RoomStatus.WAITING:
        raise HTTPException(status_code=400, detail="游戏已开始")
    
    if len(room.players) < 2:
        raise HTTPException(status_code=400, detail="至少需要2名玩家才能开始")
    
    # 检查队伍人数
    team_a_count = len([p for p in room.players if 1 <= p.seat <= 5])
    team_b_count = len([p for p in room.players if 6 <= p.seat <= 10])
    
    # 随机分配卧底
    # 先重置所有玩家卧底状态
    for p in room.players:
        p.is_spy = False
    
    # A队(1-5号)随机选一个卧底
    team_a_players = [p for p in room.players if 1 <= p.seat <= 5]
    if team_a_players:
        spy_a = random.choice(team_a_players)
        spy_a.is_spy = True
        room.spy_a = spy_a.seat
        print(f"[开始] A队卧底: {spy_a.name} (座位{spy_a.seat})")
    
    # B队(6-10号)随机选一个卧底
    team_b_players = [p for p in room.players if 6 <= p.seat <= 10]
    if team_b_players:
        spy_b = random.choice(team_b_players)
        spy_b.is_spy = True
        room.spy_b = spy_b.seat
        print(f"[开始] B队卧底: {spy_b.name} (座位{spy_b.seat})")
    
    # 初始化投票数据
    room.votes = {"votes": {}}
    
    # 更新状态为playing（身份分配阶段）
    room.status = RoomStatus.PLAYING
    
    return {
        "message": "游戏开始",
        "spy_a": room.spy_a,
        "spy_b": room.spy_b
    }

@router.post("/room/{room_code}/ready")
async def player_ready(room_code: str, player_id: str):
    """玩家确认身份，准备开始游戏"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    player = next((p for p in room.players if p.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    player.is_ready = True
    
    # 检查所有玩家是否都准备完毕
    all_ready = all(p.is_ready for p in room.players)
    
    # 如果是房主确认，且房间人数少于10人（测试模式），直接开始游戏
    is_host = (player_id == room.host_id)
    if is_host and len(room.players) < 10:
        room.status = RoomStatus.GAMING
    elif all_ready:
        room.status = RoomStatus.GAMING
    
    return {"message": "准备就绪", "all_ready": all_ready}

@router.post("/room/{room_code}/result")
async def submit_result(room_code: str, request: SubmitResultRequest):
    """提交游戏结果"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    if room.status != RoomStatus.GAMING:
        raise HTTPException(status_code=400, detail="游戏未在进行")
    
    room.winning_team = request.winning_team
    room.status = RoomStatus.VOTING
    
    return {
        "message": "结果已提交",
        "winning_team": request.winning_team,
        "status": "进入投票环节"
    }

@router.post("/room/{room_code}/reset")
async def reset_room(room_code: str, request: dict):
    """重置房间 - 回到等待大厅，再来一局"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    player_id = request.get("player_id")
    
    # 只有房主可以重置
    if player_id != room.host_id:
        raise HTTPException(status_code=403, detail="只有房主可以重置房间")
    
    # 重置房间状态
    room.status = RoomStatus.WAITING
    room.winning_team = None
    room.final_result = None
    room.votes = {"votes": {}}
    room.spy_a = None
    room.spy_b = None
    
    # 重置所有玩家状态
    for p in room.players:
        p.is_spy = False
        p.is_ready = True
    
    return {"message": "房间已重置", "room_code": room_code}
