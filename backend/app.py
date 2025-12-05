from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from config import DB_CONFIG
from routes.team_routes import team_bp
from routes.board_routes import ranking_bp

app = Flask(__name__)
CORS(app)  # 允許前端不同 port 請求

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# 原本的 test API
@app.route("/test")
def test():
    return jsonify({"message": "Flask is running!"})

# 新增的查球隊 + 球員 API
app.register_blueprint(team_bp)
app.register_blueprint(ranking_bp)

if __name__ == "__main__":
    app.run(debug=True)
