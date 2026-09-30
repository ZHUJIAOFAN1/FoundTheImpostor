<template>
  <div class="game">
    <div class="container">
      <!-- 等待大厅 -->
      <div v-if="gameStore.roomStatus === 'waiting'" class="waiting-room">
        <div class="room-header">
          <h2>等待大厅</h2>
          <div class="room-code" @click="copyRoomCode">
            房间号: {{ roomCode }}
            <el-icon><CopyDocument /></el-icon>
          </div>
        </div>

        <div class="teams">
          <div class="team team-a">
            <h3>A队</h3>
            <div class="seats">
              <div 
                v-for="seat in 5" 
                :key="'a-' + seat"
                class="seat"
                :class="{ 
                  occupied: getTeamAPlayer(seat),
                  'my-seat': getTeamAPlayer(seat)?.id === gameStore.playerId,
                  clickable: gameStore.roomStatus === 'waiting'
                }"
                @click="handleSeatClick(seat)"
              >
                <span class="player-name">{{ getTeamAPlayer(seat)?.name || '空位' }}</span>
                <span v-if="getTeamAPlayer(seat)?.id === gameStore.playerId" class="me-tag">我</span>
              </div>
            </div>
          </div>

          <div class="team team-b">
            <h3>B队</h3>
            <div class="seats">
              <div 
                v-for="seat in 5" 
                :key="'b-' + seat"
                class="seat"
                :class="{ 
                  occupied: getTeamBPlayer(seat),
                  'my-seat': getTeamBPlayer(seat)?.id === gameStore.playerId,
                  clickable: gameStore.roomStatus === 'waiting'
                }"
                @click="handleSeatClick(seat + 5)"
              >
                <span class="player-name">{{ getTeamBPlayer(seat)?.name || '空位' }}</span>
                <span v-if="getTeamBPlayer(seat)?.id === gameStore.playerId" class="me-tag">我</span>
              </div>
            </div>
          </div>
        </div>

        <div class="player-count">
          已加入: {{ gameStore.players.length }} / 10
        </div>

        <div class="actions">
          <div class="button-group">
            <el-button 
              v-if="gameStore.isHost" 
              type="primary" 
              size="large"
              @click="confirmStartGame"
            >
              开始游戏
            </el-button>
            <el-button v-else type="info" size="large" disabled>
              等待房主开始游戏...
            </el-button>
            <el-button type="danger" size="large" @click="leaveRoom">
              退出房间
            </el-button>
          </div>
        </div>

        <!-- 开始游戏确认对话框 -->
        <el-dialog v-model="showStartConfirm" title="确认开始游戏" width="400px">
          <div class="confirm-content">
            <p v-if="gameStore.players.length < 6" class="warning-text">
              ⚠️ 当前只有 {{ gameStore.players.length }} 人，少于6人可能影响游戏体验
            </p>
            <p v-if="teamAPlayers.length !== teamBPlayers.length" class="warning-text">
              ⚠️ 队伍人数不平衡：A队{{ teamAPlayers.length }}人，B队{{ teamBPlayers.length }}人
            </p>
            <p class="confirm-text">确定要开始游戏吗？</p>
          </div>
          <template #footer>
            <el-button @click="showStartConfirm = false">取消</el-button>
            <el-button type="primary" @click="startGame">确定开始</el-button>
          </template>
        </el-dialog>
      </div>

      <!-- 身份查看和游戏进行中（合并页面） -->
      <div v-else-if="gameStore.roomStatus === 'playing' || gameStore.roomStatus === 'gaming'" class="game-phase">
        <!-- 身份卡片 -->
        <IdentityCard />

        <!-- 游戏进行中信息 -->
        <div class="game-info-section" v-if="gameStore.roomStatus === 'gaming'">
          <div class="game-info">
            <h2>游戏进行中</h2>
            <p class="tip">请打开无畏契约进行游戏</p>
            <p class="tip">卧底请暗中帮助敌方获胜</p>
          </div>

          <div class="teams-display">
            <div class="team-display team-a">
              <h3>A队</h3>
              <div class="player-list">
                <div v-for="player in teamAPlayers" :key="player.id" class="player-item">
                  {{ player.name }}
                </div>
              </div>
            </div>

            <div class="team-display team-b">
              <h3>B队</h3>
              <div class="player-list">
                <div v-for="player in teamBPlayers" :key="player.id" class="player-item">
                  {{ player.name }}
                </div>
              </div>
            </div>
          </div>

          <div class="game-actions">
            <el-button 
              v-if="gameStore.isHost"
              type="danger" 
              size="large"
              @click="showResultDialog = true"
            >
              游戏结束，输入结果
            </el-button>
          </div>
        </div>

        <!-- 房主确认按钮（playing状态时显示） -->
        <div class="host-actions" v-if="gameStore.roomStatus === 'playing' && gameStore.isHost">
          <el-button type="success" size="large" @click="confirmAllReady">
            确认所有人都已查看身份，开始游戏
          </el-button>
        </div>

        <!-- 等待房主确认（playing状态时非房主显示） -->
        <div class="waiting-host" v-if="gameStore.roomStatus === 'playing' && !gameStore.isHost">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p>等待房主确认所有人都已查看身份...</p>
        </div>

        <!-- 输入结果对话框 -->
        <el-dialog v-model="showResultDialog" title="游戏结果" width="400px">
          <el-form>
            <el-form-item label="获胜队伍">
              <el-radio-group v-model="winningTeam">
                <el-radio label="A">A队获胜</el-radio>
                <el-radio label="B">B队获胜</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showResultDialog = false">取消</el-button>
            <el-button type="primary" @click="submitResult">确认</el-button>
          </template>
        </el-dialog>
      </div>

      <!-- 投票阶段 -->
      <div v-else-if="gameStore.roomStatus === 'voting'" class="voting-phase">
        <VotePanel />
      </div>

      <!-- 结果展示 -->
      <div v-else-if="gameStore.roomStatus === 'finished'" class="result-phase">
        <ResultView />
      </div>

      <!-- 换位确认对话框 -->
      <el-dialog v-model="showSwapConfirm" title="申请换位" width="400px">
        <div class="swap-confirm-content">
          <p>你确定要和 <strong>{{ swapTargetPlayer?.name }}</strong> ({{ swapTargetSeat }}号) 换位吗？</p>
          <p class="swap-hint">换位后你将坐在 {{ swapTargetSeat }}号位置</p>
        </div>
        <template #footer>
          <el-button @click="showSwapConfirm = false">取消</el-button>
          <el-button type="primary" @click="confirmSwap">确定换位</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'
import { useGameStore } from '../stores/game'
import api from '../utils/api'
import IdentityCard from '../components/IdentityCard.vue'
import VotePanel from '../components/VotePanel.vue'
import ResultView from '../components/ResultView.vue'

const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()

const roomCode = computed(() => route.params.roomCode)
const showResultDialog = ref(false)
const showStartConfirm = ref(false)
const showSwapConfirm = ref(false)
const swapTargetSeat = ref(null)
const swapTargetPlayer = ref(null)
const winningTeam = ref('A')

const teamAPlayers = computed(() => 
  gameStore.players.filter(p => p.seat >= 1 && p.seat <= 5)
)

const teamBPlayers = computed(() => 
  gameStore.players.filter(p => p.seat >= 6 && p.seat <= 10)
)

const getTeamAPlayer = (seat) => {
  return gameStore.players.find(p => p.seat === seat)
}

const getTeamBPlayer = (seat) => {
  return gameStore.players.find(p => p.seat === seat + 5)
}

const copyRoomCode = () => {
  navigator.clipboard.writeText(roomCode.value)
  ElMessage.success('房间号已复制')
}

const handleSeatClick = (seat) => {
  if (gameStore.roomStatus !== 'waiting') return
  
  const targetPlayer = gameStore.players.find(p => p.seat === seat)
  
  if (!targetPlayer) {
    // 点击空座位，直接换位
    swapSeat(seat)
  } else if (targetPlayer.id === gameStore.playerId) {
    // 点击自己的座位，不做任何事
    return
  } else {
    // 点击其他玩家，申请换位
    showSwapConfirm.value = true
    swapTargetSeat.value = seat
    swapTargetPlayer.value = targetPlayer
  }
}

const swapSeat = async (targetSeat) => {
  try {
    await api.swapSeat(roomCode.value, gameStore.playerId, targetSeat)
    await fetchRoomData()
    ElMessage.success('换位成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '换位失败')
  }
}

const confirmSwap = async () => {
  showSwapConfirm.value = false
  await swapSeat(swapTargetSeat.value)
}

const confirmStartGame = () => {
  showStartConfirm.value = true
}

const startGame = async () => {
  try {
    await api.startGame(roomCode.value)
    showStartConfirm.value = false
    ElMessage.success('游戏开始！')
  } catch (error) {
    ElMessage.error('开始游戏失败')
  }
}

const confirmAllReady = async () => {
  try {
    // 调用ready API，房主确认后会直接将状态改为gaming
    await api.playerReady(roomCode.value, gameStore.playerId)
    gameStore.roomStatus = 'gaming'
    ElMessage.success('游戏正式开始！')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const leaveRoom = async () => {
  hasLeftRoom = true
  // 先清除定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  try {
    await api.leaveRoom(roomCode.value, gameStore.playerId)
  } catch (error) {
    // 即使API失败也允许退出
    console.error('离开房间失败', error)
  }
  gameStore.reset()
  router.push('/')
  ElMessage.success('已退出房间')
}

const submitResult = async () => {
  try {
    await api.submitResult(roomCode.value, winningTeam.value)
    showResultDialog.value = false
    ElMessage.success('结果已提交')
  } catch (error) {
    ElMessage.error('提交结果失败')
  }
}

const fetchRoomData = async () => {
  if (!roomCode.value) return
  try {
    const response = await api.getRoom(roomCode.value)
    gameStore.setRoomData(response.data)
  } catch (error) {
    if (error.response?.status === 404) {
      // 房间不存在（房主已关闭），跳回首页
      clearInterval(refreshInterval)
      refreshInterval = null
      gameStore.reset()
      router.push('/')
      ElMessage.warning('房主已离开，房间已关闭')
    } else {
      console.error('获取房间信息失败', error)
    }
  }
}

let refreshInterval = null
let hasLeftRoom = false

onMounted(() => {
  fetchRoomData()
  // 定时刷新房间状态
  refreshInterval = setInterval(fetchRoomData, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  // 组件卸载时自动离开房间（处理浏览器后退等非按钮离开场景）
  if (!hasLeftRoom && roomCode.value && gameStore.playerId) {
    api.leaveRoom(roomCode.value, gameStore.playerId).catch(() => {})
  }
})
</script>

<style scoped>
.game {
  flex: 1;
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.room-header {
  text-align: center;
  margin-bottom: 30px;
}

.room-header h2 {
  margin-bottom: 15px;
}

.room-code {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: background 0.3s;
}

.room-code:hover {
  background: rgba(255, 255, 255, 0.2);
}

.teams {
  display: flex;
  justify-content: space-around;
  gap: 30px;
  margin-bottom: 30px;
}

.team {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.team h3 {
  text-align: center;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.team-a h3 { color: #4fc3f7; }
.team-b h3 { color: #ff8a65; }

.seats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.seat {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s;
}

.seat.occupied {
  background: rgba(255, 255, 255, 0.15);
}

.seat.my-seat {
  background: rgba(76, 175, 80, 0.3);
  border: 2px solid #4caf50;
}

.seat.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.seat.clickable:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.02);
}

.me-tag {
  background: #4caf50;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: bold;
}

.seat-number {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-weight: bold;
}

.player-name {
  flex: 1;
}

.player-count {
  text-align: center;
  font-size: 1.1rem;
  margin-bottom: 20px;
  color: #aaa;
}

.actions {
  text-align: center;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
  width: 100%;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.button-group .el-button {
  width: 100% !important;
  margin: 0 !important;
}

/* 游戏进行中样式 */
.gaming-phase {
  text-align: center;
}

.game-info {
  margin-bottom: 30px;
}

.game-info h2 {
  margin-bottom: 15px;
}

.tip {
  color: #aaa;
  margin: 5px 0;
}

.teams-display {
  display: flex;
  justify-content: space-around;
  gap: 30px;
  margin-bottom: 30px;
}

.team-display {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.team-display h3 {
  text-align: center;
  margin-bottom: 15px;
}

.player-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.player-item {
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

/* 确认对话框样式 */
.confirm-content {
  text-align: center;
  padding: 10px 0;
}

.warning-text {
  color: #feca57;
  font-size: 1rem;
  margin: 10px 0;
  padding: 10px;
  background: rgba(254, 202, 87, 0.1);
  border-radius: 8px;
}

.confirm-text {
  color: #ccc;
  font-size: 1rem;
  margin-top: 15px;
}

.game-actions {
  text-align: center;
}

.host-actions {
  text-align: center;
  margin-top: 30px;
}

.waiting-host {
  text-align: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  margin-top: 30px;
}

.waiting-host p {
  color: #aaa;
  margin-top: 15px;
}

.game-info-section {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.swap-confirm-content {
  text-align: center;
  padding: 10px 0;
}

.swap-confirm-content p {
  margin: 10px 0;
  font-size: 1.1rem;
}

.swap-hint {
  color: #aaa;
  font-size: 0.95rem !important;
}
</style>
