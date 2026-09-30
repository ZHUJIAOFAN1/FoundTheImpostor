from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import room, player, vote
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="卧底模式助手API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(room.router, prefix="/api")
app.include_router(player.router, prefix="/api")
app.include_router(vote.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "卧底模式助手API"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
