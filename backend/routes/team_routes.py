from flask import Blueprint, jsonify, request, current_app
from config import DB_CONFIG
import psycopg2

team_bp = Blueprint('team_bp', __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@team_bp.route("/search/teams", methods=["POST"])
def search_teams():
    data = request.json
    keyword = data.get("name", "").strip()

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT t.team_id, t.team_name, p.player_id, p.name
            FROM Team t
            LEFT JOIN Player p ON t.team_id = p.team_id
            WHERE t.team_name ILIKE %s
            ORDER BY t.team_id, p.player_id;
        """
        cur.execute(query, (f"%{keyword}%",))
        rows = cur.fetchall()
        conn.close()

        # Redis increment
        if keyword:
            current_app.redis.zincrby("team_query_count", 1, f"team:{keyword}")

        result = {}
        for team_id, team_name, player_id, player_name in rows:
            if team_name not in result:
                result[team_name] = []
            if player_id:
                result[team_name].append({"player_id": player_id, "player_name": player_name})

        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
