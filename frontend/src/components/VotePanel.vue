<template>
  <div class="vote-panel">
    <div class="vote-header">
      <h2>投票环节</h2>
      <p class="subtitle">请投票选出你认为是卧底的队友</p>
      <p class="team-info">你是 {{ myTeam }}队 | 卧底在你队伍中帮助敌方</p>
    </div>

    <!-- 投票表单 -->
    <div v-if="!hasVoted" class="vote-form">
      <div class="target-team">
        <h3>你的队友 ({{ myTeam }}队)</h3>
        <div class="target-list">
          <div 
            v-for="player in myTeamPlayers" 
            :key="player.id"
            class="target-item"
            :class="{ selected: selectedTarget === player.id }"
            @click="selectTarget(player.id)"
          >
            <span class="target-name">{{ player.name }}</span>
          </div>
        </div>
      </div>

      <el-button 
        type="danger" 
        size="large"
        :disabled="!selectedTarget"
        @click="submitVote"
      >
        确认投票
      </el-button>
    </div>

    <!-- 已投票，等待结果 -->
    <div v-else class="waiting-vote">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>已投票，等待其他玩家投票...</p>
      <p class="vote-status">投票进度: {{ voteCount }} / {{ totalVoters }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '../stores/game'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const gameStore = useGameStore()

const selectedTarget = ref(null)
const hasVoted = ref(false)
const voteCount = ref(0)

const myTeam = computed(() => gameStore.myTeam)

const myTeamPlayers = computed(() => {
  const teamStart = myTeam.value === 'A' ? 1 : 6
  const teamEnd = myTeam.value === 'A' ? 5 : 10
  return gameStore.players.filter(p => 
    p.seat >= teamStart && p.seat <= teamEnd && p.id !== gameStore.playerId
  )
})

const totalVoters = computed(() => gameStore.players.length)

const selectTarget = (playerId) => {
  selectedTarget.value = playerId
}

const submitVote = async () => {
  if (!selectedTarget.value) return
  
  try {
    await api.vote(gameStore.roomCode, gameStore.playerId, selectedTarget.value)
    hasVoted.value = true
    voteCount.value = 1
    ElMessage.success('投票成功')
    // 开始定时刷新投票进度
    startRefreshInterval()
  } catch (error) {
    ElMessage.error('投票失败')
  }
}

// 定时刷新投票进度
let refreshInterval = null

const startRefreshInterval = () => {
  fetchVoteProgress()
  refreshInterval = setInterval(fetchVoteProgress, 2000)
}

const fetchVoteProgress = async () => {
  try {
    const room = await api.getRoom(gameStore.roomCode)
    const votes = room.data.votes?.votes || {}
    voteCount.value = Object.keys(votes).length
  } catch (error) {
    // 静默失败
  }
}

onMounted(() => {
  // 如果已经投过票（页面刷新后），开始刷新
  if (hasVoted.value) {
    startRefreshInterval()
  }
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.vote-panel {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.vote-header {
  margin-bottom: 30px;
}

.vote-header h2 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.subtitle {
  color: #aaa;
  font-size: 1.1rem;
}

.team-info {
  color: #feca57;
  margin-top: 10px;
  font-size: 1rem;
}

.vote-form {
  margin-top: 30px;
}

.target-team {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
}

.target-team h3 {
  margin-bottom: 20px;
  color: #feca57;
}

.target-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.target-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.target-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.target-item.selected {
  background: rgba(255, 107, 107, 0.3);
  border: 2px solid #ff6b6b;
}

.target-name {
  font-size: 1.1rem;
}

.target-seat {
  color: #aaa;
}

.waiting-vote {
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
}

.loading-icon {
  font-size: 3rem;
  color: #feca57;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.vote-status {
  color: #aaa;
  margin-top: 15px;
}
</style>
