from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import psycopg2
from config import DB_CONFIG, REDIS_CONFIG
from routes.team_routes import team_bp
from routes.auth_routes import auth_bp
from routes.player_routes import player_bp
from routes.match_routes import match_bp
from routes.player_stats_routes import playerstats_bp
from routes.leaderboard_routes import leaderboard_bp
from routes.follow_route import follow
from routes.search_board_routes import searchboard_bp
from routes.admin_routes import admin_bp

from werkzeug.security import generate_password_hash, check_password_hash
import os
import redis

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/")
CORS(app)
app.secret_key = "DBgroup15"

# Redis 連線
redis_client = redis.Redis(**REDIS_CONFIG, decode_responses=True)
app.redis = redis_client

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(isolation_level='SERIALIZABLE')  
    return conn

# 前端頁面路由
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/register", methods=["GET"])
def register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")

@app.route("/login", methods=["GET"])
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/team_search")
def team_search_page():
    return send_from_directory(FRONTEND_DIR, "team_search.html")

@app.route("/player_search")
def player_search_page():
    return send_from_directory(FRONTEND_DIR, "player_search.html")

@app.route("/match_search")
def match_search_page():
    return send_from_directory(FRONTEND_DIR, "match_search.html")

@app.route("/player_stats_search")
def player_stats_search_page():
    return send_from_directory(FRONTEND_DIR, "player_stats_search.html")

@app.route("/leaderboard")
def leaderboard_page():
    return send_from_directory(FRONTEND_DIR, "leaderboard.html")

@app.route("/follow")
def follow_page():
    return send_from_directory(FRONTEND_DIR, "follow.html")


# 註冊/登入
app.register_blueprint(auth_bp)

# 查球隊
app.register_blueprint(team_bp)

# 查球員
app.register_blueprint(player_bp)

# 查比賽
app.register_blueprint(match_bp)

# 查球員成績
app.register_blueprint(playerstats_bp)

# 查看排行榜
app.register_blueprint(leaderboard_bp)

# 追蹤球隊/球員
app.register_blueprint(follow)

# 查看搜尋紀錄
app.register_blueprint(searchboard_bp)

# 進入 admin 後台
app.register_blueprint(admin_bp)

# 啟動 Flask
if __name__ == "__main__":
    app.run(debug=True)
