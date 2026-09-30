import axios from 'axios'

// 本地开发用 /api 代理，生产环境用环境变量指向后端
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: baseURL,
  timeout: 10000
})

export default {
  // 房间相关
  createRoom(hostName) {
    return api.post('/room', { host_name: hostName })
  },
  
  getRoom(roomCode) {
    return api.get(`/room/${roomCode}`)
  },
  
  joinRoom(roomCode, playerName) {
    return api.post(`/room/${roomCode}/join`, { player_name: playerName })
  },
  
  startGame(roomCode) {
    return api.post(`/room/${roomCode}/start`)
  },
  
  playerReady(roomCode, playerId) {
    return api.post(`/room/${roomCode}/ready`, null, { params: { player_id: playerId } })
  },
  
  swapSeat(roomCode, playerId, targetSeat) {
    return api.post(`/room/${roomCode}/swap-seat`, { 
      player_id: playerId, 
      target_seat: targetSeat 
    })
  },
  
  leaveRoom(roomCode, playerId) {
    return api.post(`/room/${roomCode}/leave`, { player_id: playerId })
  },
  
  resetRoom(roomCode, playerId) {
    return api.post(`/room/${roomCode}/reset`, { player_id: playerId })
  },
  
  submitResult(roomCode, winningTeam) {
    return api.post(`/room/${roomCode}/result`, { winning_team: winningTeam })
  },
  
  // 玩家相关
  checkIdentity(roomCode, playerId) {
    return api.get(`/room/${roomCode}/identity/${playerId}`)
  },
  
  // 投票相关
  vote(roomCode, playerId, targetId) {
    return api.post(`/room/${roomCode}/vote`, { 
      player_id: playerId, 
      target_id: targetId 
    })
  },
  
  getVoteResult(roomCode) {
    return api.get(`/room/${roomCode}/votes`)
  }
}
