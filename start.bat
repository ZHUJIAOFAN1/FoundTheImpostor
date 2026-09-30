@echo off
echo ========================================
echo   卧底模式助手 - 启动脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo [1/4] 安装后端依赖...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt -q
cd ..

echo [2/4] 安装前端依赖...
cd frontend
if not exist "node_modules" (
    call npm install
)
cd ..

echo [3/4] 启动后端服务...
cd backend
call venv\Scripts\activate
start "Backend" cmd /c "uvicorn app.main:app --reload --port 8000"
cd ..

echo [4/4] 启动前端服务...
cd frontend
start "Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ========================================
echo   启动完成！
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo ========================================
echo.
pause
