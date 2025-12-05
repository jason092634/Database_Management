from flask import Blueprint, jsonify
from config import DB_CONFIG
import psycopg2

ranking_bp = Blueprint('ranking_bp', __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ---- 共同 function：執行 SQL，統一格式輸出 ----
def run_query(sql, fields):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {}
        for i, f in enumerate(fields):
            item[f] = r[i]
        result.append(item)

    return result


# ---- 打擊率 AVG ----
@ranking_bp.route("/ranking/avg", methods=["GET"])
def ranking_avg():
    sql = """
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
    fields = ["player_id", "player_name", "team_name",
              "total_hits", "total_at_bats", "avg", "rank"]

    try:
        return jsonify({"success": True, "result": run_query(sql, fields)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ---- 防禦率 ERA ----
@ranking_bp.route("/ranking/era", methods=["GET"])
def ranking_era():
    sql = """
        SELECT
            p.player_id,
            p.name AS player_name,
            t.team_name,
            SUM(COALESCE(pr.innings_pitched, 0)) AS total_ip,
            SUM(COALESCE(pr.earned_runs, 0)) AS total_er,
            ROUND(
                9 * SUM(COALESCE(pr.earned_runs, 0))::numeric
                / NULLIF(SUM(COALESCE(pr.innings_pitched, 0)), 0),
                2
            ) AS era,
            RANK() OVER (
                ORDER BY
                    9 * SUM(COALESCE(pr.earned_runs, 0))::numeric
                    / NULLIF(SUM(COALESCE(pr.innings_pitched, 0)), 0)
            ) AS rank
        FROM player p
        JOIN match_player mp ON mp.player_id = p.player_id
        JOIN match m ON m.match_id = mp.match_id
        LEFT JOIN pitchingrecord pr ON pr.record_id = mp.record_id
        LEFT JOIN team t ON t.team_id = p.team_id
        WHERE EXTRACT(YEAR FROM m.date) = 2025
        GROUP BY p.player_id, p.name, t.team_name
        HAVING SUM(COALESCE(pr.innings_pitched, 0)) >= 10
        ORDER BY era ASC
        LIMIT 5;
    """
    fields = ["player_id", "player_name", "team_name",
              "total_ip", "total_er", "era", "rank"]

    try:
        return jsonify({"success": True, "result": run_query(sql, fields)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ---- 全壘打 HR ----
@ranking_bp.route("/ranking/hr", methods=["GET"])
def ranking_hr():
    sql = """
        SELECT
            p.player_id,
            p.name AS player_name,
            t.team_name,
            SUM(COALESCE(b.home_runs, 0)) AS total_hr,
            RANK() OVER (
                ORDER BY SUM(COALESCE(b.home_runs, 0)) DESC
            ) AS rank
        FROM player p
        JOIN match_player mp ON mp.player_id = p.player_id
        JOIN match m ON m.match_id = mp.match_id
        LEFT JOIN battingrecord b ON b.record_id = mp.record_id
        LEFT JOIN team t ON t.team_id = p.team_id
        WHERE EXTRACT(YEAR FROM m.date) = 2025
        GROUP BY p.player_id, p.name, t.team_name
        ORDER BY total_hr DESC
        LIMIT 5;
    """
    fields = ["player_id", "player_name", "team_name", "total_hr", "rank"]

    try:
        return jsonify({"success": True, "result": run_query(sql, fields)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
