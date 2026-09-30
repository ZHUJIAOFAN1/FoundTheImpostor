# 卧底模式助手

无畏契约（Valorant）卧底模式游戏助手 Web 应用。

## 功能介绍

- 创建/加入游戏房间
- 随机分配队伍和卧底身份
- 私密查看个人身份
- 投票系统（失败方投票 + 胜利方投票）
- 实时游戏状态同步

## 游戏规则

1. 10名玩家分成两队（每队5人）
2. 每队随机指定1名卧底
3. 卧底需要暗中帮助敌方获胜
4. 游戏结束后，失败方投票猜对方队伍的卧底
5. 如果失败方投对，胜利方也要投票猜卧底
6. 胜利方投对 → 胜利方胜
7. 胜利方投错 → 失败方逆转胜
8. 失败方投错 → 失败方继续失败

## 技术栈

- 前端：Vue 3 + Vite + Element Plus
- 后端：Python FastAPI
- 数据库：Supabase（可选，开发模式使用内存存储）

## 本地开发

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 运行

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 运行

## 部署

### 前端部署到 Vercel

```bash
cd frontend
npm run build
# 将 dist 目录部署到 Vercel
```

### 后端部署到 Railway

1. 在 Railway 创建新项目
2. 连接 GitHub 仓库
3. 设置启动命令：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 配置环境变量

## 项目结构

```
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── components/ # Vue组件
│   │   ├── views/      # 页面视图
│   │   ├── stores/     # 状态管理
│   │   └── utils/      # 工具函数
│   └── ...
│
└── backend/            # 后端项目
    ├── app/
    │   ├── routers/    # API路由
    │   ├── main.py     # 入口文件
    │   ├── models.py   # 数据模型
    │   └── database.py # 数据库配置
    └── ...
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger API 文档。

## License

MIT
