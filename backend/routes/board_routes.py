from flask import Blueprint, jsonify
from config import DB_CONFIG
import psycopg2

ranking_bp = Blueprint('ranking_bp', __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@ranking_bp.route("/ranking/avg", methods=["GET"])
def ranking_avg():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
        SELECT
            s.player_id,
            s.player_name,
            s.team_name,
            s.total_hits,
            s.total_at_bats,
            ROUND(s.total_hits::numeric / NULLIF(s.total_at_bats, 0), 3) AS avg,
            RANK() OVER (
                ORDER BY s.total_hits::numeric / NULLIF(s.total_at_bats, 0) DESC
            ) AS rank
        FROM (
            SELECT
                p.player_id,
                p.name AS player_name,
                t.team_name,
                SUM(COALESCE(b.hits, 0)) AS total_hits,
                SUM(COALESCE(b.at_bats, 0)) AS total_at_bats
            FROM player p
            JOIN match_player mp ON mp.player_id = p.player_id
            JOIN match m ON m.match_id = mp.match_id
            LEFT JOIN battingrecord b ON b.record_id = mp.record_id
            LEFT JOIN team t ON t.team_id = p.team_id
            WHERE EXTRACT(YEAR FROM m.date) = 2025
            GROUP BY p.player_id, p.name, t.team_name
        ) s
        WHERE s.total_at_bats >= 30
        ORDER BY avg DESC
        LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "player_id": r[0],
                "player_name": r[1],
                "team_name": r[2],
                "total_hits": r[3],
                "total_at_bats": r[4],
                "avg": float(r[5]),
                "rank": r[6]
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})