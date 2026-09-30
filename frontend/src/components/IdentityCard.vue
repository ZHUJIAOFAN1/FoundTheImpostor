<template>
  <div class="identity-card">
    <div class="card-header">
      <h2>身份分配</h2>
      <p class="subtitle">点击查看你的身份</p>
    </div>

    <div class="my-info">
      <div class="player-badge">
        <span class="team-label" :class="'team-' + myTeam.toLowerCase()">{{ myTeam }}队</span>
      </div>
    </div>

    <div class="identity-reveal" v-if="!revealed">
      <el-button type="warning" size="large" @click="revealIdentity">
        点击查看身份
      </el-button>
      <p class="hint">只有你自己能看到</p>
    </div>

    <div class="identity-result" v-else>
      <div class="identity-display" :class="{ spy: isSpy }">
        <div class="identity-icon">
          {{ isSpy ? '🕵️' : '👤' }}
        </div>
        <div class="identity-text">
          {{ isSpy ? '你是卧底！' : '你不是卧底' }}
        </div>
        <div class="identity-hint">
          {{ isSpy ? '请暗中帮助敌方获胜' : '请正常游戏，争取胜利' }}
        </div>
      </div>
      
      <div class="teammates">
        <h4>你的队友</h4>
        <div class="teammate-list">
          <div v-for="player in teammates" :key="player.id" class="teammate-item">
            {{ player.name }}
          </div>
        </div>
      </div>

      <!-- 只在playing状态显示确认按钮 -->
      <el-button v-if="gameStore.roomStatus === 'playing'" type="primary" @click="confirmIdentity">
        我已知晓身份
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useGameStore } from '../stores/game'
import api from '../utils/api'

const gameStore = useGameStore()
const revealed = ref(false)

const mySeat = computed(() => {
  const me = gameStore.players.find(p => p.id === gameStore.playerId)
  return me?.seat || 0
})

const myTeam = computed(() => {
  return mySeat.value <= 5 ? 'A' : 'B'
})

const isSpy = computed(() => {
  const me = gameStore.players.find(p => p.id === gameStore.playerId)
  return me?.is_spy || false
})

const teammates = computed(() => {
  const myTeamStart = myTeam.value === 'A' ? 1 : 6
  const myTeamEnd = myTeam.value === 'A' ? 5 : 10
  return gameStore.players.filter(p => 
    p.seat >= myTeamStart && 
    p.seat <= myTeamEnd && 
    p.id !== gameStore.playerId
  )
})

const revealIdentity = async () => {
  revealed.value = true
}

const confirmIdentity = async () => {
  try {
    const response = await api.playerReady(gameStore.roomCode, gameStore.playerId)
    // 如果后端返回all_ready为true，或者当前是测试模式，手动更新状态
    if (response.data.all_ready || gameStore.isHost) {
      gameStore.roomStatus = 'gaming'
    }
  } catch (error) {
    ElMessage.error('确认身份失败')
  }
}
</script>

<style scoped>
.identity-card {
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
}

.card-header {
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.subtitle {
  color: #aaa;
}

.my-info {
  margin-bottom: 30px;
}

.player-badge {
  display: inline-flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.1);
  padding: 15px 30px;
  border-radius: 15px;
}

.seat-number {
  font-size: 1.5rem;
  font-weight: bold;
}

.team-label {
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
}

.team-label.team-a {
  background: #4fc3f7;
  color: #000;
}

.team-label.team-b {
  background: #ff8a65;
  color: #000;
}

.identity-reveal {
  margin: 30px 0;
}

.hint {
  color: #888;
  margin-top: 15px;
  font-size: 0.9rem;
}

.identity-result {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.identity-display {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
}

.identity-display.spy {
  background: rgba(255, 107, 107, 0.2);
  border: 2px solid #ff6b6b;
}

.identity-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.identity-text {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.identity-display.spy .identity-text {
  color: #ff6b6b;
}

.identity-hint {
  color: #aaa;
  font-size: 1rem;
}

.teammates {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
}

.teammates h4 {
  margin-bottom: 15px;
  color: #feca57;
}

.teammate-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.teammate-item {
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}
</style>
