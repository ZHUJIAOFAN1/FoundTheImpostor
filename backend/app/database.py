import os
from dotenv import load_dotenv

load_dotenv()

# 尝试导入supabase，如果失败则使用内存存储
try:
    from supabase import create_client, Client
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_KEY", "")
    
    if url and key:
        supabase: "Client | None" = create_client(url, key)
    else:
        supabase = None
except ImportError:
    supabase = None

# 内存存储（开发用）
rooms_db = {}

def get_db():
    """获取数据库客户端"""
    return supabase

def get_rooms_db():
    """获取房间存储"""
    return rooms_db
