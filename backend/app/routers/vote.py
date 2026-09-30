from fastapi import APIRouter, HTTPException
from app.models import VoteRequest, VoteResultResponse, RoomStatus
from app.database import get_rooms_db

router = APIRouter()

def get_unique_most_voted(vote_counts: dict):
    """找出唯一得票最多的玩家，如果有并列最高票则返回None"""
    if not vote_counts:
        return None, 0
    
    # 按票数降序排列
    sorted_votes = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
    top_target = sorted_votes[0][0]
    top_count = sorted_votes[0][1]
    
    # 检查是否有并列最高票
    if len(sorted_votes) > 1 and sorted_votes[1][1] == top_count:
        # 有并列，不算投对
        print(f"[统计] 出现并列最高票: {top_count}票，有{sum(1 for v in sorted_votes if v[1] == top_count)}人并列")
        return None, top_count
    
    return top_target, top_count

@router.post("/room/{room_code}/vote")
async def vote(room_code: str, request: VoteRequest):
    """投票 - 投自己队伍的卧底"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    if room.status != RoomStatus.VOTING:
        raise HTTPException(status_code=400, detail="当前不在投票阶段")
    
    # 获取投票玩家
    voter = next((p for p in room.players if p.id == request.player_id), None)
    if not voter:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    # 获取被投玩家
    target = next((p for p in room.players if p.id == request.target_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="目标玩家不存在")
    
    # 验证：必须投自己队伍的玩家
    voter_team = "A" if voter.seat <= 5 else "B"
    target_team = "A" if target.seat <= 5 else "B"
    
    if voter_team != target_team:
        raise HTTPException(status_code=400, detail="必须投自己队伍的玩家")
    
    if target.id == voter.id:
        raise HTTPException(status_code=400, detail="不能投自己")
    
    # 记录投票 - 确保votes结构正确初始化
    if not room.votes or "votes" not in room.votes:
        room.votes = {"votes": {}}
    
    room.votes["votes"][request.player_id] = request.target_id
    
    print(f"[投票] {voter.name}({voter_team}队) 投了 {target.name}({target_team}队)")
    print(f"[投票] 当前已投票数: {len(room.votes['votes'])} / {len(room.players)}")
    
    # 检查是否所有人都投完了
    all_voted = len(room.votes["votes"]) >= len(room.players)
    
    if all_voted:
        print("[投票] 所有人已投票，开始统计结果")
        
        # 按队伍分组统计投票
        # team_a_votes: A队玩家投出的票，key=被投玩家ID，value=票数
        # team_b_votes: B队玩家投出的票
        team_a_votes = {}
        team_b_votes = {}
        
        for voter_id, target_id in room.votes["votes"].items():
            voter_player = next((p for p in room.players if p.id == voter_id), None)
            if voter_player:
                voter_t = "A" if voter_player.seat <= 5 else "B"
                if voter_t == "A":
                    team_a_votes[target_id] = team_a_votes.get(target_id, 0) + 1
                else:
                    team_b_votes[target_id] = team_b_votes.get(target_id, 0) + 1
        
        print(f"[统计] A队投票: {team_a_votes}")
        print(f"[统计] B队投票: {team_b_votes}")
        
        # 确定失败方和胜利方
        loser_team = "B" if room.winning_team == "A" else "A"
        winner_team = room.winning_team
        
        # 失败方投票结果 - 找出唯一得票最多的玩家
        loser_vote_counts = team_a_votes if loser_team == "A" else team_b_votes
        
        loser_most_voted = None
        loser_correct = False
        
        if loser_vote_counts:
            # 找出唯一得票最多的玩家ID（有并列则返回None）
            loser_most_voted, top_count = get_unique_most_voted(loser_vote_counts)
            
            if loser_most_voted:
                loser_most_voted_player = next((p for p in room.players if p.id == loser_most_voted), None)
                if loser_most_voted_player:
                    loser_correct = loser_most_voted_player.is_spy
                    print(f"[统计] 失败方({loser_team}队)投出: {loser_most_voted_player.name}, 是卧底={loser_correct}, 票数={top_count}")
                else:
                    loser_correct = False
                    print(f"[统计] 失败方({loser_team}队)投出的玩家不存在")
            else:
                # 并列最高票，判定投失败
                loser_correct = False
                print(f"[统计] 失败方({loser_team}队)出现并列最高票({top_count}票)，判定投失败")
        else:
            print(f"[统计] 失败方({loser_team}队)没有投票")
        
        room.votes["loser_vote_result"] = {
            "target": loser_most_voted,
            "correct": loser_correct
        }
        
        winner_most_voted = None
        winner_correct = False
        
        if loser_correct:
            # 失败方投对了，检查胜利方
            winner_vote_counts = team_a_votes if winner_team == "A" else team_b_votes
            
            if winner_vote_counts:
                winner_most_voted, top_count = get_unique_most_voted(winner_vote_counts)
                if winner_most_voted:
                    winner_most_voted_player = next((p for p in room.players if p.id == winner_most_voted), None)
                    if winner_most_voted_player:
                        winner_correct = winner_most_voted_player.is_spy
                        print(f"[统计] 胜利方({winner_team}队)投出: {winner_most_voted_player.name}, 是卧底={winner_correct}, 票数={top_count}")
                    else:
                        winner_correct = False
                else:
                    # 并列最高票，判定投失败
                    winner_correct = False
                    print(f"[统计] 胜利方({winner_team}队)出现并列最高票({top_count}票)，判定投失败")
            else:
                winner_correct = False
            
            room.votes["winner_vote_result"] = {
                "target": winner_most_voted,
                "correct": winner_correct
            }
            
            # 判定最终结果
            if winner_correct:
                room.final_result = "normal"
                print("[结果] 失败方投对 + 胜利方投对 → normal (胜利方胜)")
            else:
                room.final_result = "loser_win"
                print("[结果] 失败方投对 + 胜利方投错 → loser_win (失败方逆转)")
        else:
            # 失败方投错了，胜利方胜
            room.final_result = "normal"
            print("[结果] 失败方投错 → normal (胜利方胜)")
        
        print(f"[结果] winning_team={room.winning_team}, final_result={room.final_result}")
        room.status = RoomStatus.FINISHED
    
    return {
        "message": "投票成功",
        "all_voted": all_voted
    }

@router.get("/room/{room_code}/votes", response_model=VoteResultResponse)
async def get_vote_results(room_code: str):
    """获取投票结果"""
    rooms_db = get_rooms_db()
    
    if room_code not in rooms_db:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = rooms_db[room_code]
    
    result = VoteResultResponse()
    
    if room.votes and "loser_vote_result" in room.votes:
        result.loser_vote = room.votes["loser_vote_result"]["target"]
        result.loser_correct = room.votes["loser_vote_result"]["correct"]
    
    if room.votes and "winner_vote_result" in room.votes:
        result.winner_vote = room.votes["winner_vote_result"]["target"]
        result.winner_correct = room.votes["winner_vote_result"]["correct"]
    
    return result
