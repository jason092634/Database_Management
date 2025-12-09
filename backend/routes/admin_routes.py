from flask import Blueprint, request, jsonify
import psycopg2
from config import DB_CONFIG

admin_bp = Blueprint("admin_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@admin_bp.route("/admin/leagues", methods=["GET"])
def get_leagues():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT league_id, league_name
            FROM league
            ORDER BY league_name
        """)
        rows = cur.fetchall()
        conn.close()

        leagues = [{"league_id": r[0], "league_name": r[1]} for r in rows]
        return jsonify({"success": True, "leagues": leagues})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/teams", methods=["GET"])
def get_teams():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT team_id, team_name, manager_name, team_status, league_id
            FROM Team
            ORDER BY team_id
        """)
        rows = cur.fetchall()
        conn.close()

        teams = [
            {
                "team_id": r[0],
                "team_name": r[1],
                "manager_name": r[2],
                "team_status": r[3],
                "league_id": r[4]
            }
            for r in rows
        ]
        return jsonify({"success": True, "teams": teams})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/team/add", methods=["POST"])
def add_team():
    try:
        data = request.json
        team_name = data.get("team_name", "").strip()
        manager_name = data.get("manager_name", "").strip()
        team_status = data.get("team_status", "Active")
        league_id = data.get("league_id")

        # 驗證必填欄位
        if not team_name:
            return jsonify({"success": False, "error": "球隊名稱必填"})
        if not league_id:
            return jsonify({"success": False, "error": "請選擇聯盟"})

        conn = get_connection()
        cur = conn.cursor()

        # 檢查球隊名稱是否已存在
        cur.execute("SELECT COUNT(*) FROM team WHERE team_name = %s", (team_name,))
        if cur.fetchone()[0] > 0:
            conn.close()
            return jsonify({"success": False, "error": "球隊名稱已存在"})

        # 新增球隊
        cur.execute("""
            INSERT INTO team (team_name, manager_name, team_status, league_id)
            VALUES (%s, %s, %s, %s)
        """, (team_name, manager_name or None, team_status, league_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "新增球隊成功"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/team/edit", methods=["POST"])
def edit_team():
    data = request.json
    team_id = data.get("team_id")
    team_name = data.get("team_name")
    manager_name = data.get("manager_name")
    team_status = data.get("team_status")
    league_id = data.get("league_id")

    if not team_id:
        return jsonify({"success": False, "error": "請選擇球隊"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Build dynamic SQL for optional fields
        update_fields = []
        params = []

        if team_name:
            update_fields.append("team_name = %s")
            params.append(team_name)
        if manager_name:
            update_fields.append("manager_name = %s")
            params.append(manager_name)
        if team_status:
            update_fields.append("team_status = %s")
            params.append(team_status)
        if league_id:
            update_fields.append("league_id = %s")
            params.append(league_id)

        if not update_fields:
            return jsonify({"success": False, "error": "沒有欄位需要修改"})

        params.append(team_id)
        sql = f"UPDATE Team SET {', '.join(update_fields)} WHERE team_id = %s"
        cur.execute(sql, params)
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "球隊資料已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/player/add", methods=["POST"])
def add_player():
    data = request.get_json()
    player_name = data.get("player_name")
    team_id = data.get("team_id")
    number = data.get("number")
    status = data.get("status", "Active")

    if not player_name or not team_id:
        return jsonify({"success": False, "error": "球員姓名與球隊為必填"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO player (name, team_id, number, status)
            VALUES (%s, %s, %s, %s)
        """, (player_name, team_id, number, status))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/umpires", methods=["GET"])
def get_umpires():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT umpire_id, name, status FROM Umpire ORDER BY name")
        umpires = [{"umpire_id": u[0], "name": u[1], "status": u[2]} for u in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({"success": True, "umpires": umpires})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/players", methods=["GET"])
def get_players_by_team():
    team_id = request.args.get("team_id")
    if not team_id:
        return jsonify({"success": False, "error": "缺少 team_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT player_id, name, team_id, number, status
            FROM player
            WHERE team_id = %s
            ORDER BY name
        """, (team_id,))
        rows = cur.fetchall()
        players = []
        for r in rows:
            players.append({
                "player_id": r[0],
                "player_name": r[1],
                "team_id": r[2],
                "number": r[3],
                "status": r[4]
            })
        conn.close()
        return jsonify({"success": True, "players": players})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@admin_bp.route("/admin/player/edit", methods=["POST"])
def edit_player():
    data = request.json
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"success": False, "error": "缺少 player_id"})

    player_name = data.get("player_name")
    team_id = data.get("team_id")
    number = data.get("number")
    status = data.get("status")

    # 檢查是否有欄位要修改
    if not any([player_name, team_id, number, status]):
        return jsonify({"success": False, "error": "沒有欄位需要修改"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        update_fields = []
        params = []

        if player_name:
            update_fields.append("name = %s")
            params.append(player_name)
        if team_id:
            update_fields.append("team_id = %s")
            params.append(team_id)
        if number:
            update_fields.append("number = %s")
            params.append(number)
        if status:
            update_fields.append("status = %s")
            params.append(status)

        params.append(player_id)
        sql = f"UPDATE player SET {', '.join(update_fields)} WHERE player_id = %s"
        cur.execute(sql, params)
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "球員資料已更新"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@admin_bp.route("/admin/umpire/add", methods=["POST"])
def add_umpire():
    data = request.get_json()
    umpire_name = data.get("name")  # 前端 payload key
    status = data.get("status", "Active")  # 預設 Active

    if not umpire_name:
        return jsonify({"success": False, "error": "裁判姓名為必填"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 先檢查是否已存在相同名字
        cur.execute("SELECT COUNT(*) FROM Umpire WHERE name = %s", (umpire_name,))
        exists = cur.fetchone()[0]

        if exists > 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "裁判名稱已存在"})

        # 若不存在，則新增
        cur.execute("""
            INSERT INTO Umpire (name, status)
            VALUES (%s, %s)
        """, (umpire_name, status))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/umpire/edit", methods=["POST"])
def edit_umpire():
    data = request.get_json()
    umpire_id = data.get("umpire_id")
    name = data.get("name")
    status = data.get("status", "Active")

    if not umpire_id or not name:
        return jsonify({"success": False, "error": "裁判 ID 與姓名為必填"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 檢查名稱是否與其他裁判重複
        cur.execute("SELECT COUNT(*) FROM Umpire WHERE name = %s AND umpire_id <> %s", (name, umpire_id))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "裁判名稱已存在"})

        # 更新裁判
        cur.execute("UPDATE Umpire SET name = %s, status = %s WHERE umpire_id = %s", (name, status, umpire_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/add", methods=["POST"])
def add_match():
    data = request.get_json()

    # 必填欄位
    date = data.get("date")
    home_team_id = data.get("home_team_id")
    away_team_id = data.get("away_team_id")
    status = data.get("status")
    location = data.get("location")
    start_time = data.get("start_time")

    # 選填欄位
    home_score = data.get("home_score")
    away_score = data.get("away_score")
    weather = data.get("weather")
    temperature = data.get("temperature")
    attendance = data.get("attendance")

    # 驗證必填欄位
    if not all([date, home_team_id, away_team_id, status, location, start_time]):
        return jsonify({
            "success": False,
            "error": "日期、主隊、客隊、比賽狀態、比賽場地、開始時間為必填"
        })

    if home_team_id == away_team_id:
        return jsonify({"success": False, "error": "主隊與客隊不能相同"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Match
            (date, start_time, location, home_team_id, home_score, away_team_id, away_score, status, weather, temperature, attendance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            date,
            start_time,
            location,
            home_team_id,
            home_score if home_score is not None else 0,
            away_team_id,
            away_score if away_score is not None else 0,
            status,
            weather or None,
            temperature or None,
            attendance or None
        ))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "新增比賽成功"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@admin_bp.route("/admin/matches", methods=["GET"])
def get_matches_by_date():
    date = request.args.get("date")
    if not date:
        return jsonify({"success": False, "error": "缺少日期"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.match_id, m.date, m.start_time, m.home_team_id, m.away_team_id, m.status,
                   m.location, m.home_score, m.away_score, m.weather, m.temperature, m.attendance,
                   ht.team_name AS home_team_name,
                   at.team_name AS away_team_name
            FROM Match m
            JOIN Team ht ON m.home_team_id = ht.team_id
            JOIN Team at ON m.away_team_id = at.team_id
            WHERE m.date = %s
            ORDER BY m.start_time
        """, (date,))
        rows = cur.fetchall()

        matches = []
        for r in rows:
            matches.append({
                "match_id": r[0],
                "date": r[1].isoformat(),
                "start_time": str(r[2]) if r[2] else None,
                "home_team_id": r[3],
                "away_team_id": r[4],
                "status": r[5],
                "location": r[6],
                "home_score": r[7],
                "away_score": r[8],
                "weather": r[9],
                "temperature": float(r[10]) if r[10] is not None else None,
                "attendance": r[11],
                "home_team_name": r[12],
                "away_team_name": r[13]
            })

        cur.close()
        conn.close()
        return jsonify({"success": True, "matches": matches})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/edit", methods=["POST"])
def edit_match():
    data = request.get_json()
    match_id = data.get("match_id")

    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    # 欄位
    date = data.get("date")
    home_team_id = data.get("home_team_id")
    away_team_id = data.get("away_team_id")
    status = data.get("status")
    location = data.get("location")
    start_time = data.get("start_time")
    home_score = data.get("home_score")
    away_score = data.get("away_score")
    weather = data.get("weather")
    temperature = data.get("temperature")
    attendance = data.get("attendance")

    if home_team_id == away_team_id:
        return jsonify({"success": False, "error": "主隊與客隊不能相同"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        update_fields = []
        params = []

        if date:
            update_fields.append("date = %s")
            params.append(date)
        if home_team_id:
            update_fields.append("home_team_id = %s")
            params.append(home_team_id)
        if away_team_id:
            update_fields.append("away_team_id = %s")
            params.append(away_team_id)
        if status:
            update_fields.append("status = %s")
            params.append(status)
        if location is not None:
            update_fields.append("location = %s")
            params.append(location)
        if start_time is not None:
            update_fields.append("start_time = %s")
            params.append(start_time)
        if home_score is not None:
            update_fields.append("home_score = %s")
            params.append(home_score)
        if away_score is not None:
            update_fields.append("away_score = %s")
            params.append(away_score)
        if weather is not None:
            update_fields.append("weather = %s")
            params.append(weather)
        if temperature is not None:
            update_fields.append("temperature = %s")
            params.append(temperature)
        if attendance is not None:
            update_fields.append("attendance = %s")
            params.append(attendance)

        if not update_fields:
            return jsonify({"success": False, "error": "沒有欄位需要修改"})

        params.append(match_id)
        sql = f"UPDATE Match SET {', '.join(update_fields)} WHERE match_id = %s"
        cur.execute(sql, params)
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "比賽資料已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

