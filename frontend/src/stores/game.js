import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  const roomCode = ref('')
  const playerId = ref('')
  const playerName = ref('')
  const roomStatus = ref('waiting') // waiting, playing, gaming, voting, finished
  const players = ref([])
  const hostId = ref('')
  const myTeam = ref(null) // 'A' or 'B'
  const isSpy = ref(false)
  const winningTeam = ref(null)
  const finalResult = ref(null)
  const voteResults = ref(null)

  const isHost = computed(() => playerId.value === hostId.value)

  const setPlayerInfo = (code, id, name) => {
    roomCode.value = code
    playerId.value = id
    playerName.value = name
  }

  const setRoomData = (data) => {
    roomStatus.value = data.status
    players.value = data.players || []
    hostId.value = data.host_id
    
    // 设置玩家队伍和卧底信息
    const myPlayer = players.value.find(p => p.id === playerId.value)
    if (myPlayer) {
      myTeam.value = myPlayer.seat <= 5 ? 'A' : 'B'
      isSpy.value = myPlayer.is_spy || false
    }
    
    if (data.winning_team) {
      winningTeam.value = data.winning_team
    }
    if (data.final_result) {
      finalResult.value = data.final_result
    }
    // 保存投票结果
    if (data.votes) {
      voteResults.value = {
        votes: data.votes.votes || {},
        loser_vote_result: data.votes.loser_vote_result || null,
        winner_vote_result: data.votes.winner_vote_result || null
      }
    }
  }

  const reset = () => {
    roomCode.value = ''
    playerId.value = ''
    playerName.value = ''
    roomStatus.value = 'waiting'
    players.value = []
    hostId.value = ''
    myTeam.value = null
    isSpy.value = false
    winningTeam.value = null
    finalResult.value = null
    voteResults.value = null
  }

  return {
    roomCode,
    playerId,
    playerName,
    roomStatus,
    players,
    hostId,
    myTeam,
    isSpy,
    winningTeam,
    finalResult,
    voteResults,
    isHost,
    setPlayerInfo,
    setRoomData,
    reset
  }
})
