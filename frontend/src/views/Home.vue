<template>
  <div class="home">
    <div class="container">
      <div class="logo">
        <h1>🎭 卧底模式助手</h1>
        <p class="subtitle">无畏契约社群游戏工具</p>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" class="action-btn" @click="showCreateDialog = true">
          创建房间
        </el-button>
        <el-button type="success" size="large" class="action-btn" @click="showJoinDialog = true">
          加入房间
        </el-button>
      </div>

      <div class="rules">
        <el-collapse>
          <el-collapse-item title="📖 游戏规则" name="rules">
            <div class="rules-content">
              <h4>基本规则</h4>
              <ul>
                <li>10名玩家分成两队（每队5人）</li>
                <li>每队随机指定1名卧底</li>
                <li>卧底需要暗中帮助敌方获胜</li>
              </ul>
              <h4>投票规则</h4>
              <ul>
                <li>游戏结束后，失败方投票猜对方队伍的卧底</li>
                <li>如果失败方投对，胜利方也要投票猜卧底</li>
                <li>胜利方投对 → 胜利方胜</li>
                <li>胜利方投错 → 失败方逆转胜</li>
                <li>失败方投错 → 失败方继续失败</li>
              </ul>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 创建房间对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建房间" width="420px" class="room-dialog">
      <el-form :model="createForm" label-width="90px" label-position="right" class="room-form">
        <el-form-item label="你的昵称">
          <el-input v-model="createForm.playerName" placeholder="请输入昵称" maxlength="12" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createRoom" :loading="creating">创建</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 加入房间对话框 -->
    <el-dialog v-model="showJoinDialog" title="加入房间" width="420px" class="room-dialog">
      <el-form :model="joinForm" label-width="90px" label-position="right" class="room-form">
        <el-form-item label="房间号">
          <el-input v-model="joinForm.roomCode" placeholder="请输入6位房间号" maxlength="6" />
        </el-form-item>
        <el-form-item label="你的昵称">
          <el-input v-model="joinForm.playerName" placeholder="请输入昵称" maxlength="12" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showJoinDialog = false">取消</el-button>
          <el-button type="primary" @click="joinRoom" :loading="joining">加入</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useGameStore } from '../stores/game'
import api from '../utils/api'

const router = useRouter()
const gameStore = useGameStore()

const showCreateDialog = ref(false)
const showJoinDialog = ref(false)
const creating = ref(false)
const joining = ref(false)

const createForm = ref({
  playerName: ''
})

const joinForm = ref({
  roomCode: '',
  playerName: ''
})

const createRoom = async () => {
  if (!createForm.value.playerName.trim()) {
    ElMessage.warning('请输入昵称')
    return
  }
  
  creating.value = true
  try {
    const response = await api.createRoom(createForm.value.playerName)
    gameStore.setPlayerInfo(response.data.room_code, response.data.host_id, createForm.value.playerName)
    gameStore.hostId = response.data.host_id  // 设置房主ID
    showCreateDialog.value = false
    router.push(`/room/${response.data.room_code}`)
  } catch (error) {
    ElMessage.error('创建房间失败')
  } finally {
    creating.value = false
  }
}

const joinRoom = async () => {
  if (!joinForm.value.roomCode.trim()) {
    ElMessage.warning('请输入房间号')
    return
  }
  if (!joinForm.value.playerName.trim()) {
    ElMessage.warning('请输入昵称')
    return
  }
  
  joining.value = true
  try {
    const response = await api.joinRoom(joinForm.value.roomCode, joinForm.value.playerName)
    gameStore.setPlayerInfo(joinForm.value.roomCode, response.data.player_id, joinForm.value.playerName)
    gameStore.hostId = response.data.host_id  // 设置房主ID
    showJoinDialog.value = false
    router.push(`/room/${joinForm.value.roomCode}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加入房间失败')
  } finally {
    joining.value = false
  }
}
</script>

<style scoped>
.home {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  max-width: 500px;
  width: 100%;
  text-align: center;
}

.logo {
  margin-bottom: 50px;
}

.logo h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #ff6b6b, #feca57);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #aaa;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
  width: 100%;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.action-btn {
  width: 100% !important;
  height: 60px;
  font-size: 1.2rem;
  margin: 0 !important;
}

.rules {
  text-align: left;
}

.rules-content {
  padding: 10px 0;
}

.rules-content h4 {
  color: #feca57;
  margin: 15px 0 10px;
}

.rules-content ul {
  padding-left: 20px;
}

.rules-content li {
  margin: 8px 0;
  color: #ccc;
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 1.1rem;
  padding: 0 20px;
  border-radius: 10px;
  border: none;
}

:deep(.el-collapse-item__wrap) {
  background: transparent;
  border: none;
}

:deep(.el-collapse-item__content) {
  color: #ccc;
}

/* 对话框样式 */
:deep(.room-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.room-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
  margin: 0;
}

:deep(.room-dialog .el-dialog__title) {
  color: #fff;
  font-size: 1.2rem;
  font-weight: bold;
}

:deep(.room-dialog .el-dialog__body) {
  background: #1a1a2e;
  padding: 30px 20px;
}

:deep(.room-dialog .el-dialog__footer) {
  background: #1a1a2e;
  padding: 15px 20px 20px;
}

.room-form {
  width: 100%;
}

:deep(.room-form .el-form-item) {
  margin-bottom: 20px;
}

:deep(.room-form .el-form-item__label) {
  color: #ccc;
  font-size: 1rem;
}

:deep(.room-form .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

:deep(.room-form .el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.4);
}

:deep(.room-form .el-input__wrapper.is-focus) {
  border-color: #409eff;
  background: rgba(255, 255, 255, 0.15);
}

:deep(.room-form .el-input__inner) {
  color: #fff;
}

:deep(.room-form .el-input__inner::placeholder) {
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
