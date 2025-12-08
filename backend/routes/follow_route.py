from flask import Blueprint, request, jsonify, session
import psycopg2
from config import DB_CONFIG

follow = Blueprint("follow", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_current_user_id():
    """
    取得目前 user_id：
    1. 先看 URL query: /xxx?user_id=3
    2. 再看 JSON body: {"user_id": 3}
    3. 都沒有就先預設 1（方便除錯）
    """
    uid = request.args.get("user_id")
    if uid:
        try:
            return int(uid)
        except ValueError:
            pass

    data = request.get_json(silent=True) or {}
    uid = data.get("user_id")
    if uid is not None:
        try:
            return int(uid)
        except ValueError:
            pass

    return 1


# 1. 追蹤球員
@follow.route("/follow/player", methods=["POST"])
def follow_player():
    try:
        data = request.json
        player_id = data.get("player_id")
        user_id = get_current_user_id()

        if not player_id:
            return jsonify({"success": False, "error": "缺少 player_id"})

        conn = get_connection()
        cur = conn.cursor()

        # 避免重複追蹤
        cur.execute("""
            SELECT 1 FROM Followed_player 
            WHERE user_id = %s AND player_id = %s
        """, (user_id, player_id))

        if cur.fetchone():
            conn.close()
            return jsonify({"success": True, "message": "已經追蹤過該球員"})

        # 新增追蹤紀錄
        cur.execute("""
            INSERT INTO Followed_player (user_id, player_id, follow_time)
            VALUES (%s, %s, NOW())
        """, (user_id, player_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "成功追蹤球員"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 2. 追蹤球隊
@follow.route("/follow/team", methods=["POST"])
def follow_team():
    try:
        data = request.json
        team_id = data.get("team_id")
        team_name = data.get("team_name")

        user_id = get_current_user_id()

        if not team_id and not team_name:
            return jsonify({"success": False, "error": "缺少 team_id 或 team_name"})

        conn = get_connection()
        cur = conn.cursor()

        # 如果沒有 team_id，但有 team_name，就用名稱查出 team_id
        if not team_id and team_name:
            cur.execute(
                "SELECT team_id FROM Team WHERE team_name = %s LIMIT 1",
                (team_name,),
            )
            row = cur.fetchone()
            if not row:
                conn.close()
                return jsonify({"success": False, "error": "找不到該球隊"})
            team_id = row[0]

        # 避免重複追蹤
        cur.execute("""
            SELECT 1 FROM Followed_team
            WHERE user_id = %s AND team_id = %s
        """, (user_id, team_id))

        if cur.fetchone():
            conn.close()
            return jsonify({"success": True, "message": "已經追蹤過該球隊"})

        # 新增追蹤紀錄
        cur.execute("""
            INSERT INTO Followed_team (user_id, team_id, follow_time)
            VALUES (%s, %s, NOW())
        """, (user_id, team_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "成功追蹤球隊"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 3. 取得追蹤球員列表
@follow.route("/followed/players", methods=["GET"])
def get_followed_players():
    try:
        user_id = get_current_user_id()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                fp.player_id,
                p.name,
                p.number,
                t.team_name,
                fp.follow_time
            FROM Followed_player fp
            JOIN Player p ON fp.player_id = p.player_id
            LEFT JOIN Team t ON p.team_id = t.team_id
            WHERE fp.user_id = %s
            ORDER BY fp.follow_time DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()

        result = [
            {
                "player_id":  r[0],
                "name":       r[1],
                "number":     r[2],
                "team_name":  r[3],
                "follow_time": r[4],
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 4. 取得追蹤球隊列表
@follow.route("/followed/teams", methods=["GET"])
def get_followed_teams():
    try:
        user_id = get_current_user_id()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                ft.team_id,
                t.team_name,
                t.manager_name,
                ft.follow_time
            FROM Followed_team ft
            JOIN Team t ON ft.team_id = t.team_id
            WHERE ft.user_id = %s
            ORDER BY ft.follow_time DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()

        result = [
            {
                "team_id":      r[0],
                "team_name":    r[1],
                "manager_name": r[2],
                "follow_time":  r[3],
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 5. 追蹤頁面用：查球隊基本資訊
@follow.route("/follow/search_teams", methods=["POST"])
def follow_search_teams():
    try:
        data = request.json
        keyword = data.get("name", "")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                t.team_id,
                t.team_name,
                t.manager_name,
                l.league_name
            FROM Team t
            LEFT JOIN League l ON t.league_id = l.league_id
            WHERE t.team_name ILIKE %s
            ORDER BY t.team_id
        """, (f"%{keyword}%",))

        rows = cur.fetchall()
        conn.close()

        result = [
            {
                "team_id":      r[0],
                "team_name":    r[1],
                "manager_name": r[2] or "Unknown",
                "league_name":  r[3] or "Unknown",
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 6. 追蹤頁面用：查球員基本資訊
@follow.route("/follow/search_players", methods=["POST"])
def follow_search_players():
    try:
        data = request.json
        name_input = data.get("name", "").strip()

        if not name_input:
            return jsonify({"success": False, "error": "請輸入球員名稱"})

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                p.player_id,              -- r[0]
                p.name AS player_name,    -- r[1]
                p.number,                 -- r[2]
                p.status,                 -- r[3]
                t.team_name,              -- r[4]
                t.manager_name,           -- r[5]
                l.league_name             -- r[6]
            FROM player p
            LEFT JOIN team t ON p.team_id = t.team_id
            LEFT JOIN league l ON t.league_id = l.league_id
            WHERE p.name ILIKE %s
        """, (f"%{name_input}%",))

        rows = cur.fetchall()
        conn.close()

        players = [
            {
                "player_id":   r[0],
                "player_name": r[1],
                "number":      r[2],
                "status":      r[3],
                "team_name":   r[4] or "Unknown",
                "league_name": r[6] or "Unknown",   
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": players})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
# 取消追蹤球員
@follow.route("/unfollow/player", methods=["POST"])
def unfollow_player():
    try:
        data = request.json or {}
        player_id = data.get("player_id")
        user_id = get_current_user_id()

        if not player_id:
            return jsonify({"success": False, "error": "缺少 player_id"})

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM Followed_player
            WHERE user_id = %s AND player_id = %s
        """, (user_id, player_id))

        deleted = cur.rowcount
        conn.commit()
        conn.close()

        if deleted == 0:
            return jsonify({"success": False, "message": "本來就沒有追蹤這個球員"})
        else:
            return jsonify({"success": True, "message": "已取消追蹤球員"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 取消追蹤球隊
@follow.route("/unfollow/team", methods=["POST"])
def unfollow_team():
    try:
        data = request.json or {}
        team_id = data.get("team_id")
        user_id = get_current_user_id()

        if not team_id:
            return jsonify({"success": False, "error": "缺少 team_id"})

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM Followed_team
            WHERE user_id = %s AND team_id = %s
        """, (user_id, team_id))

        deleted = cur.rowcount
        conn.commit()
        conn.close()

        if deleted == 0:
            return jsonify({"success": False, "message": "本來就沒有追蹤這個球隊"})
        else:
            return jsonify({"success": True, "message": "已取消追蹤球隊"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 取得某球員最近 10 場比賽資訊
@follow.route("/follow/player/<int:player_id>/recent_matches", methods=["GET"])
def get_player_recent_matches(player_id):
    """
    回傳指定球員最近 10 場有出賽的比賽資訊
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                m.match_id,
                m.date,
                m.location,
                ht.team_name AS home_team_name,
                at.team_name AS away_team_name,
                m.home_score,
                m.away_score
            FROM Match m
            JOIN Match_Player mp ON m.match_id = mp.match_id
            JOIN Player p ON mp.player_id = p.player_id
            LEFT JOIN Team ht ON m.home_team_id = ht.team_id
            LEFT JOIN Team at ON m.away_team_id = at.team_id
            WHERE p.player_id = %s
            ORDER BY m.date DESC, m.start_time DESC NULLS LAST
            LIMIT 10
        """, (player_id,))

        rows = cur.fetchall()
        conn.close()

        result = [
            {
                "match_id":        r[0],
                "date":            r[1],
                "location":        r[2],
                "home_team_name":  r[3],
                "away_team_name":  r[4],
                "home_score":      r[5],
                "away_score":      r[6],
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 取得某球隊最近 10 場比賽資訊
@follow.route("/follow/team/<int:team_id>/recent_matches", methods=["GET"])
def get_team_recent_matches(team_id):
    """
    回傳指定球隊最近 10 場比賽（不分主客場）
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                m.match_id,
                m.date,
                m.location,
                ht.team_name AS home_team_name,
                at.team_name AS away_team_name,
                m.home_score,
                m.away_score
            FROM Match m
            LEFT JOIN Team ht ON m.home_team_id = ht.team_id
            LEFT JOIN Team at ON m.away_team_id = at.team_id
            WHERE m.home_team_id = %s OR m.away_team_id = %s
            ORDER BY m.date DESC, m.start_time DESC NULLS LAST
            LIMIT 10
        """, (team_id, team_id))

        rows = cur.fetchall()
        conn.close()

        result = [
            {
                "match_id":        r[0],
                "date":            r[1],
                "location":        r[2],
                "home_team_name":  r[3],
                "away_team_name":  r[4],
                "home_score":      r[5],
                "away_score":      r[6],
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})