# Baseball Database Management System  
資料庫期末專案 – 棒球數據管理與查詢系統
後端：Flask + PostgreSQL + Redis｜前端：HTML / Fetch API

## 專案簡介 (Project Introduction)
本專案為資料庫系統期末專案，實作一套棒球數據查詢與統計系統。  

後端使用 **Flask + PostgreSQL（結構化資料） + Redis（NoSQL 查詢次數計數器）**，提供隊伍、球員、比賽等數據查詢API，並額外使用 Redis 追蹤搜尋次數、記錄每次查詢行為，最後統計出搜尋次數排行榜。

## 主要功能
- 使用者帳號系統（註冊 / 登入 / 加密 / Token 驗證）
- 球隊、球員、比賽查詢 API
- PostgreSQL 儲存結構化資料
- Redis 蒐集查詢次數，並產生三類排行榜：
  - 球隊搜尋次數排行榜
  - 球員搜尋次數排行榜
  - 比賽搜尋次數排行榜
- 統計數據排行榜展示（打擊率、全壘打數等）
- PostgreSQL 資料庫備份檔

## 安裝說明 (Installation Guide)

### 1. Clone 專案
git clone https://github.com/jason092634/Database_Management.git

cd <Database_Management>

### 2. Python 套件
pip install -r requirements.txt
pip install redis

### 3. 建立 PostgreSQL 資料庫並匯入備份
psql -U postgres -f DB_Backup.sql

### 4. 下載 Redis
sudo apt install redis-server
sudo systemctl start redis

### 5. 設定環境變數（資料庫與 Redis）
建立 config.py 或 .env：

DB_CONFIG = {
    "host": "localhost",
    "database": your database,
    "user": "postgres",
    "password": your password
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0
}

ADMIN_SECRET_KEY=your admin secret key

### 6. 啟動後端 Flask
python app.py
後端將在 http://127.0.0.1:5000/ 啟動。

## 使用示例 / 教學 (Example / Tutorial)

### 1. 範例：查詢球員資料

API 範例：

Request
POST /search/player
{
  "player_name": "Ohtani"
}

Response
{
  "player_id": 17,
  "team": "Angels",
  "avg": 0.286,
  "home_runs": 44
}

並且 Redis 會自動將「Ohtani」搜尋次數 +1。

### 2. 範例：取得排行榜

GET /ranking/players

Response:

[
  {"player_name": "Ohtani", "count": 152},
  {"player_name": "Judge", "count": 98}
]

## 專案結構 (Project Structure)

backend/

│ .gitattributes

│ .gitignore

│ .env

│ pyvenv.cfg

│ requirements.txt

│ app.py

│ config.py

│

├─routes/

│   __init__.py

│   admin_routes.py

│   auth_routes.py

│   follow_routes.py

│   leaderboard_routes.py

│   match_routes.py

│   player_routes.py

│   player_stats_routes.py

│   search_board_routes.py

│   team_routes.py

│

frontend/

│ admin.html

│ dashboard.html

│ follow.html

│ index.html

│ leaderboard.html

│ login.html

│ match_search.html

│ player_search.html

│ player_stats_search.html

│ register.html

│ search_board.html

│ team_search.html

│

file/

│ create_table.sql

│

├─csv/

│   battingrecord.csv

│   fieldingrecord.csv

│   league.csv

│   match.csv

│   match_player.csv

│   match_umpire.csv

│   pitchingrecord.csv

│   player.csv

│   team.csv

│   umpire.csv

│

DB_Backup.sql

README.md

.gitignore

## 組員名單

資管三 B12705013 林志欣
資管三 B12705044 黃夢恩
地理三 B12208033 陳煒麟

## 附註

資料庫備份檔 DB_Backup.sql 已包含在 repository 中。另外 file 資料夾中也有每張表對應的 csv 檔案，以及原始的 sql 指令。