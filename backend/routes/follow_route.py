from flask import Blueprint, request, jsonify, session
import psycopg2
from config import DB_CONFIG

follow = Blueprint("follow", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# 1. 追蹤球員
@follow.route("/follow/player", methods=["POST"])
def follow_player():
    try:
        data = request.json
        player_id = data.get("player_id")
        # 預設假user_id為1
        user_id = session.get("user_id", 1)

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
        team_name = data.get("team_name")  # ⭐ 新增：允許前端給球隊名稱

        user_id = session.get("user_id", 1)

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
        user_id = session.get("user_id", 1)

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
                "player_id": r[0],
                "name": r[1],
                "number": r[2],
                "team_name": r[3],
                "follow_time": r[4]
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
        user_id = session.get("user_id", 1)

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
                "team_id": r[0],
                "team_name": r[1],
                "manager_name": r[2],
                "follow_time": r[3]
            }
            for r in rows
        ]

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
