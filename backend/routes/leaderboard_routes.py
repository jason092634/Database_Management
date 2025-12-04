from flask import Blueprint, jsonify
from config import DB_CONFIG
import psycopg2

leaderboard_bp = Blueprint("leaderboard_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# 全壘打排行榜
@leaderboard_bp.route("/api/leaderboard/home_runs", methods=["GET"])
def leaderboard_home_runs():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                p.name,
                t.team_name,
                SUM(b.home_runs) AS total_home_runs
            FROM BattingRecord b
            JOIN Match_Player mp ON b.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY total_home_runs DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "home_runs": row[2]
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 安打排行榜
@leaderboard_bp.route("/api/leaderboard/hits", methods=["GET"])
def leaderboard_hits():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                p.name,
                t.team_name,
                SUM(b.hits) AS total_hits
            FROM BattingRecord b
            JOIN Match_Player mp ON b.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY total_hits DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "hits": row[2]
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
# 打點排行榜
@leaderboard_bp.route("/api/leaderboard/rbis", methods=["GET"])
def leaderboard_rbis():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                p.name,
                t.team_name,
                SUM(b.rbis) AS total_rbis
            FROM BattingRecord b
            JOIN Match_Player mp ON b.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY total_rbis DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "rbis": row[2]
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 打擊率排行榜
@leaderboard_bp.route("/api/leaderboard/avg", methods=["GET"])
def leaderboard_batting_average():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                SUM(b.hits) AS hits,
                SUM(b.at_bats) AS at_bats,
                ROUND(
                    SUM(b.hits)::numeric / NULLIF(SUM(b.at_bats), 0),
                    3
                ) AS batting_average
            FROM BattingRecord b
            JOIN Match_Player mp ON b.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            HAVING SUM(b.at_bats) >= 30
            ORDER BY batting_average DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "batting_avg": float(row[4])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 盜壘排行榜
@leaderboard_bp.route("/api/leaderboard/stolen_bases", methods=["GET"])
def leaderboard_stolen_bases():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                SUM(b.stolen_bases) AS stolen_bases
            FROM BattingRecord b
            JOIN Match_Player mp ON b.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            HAVING SUM(b.stolen_bases) > 0
            ORDER BY stolen_bases DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "stolen_bases": int(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
# 三振排行榜
@leaderboard_bp.route("/api/leaderboard/strikeouts", methods=["GET"])
def leaderboard_strikeouts():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                SUM(pr.strikeouts) AS strikeouts
            FROM PitchingRecord pr
            JOIN Match_Player mp ON pr.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY strikeouts DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "strikeouts": int(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 勝投排行榜
@leaderboard_bp.route("/api/leaderboard/wins", methods=["GET"])
def leaderboard_wins():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                COUNT(*) AS wins
            FROM PitchingRecord pr
            JOIN Match_Player mp ON pr.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            WHERE pr.pitch_result = 'W'
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY wins DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "wins": int(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 防禦率排行榜
@leaderboard_bp.route("/api/leaderboard/era", methods=["GET"])
def leaderboard_era():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                ROUND(SUM(pr.earned_runs) * 9.0 / NULLIF(SUM(pr.innings_pitched), 0), 2) AS era,
                SUM(pr.innings_pitched) AS total_innings
            FROM PitchingRecord pr
            JOIN Match_Player mp ON pr.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            GROUP BY p.player_id, p.name, t.team_name
            HAVING SUM(pr.innings_pitched) >= 10  -- 至少投球10局
            ORDER BY era ASC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "era": float(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 中繼成功排行榜
@leaderboard_bp.route("/api/leaderboard/holds", methods=["GET"])
def leaderboard_holds():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                COUNT(*) AS holds
            FROM PitchingRecord pr
            JOIN Match_Player mp ON pr.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            WHERE pr.pitch_result = 'H'
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY holds DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "holds": int(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 救援成功排行榜
@leaderboard_bp.route("/api/leaderboard/saves", methods=["GET"])
def leaderboard_saves():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.name,
                t.team_name,
                COUNT(*) AS saves
            FROM PitchingRecord pr
            JOIN Match_Player mp ON pr.record_id = mp.record_id
            JOIN Player p ON mp.player_id = p.player_id
            JOIN Team t ON p.team_id = t.team_id
            WHERE pr.pitch_result = 'S'
            GROUP BY p.player_id, p.name, t.team_name
            ORDER BY saves DESC
            LIMIT 5;
        """

        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "team_name": row[1],
                "saves": int(row[2])
            })

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

