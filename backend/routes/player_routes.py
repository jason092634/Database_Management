from flask import Blueprint, request, jsonify
import psycopg2
from config import DB_CONFIG

player_bp = Blueprint("player_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@player_bp.route("/search/players", methods=["POST"])
def search_players():
    data = request.json
    name_input = data.get("name", "").strip()

    if not name_input:
        return jsonify({"success": False, "error": "請輸入球員名稱"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                p.player_id,
                p.name AS player_name,
                p.number,
                p.status,
                t.team_name,
                t.manager_name,
                l.league_name
            FROM player p
            LEFT JOIN team t ON p.team_id = t.team_id
            LEFT JOIN league l ON t.league_id = l.league_id
            WHERE p.name ILIKE %s
        """, (f"%{name_input}%",))
        rows = cur.fetchall()
        conn.close()

        players = [
            {
                "player_id": r[0],
                "player_name": r[1],
                "number": r[2],
                "status": r[3],
                "team_name": r[4] or "Unknown",
                "manager_name": r[5] or "Unknown",
                "league_name": r[6] or "Unknown"
            } for r in rows
        ]

        return jsonify({"success": True, "result": players})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})