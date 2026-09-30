<template>
  <div class="result-view">
    <!-- 最终结果 -->
    <div class="result-header">
      <div class="result-icon">🏆</div>
      <h2 class="result-title">{{ overallWinnerTeam }}队 获得最终胜利！</h2>
      <p class="result-subtitle" v-if="finalResult === 'loser_win'">
        失败方成功逆转！
      </p>
      <p class="result-subtitle" v-else>
        胜利方保持胜利！
      </p>
    </div>

    <div class="result-details">
      <!-- 游戏阶段结果 -->
      <div class="detail-card">
        <h3>游戏阶段</h3>
        <div class="phase-result">
          <div class="phase-item">
            <span class="phase-label">游戏胜负:</span>
            <span class="phase-value" :class="gameWinnerClass">{{ gameStore.winningTeam }}队获胜</span>
          </div>
          <div class="phase-item" v-if="voteResults">
            <span class="phase-label">失败方投票:</span>
            <span class="phase-value">
              投出 {{ getVoteTargetName(voteResults.loser_vote_result?.target) }}
              <el-tag :type="voteResults.loser_vote_result?.correct ? 'success' : 'danger'" size="small">
                {{ voteResults.loser_vote_result?.correct ? '投对了' : '投错了' }}
              </el-tag>
            </span>
          </div>
          <div class="phase-item" v-if="voteResults?.winner_vote_result">
            <span class="phase-label">胜利方投票:</span>
            <span class="phase-value">
              投出 {{ getVoteTargetName(voteResults.winner_vote_result?.target) }}
              <el-tag :type="voteResults.winner_vote_result?.correct ? 'success' : 'danger'" size="small">
                {{ voteResults.winner_vote_result?.correct ? '投对了' : '投错了' }}
              </el-tag>
            </span>
          </div>
        </div>
      </div>

      <!-- 卧底揭晓 -->
      <div class="detail-card">
        <h3>🕵️ 卧底揭晓</h3>
        <div class="spy-reveal">
          <div class="spy-item">
            <span class="spy-team">A队卧底:</span>
            <span class="spy-name">{{ spyA?.name || '未知' }}</span>
          </div>
          <div class="spy-item">
            <span class="spy-team">B队卧底:</span>
            <span class="spy-name">{{ spyB?.name || '未知' }}</span>
          </div>
        </div>
      </div>

      <!-- 投票详情 -->
      <div class="detail-card" v-if="teamAVoteDetails.length || teamBVoteDetails.length">
        <h3>🗳️ 投票详情</h3>
        <div class="vote-details-teams">
          <div class="vote-detail-team">
            <h4 class="team-a-color">A队投票</h4>
            <div class="vote-detail-list">
              <div v-for="(vote, idx) in teamAVoteDetails" :key="'a-' + idx" class="vote-detail-item">
                <span class="voter-name">{{ vote.voter }}</span>
                <span class="vote-arrow">→</span>
                <span class="target-name" :class="{ 'is-spy-target': vote.isSpy }">{{ vote.target }}</span>
                <el-tag v-if="vote.isSpy" type="success" size="small">卧底</el-tag>
              </div>
            </div>
          </div>
          <div class="vote-detail-team">
            <h4 class="team-b-color">B队投票</h4>
            <div class="vote-detail-list">
              <div v-for="(vote, idx) in teamBVoteDetails" :key="'b-' + idx" class="vote-detail-item">
                <span class="voter-name">{{ vote.voter }}</span>
                <span class="vote-arrow">→</span>
                <span class="target-name" :class="{ 'is-spy-target': vote.isSpy }">{{ vote.target }}</span>
                <el-tag v-if="vote.isSpy" type="success" size="small">卧底</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 队伍名单 -->
      <div class="detail-card">
        <h3>队伍名单</h3>
        <div class="teams-list">
          <div class="team-section team-a-section">
            <h4 class="team-heading team-a-color">A队</h4>
            <div class="member-list">
              <div 
                v-for="player in teamAPlayers" 
                :key="player.id" 
                class="member-item"
                :class="{ 'is-spy': player.is_spy }"
              >
                <span class="member-name">{{ player.name }}</span>
                <span v-if="player.is_spy" class="spy-tag">卧底</span>
              </div>
            </div>
          </div>
          <div class="team-section team-b-section">
            <h4 class="team-heading team-b-color">B队</h4>
            <div class="member-list">
              <div 
                v-for="player in teamBPlayers" 
                :key="player.id" 
                class="member-item"
                :class="{ 'is-spy': player.is_spy }"
              >
                <span class="member-name">{{ player.name }}</span>
                <span v-if="player.is_spy" class="spy-tag">卧底</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 结果说明 -->
      <div class="detail-card explanation">
        <h3>结果说明</h3>
        <p class="explanation-text">{{ resultExplanation }}</p>
      </div>
    </div>

    <div class="result-actions">
      <el-button type="success" size="large" @click="backToRoom">
        返回房间（再来一局）
      </el-button>
      <el-button type="primary" size="large" @click="backToHome">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useGameStore } from '../stores/game'
import api from '../utils/api'

const router = useRouter()
const gameStore = useGameStore()

const finalResult = computed(() => gameStore.finalResult)
const voteResults = computed(() => gameStore.voteResults)

// 计算最终胜利队伍
const overallWinnerTeam = computed(() => {
  if (finalResult.value === 'loser_win') {
    // 失败方逆转，游戏失败方获胜
    return gameStore.winningTeam === 'A' ? 'B' : 'A'
  }
  // 正常结果，游戏胜利方获胜
  return gameStore.winningTeam
})

const gameWinnerClass = computed(() => {
  return gameStore.winningTeam === 'A' ? 'team-a-win' : 'team-b-win'
})

const spyA = computed(() => {
  return gameStore.players.find(p => p.seat >= 1 && p.seat <= 5 && p.is_spy)
})

const spyB = computed(() => {
  return gameStore.players.find(p => p.seat >= 6 && p.seat <= 10 && p.is_spy)
})

const teamAPlayers = computed(() => 
  gameStore.players.filter(p => p.seat >= 1 && p.seat <= 5)
)

const teamBPlayers = computed(() => 
  gameStore.players.filter(p => p.seat >= 6 && p.seat <= 10)
)

// 投票详情：按队伍分组，显示谁投了谁
const teamAVoteDetails = computed(() => {
  if (!voteResults.value?.votes) return []
  return Object.entries(voteResults.value.votes)
    .map(([voterId, targetId]) => {
      const voter = gameStore.players.find(p => p.id === voterId)
      const target = gameStore.players.find(p => p.id === targetId)
      if (!voter || !target) return null
      const voterTeam = voter.seat <= 5 ? 'A' : 'B'
      if (voterTeam !== 'A') return null
      return { voter: voter.name, target: target.name, isSpy: target.is_spy }
    })
    .filter(Boolean)
})

const teamBVoteDetails = computed(() => {
  if (!voteResults.value?.votes) return []
  return Object.entries(voteResults.value.votes)
    .map(([voterId, targetId]) => {
      const voter = gameStore.players.find(p => p.id === voterId)
      const target = gameStore.players.find(p => p.id === targetId)
      if (!voter || !target) return null
      const voterTeam = voter.seat <= 5 ? 'A' : 'B'
      if (voterTeam !== 'B') return null
      return { voter: voter.name, target: target.name, isSpy: target.is_spy }
    })
    .filter(Boolean)
})

const resultExplanation = computed(() => {
  const gameWinner = gameStore.winningTeam
  const gameLoser = gameWinner === 'A' ? 'B' : 'A'
  const loserCorrect = voteResults.value?.loser_vote_result?.correct
  const winnerCorrect = voteResults.value?.winner_vote_result?.correct
  
  if (loserCorrect) {
    if (winnerCorrect) {
      return `${gameLoser}队（失败方）投对了卧底，${gameWinner}队（胜利方）也投对了卧底。${gameWinner}队获得最终胜利。`
    } else {
      return `${gameLoser}队（失败方）投对了卧底，但${gameWinner}队（胜利方）投错了卧底。${gameLoser}队成功逆转获胜！`
    }
  } else {
    return `${gameLoser}队（失败方）投错了卧底。${gameWinner}队获得最终胜利。`
  }
})

const getVoteTargetName = (targetId) => {
  if (!targetId) return '无'
  const player = gameStore.players.find(p => p.id === targetId)
  return player ? player.name : '未知'
}

const backToRoom = async () => {
  try {
    await api.resetRoom(gameStore.roomCode, gameStore.playerId)
    gameStore.roomStatus = 'waiting'
    gameStore.winningTeam = null
    gameStore.finalResult = null
    gameStore.voteResults = null
    ElMessage.success('房间已重置，可以开始新一局')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '重置失败')
  }
}

const backToHome = () => {
  gameStore.reset()
  router.push('/')
}
</script>

<style scoped>
.result-view {
  max-width: 650px;
  margin: 0 auto;
  text-align: center;
}

.result-header {
  margin-bottom: 40px;
}

.result-icon {
  font-size: 5rem;
  margin-bottom: 20px;
}

.result-title {
  font-size: 2rem;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #feca57, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.result-subtitle {
  color: #aaa;
  font-size: 1.2rem;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.detail-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.detail-card h3 {
  color: #feca57;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

/* 游戏阶段结果 */
.phase-result {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.phase-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.phase-label {
  color: #aaa;
}

.phase-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.phase-value.team-a-win {
  color: #4fc3f7;
}

.phase-value.team-b-win {
  color: #ff8a65;
}

/* 卧底揭晓 */
.spy-reveal {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.spy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 10px;
}

.spy-team {
  color: #aaa;
}

.spy-name {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.1rem;
}

/* 队伍名单 */
.teams-list {
  display: flex;
  gap: 20px;
}

.team-section {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 15px;
}

.team-heading {
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.team-a-color { color: #4fc3f7; }
.team-b-color { color: #ff8a65; }

.member-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.member-item.is-spy {
  background: rgba(255, 107, 107, 0.15);
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.member-name {
  color: #eee;
}

.spy-tag {
  background: #ff6b6b;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: bold;
}

/* 投票详情 */
.vote-details-teams {
  display: flex;
  gap: 20px;
}

.vote-detail-team {
  flex: 1;
}

.vote-detail-team h4 {
  margin-bottom: 12px;
  font-size: 1rem;
}

.vote-detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vote-detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.voter-name {
  color: #eee;
  font-weight: 500;
}

.vote-arrow {
  color: #666;
}

.target-name {
  color: #ccc;
}

.target-name.is-spy-target {
  color: #4caf50;
  font-weight: bold;
}

/* 结果说明 */
.explanation-text {
  color: #ccc;
  line-height: 1.8;
  text-align: left;
}

/* 操作按钮 */
.result-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}
</style>
