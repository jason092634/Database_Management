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
    
@admin_bp.route("/admin/match/umpires", methods=["GET"])
def get_match_umpires():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT mu.umpire_id, u.name, mu.role
            FROM Match_Umpire mu
            JOIN Umpire u ON mu.umpire_id = u.umpire_id
            WHERE mu.match_id = %s
        """, (match_id,))
        rows = cur.fetchall()
        umpires = [{"umpire_id": r[0], "name": r[1], "role": r[2]} for r in rows]
        cur.close()
        conn.close()
        return jsonify({"success": True, "umpires": umpires})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/umpire/add", methods=["POST"])
def add_match_umpire():
    data = request.get_json()
    match_id = data.get("match_id")
    umpires = data.get("umpires")  # List of dict {role, umpire_id}

    if not match_id or not umpires:
        return jsonify({"success": False, "error": "缺少比賽或裁判資料"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        for u in umpires:
            role = u.get("role")
            umpire_id = u.get("umpire_id")

            if umpire_id is None or umpire_id == "":
                continue  # 可留空

            # 如果該比賽該 role 已存在，先刪掉
            cur.execute("""
                DELETE FROM Match_Umpire
                WHERE match_id = %s AND role = %s
            """, (match_id, role))

            # 新增
            cur.execute("""
                INSERT INTO Match_Umpire (match_id, umpire_id, role)
                VALUES (%s, %s, %s)
            """, (match_id, umpire_id, role))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "裁判名單已更新"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/players", methods=["GET"])
def get_match_players():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 先查這場比賽的主客隊 ID
        cur.execute("SELECT home_team_id, away_team_id FROM Match WHERE match_id = %s", (match_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "找不到比賽"})
        home_team_id, away_team_id = row

        # 查主場球隊球員
        cur.execute("SELECT player_id, name FROM Player WHERE team_id = %s ORDER BY number", (home_team_id,))
        home_players = [{"player_id": r[0], "name": r[1]} for r in cur.fetchall()]

        # 查客場球隊球員
        cur.execute("SELECT player_id, name FROM Player WHERE team_id = %s ORDER BY number", (away_team_id,))
        away_players = [{"player_id": r[0], "name": r[1]} for r in cur.fetchall()]

        # 查這場比賽 Match_Player 的資料
        cur.execute("""
            SELECT record_id, player_id, position, batting_order, is_starting
            FROM Match_Player
            WHERE match_id = %s
        """, (match_id,))
        match_players = [{"record_id": r[0], "player_id": r[1], "position": r[2], "batting_order": r[3], "is_starting": r[4]} for r in cur.fetchall()]

        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "home_players": home_players,
            "away_players": away_players,
            "match_players": match_players
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/player/add", methods=["POST"])
def add_match_player():
    data = request.get_json()
    match_id = data.get("match_id")
    players = data.get("players")  # list of {player_id, position, batting_order, is_starting}

    if not match_id or not players:
        return jsonify({"success": False, "error": "缺少比賽或球員資料"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        for p in players:
            player_id = p.get("player_id")
            position = p.get("position")
            batting_order = p.get("batting_order")
            is_starting = p.get("is_starting", True)

            if not player_id:
                continue

            # 檢查是否已有該球員在此比賽的紀錄
            cur.execute("""
                SELECT record_id FROM Match_Player
                WHERE match_id = %s AND player_id = %s
            """, (match_id, player_id))
            row = cur.fetchone()

            if row:
                # 更新
                cur.execute("""
                    UPDATE Match_Player
                    SET position = %s, batting_order = %s, is_starting = %s
                    WHERE record_id = %s
                """, (position, batting_order, is_starting, row[0]))
            else:
                # 新增
                cur.execute("""
                    INSERT INTO Match_Player (match_id, player_id, position, batting_order, is_starting)
                    VALUES (%s, %s, %s, %s, %s)
                """, (match_id, player_id, position, batting_order, is_starting))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "球員出賽名單已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/batting", methods=["GET"])
def get_match_batting():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT home_team_id, away_team_id FROM Match WHERE match_id = %s", (match_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "找不到比賽"})
        home_team_id, away_team_id = row

        cur.execute("""
            SELECT mp.record_id, mp.player_id, p.name, mp.position, mp.batting_order, mp.is_starting,
                   p.team_id,
                   br.at_bats, br.plate_appearance, br.hits, br.doubles, br.triples, br.home_runs,
                   br.strikeouts, br.walks, br.hit_by_pitch, br.sacrifice_flies, br.double_play, br.triple_play,
                   br.rbis, br.runs, br.stolen_bases, br.caught_stealing, br.remarks
            FROM Match_Player mp
            LEFT JOIN Player p ON mp.player_id = p.player_id
            LEFT JOIN BattingRecord br ON mp.record_id = br.record_id
            WHERE mp.match_id = %s
            ORDER BY mp.batting_order, mp.player_id
        """, (match_id,))

        home_players = []
        away_players = []

        for r in cur.fetchall():
            player_data = {
                "player_id": r[1],
                "name": r[2],
                "batting_record": {   # ⚡ 改為 batting_record
                    "record_id": r[0],  # ⚡ 使用 record_id
                    "position": r[3],
                    "batting_order": r[4],
                    "is_starting": r[5],
                    "at_bats": r[7] or 0,
                    "plate_appearance": r[8] or 0,
                    "hits": r[9] or 0,
                    "doubles": r[10] or 0,
                    "triples": r[11] or 0,
                    "home_runs": r[12] or 0,
                    "strikeouts": r[13] or 0,
                    "walks": r[14] or 0,
                    "hit_by_pitch": r[15] or 0,
                    "sacrifice_flies": r[16] or 0,
                    "double_play": r[17] or 0,
                    "triple_play": r[18] or 0,
                    "rbis": r[19] or 0,
                    "runs": r[20] or 0,
                    "stolen_bases": r[21] or 0,
                    "caught_stealing": r[22] or 0,
                    "remarks": r[23] or ""
                }
            }

            if r[6] == home_team_id:
                home_players.append(player_data)
            else:
                away_players.append(player_data)

        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "home_players": home_players,
            "away_players": away_players
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/batting/add", methods=["POST"])
def add_match_batting():
    data = request.get_json()
    records = data.get("records")

    if not records or len(records) == 0:
        return jsonify({"success": False, "error": "沒有有效的打擊數據可以更新"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        for r in records:
            record_id = r.get("record_id")
            if not record_id:
                continue

            at_bats = r.get("at_bats", 0)
            plate_appearance = r.get("plate_appearance", 0)
            hits = r.get("hits", 0)
            doubles = r.get("doubles", 0)
            triples = r.get("triples", 0)
            home_runs = r.get("home_runs", 0)
            strikeouts = r.get("strikeouts", 0)
            walks = r.get("walks", 0)
            hit_by_pitch = r.get("hit_by_pitch", 0)
            sacrifice_flies = r.get("sacrifice_flies", 0)
            double_play = r.get("double_play", 0)
            triple_play = r.get("triple_play", 0)
            rbis = r.get("rbis", 0)
            runs = r.get("runs", 0)
            stolen_bases = r.get("stolen_bases", 0)
            caught_stealing = r.get("caught_stealing", 0)
            remarks = r.get("remarks", "")

            # 檢查是否已存在
            cur.execute("SELECT 1 FROM BattingRecord WHERE record_id = %s", (record_id,))
            exists = cur.fetchone()

            if exists:
                cur.execute("""
                    UPDATE BattingRecord
                    SET at_bats=%s, plate_appearance=%s, hits=%s, doubles=%s, triples=%s,
                        home_runs=%s, strikeouts=%s, walks=%s, hit_by_pitch=%s, sacrifice_flies=%s,
                        double_play=%s, triple_play=%s, rbis=%s, runs=%s, stolen_bases=%s,
                        caught_stealing=%s, remarks=%s
                    WHERE record_id=%s
                """, (at_bats, plate_appearance, hits, doubles, triples, home_runs, strikeouts, walks,
                      hit_by_pitch, sacrifice_flies, double_play, triple_play, rbis, runs, stolen_bases,
                      caught_stealing, remarks, record_id))
            else:
                cur.execute("""
                    INSERT INTO BattingRecord (
                        record_id, at_bats, plate_appearance, hits, doubles, triples, home_runs,
                        strikeouts, walks, hit_by_pitch, sacrifice_flies, double_play, triple_play,
                        rbis, runs, stolen_bases, caught_stealing, remarks
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (record_id, at_bats, plate_appearance, hits, doubles, triples, home_runs,
                      strikeouts, walks, hit_by_pitch, sacrifice_flies, double_play, triple_play,
                      rbis, runs, stolen_bases, caught_stealing, remarks))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "打擊數據已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/pitching", methods=["GET"])
def get_match_pitching():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 取得主客隊
        cur.execute("SELECT home_team_id, away_team_id FROM Match WHERE match_id = %s", (match_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "找不到比賽"})
        home_team_id, away_team_id = row

        # 查球員及投球紀錄
        cur.execute("""
            SELECT mp.record_id, mp.player_id, p.name, mp.position, mp.is_starting,
                   p.team_id,
                   pr.pitching_role, pr.pitch_result, pr.innings_pitched, pr.pitches, pr.batters_faced,
                   pr.strikeouts, pr.walks, pr.hit_batters, pr.hits_allowed, pr.singles, pr.doubles, pr.triples,
                   pr.home_runs, pr.runs_allowed, pr.earned_runs, pr.fly_outs, pr.ground_outs, pr.line_outs,
                   pr.stolen_bases_allowed, pr.wild_pitches, pr.balks, pr.remarks
            FROM Match_Player mp
            LEFT JOIN Player p ON mp.player_id = p.player_id
            LEFT JOIN PitchingRecord pr ON mp.record_id = pr.record_id
            WHERE mp.match_id = %s
            ORDER BY mp.position, mp.player_id
        """, (match_id,))

        home_players = []
        away_players = []

        for r in cur.fetchall():
            player_data = {
                "player_id": r[1],
                "name": r[2],
                "pitching_record": {
                    "record_id": r[0],
                    "position": r[3],
                    "is_starting": r[4],
                    "pitching_role": r[6] or "",
                    "pitch_result": r[7] or "",
                    "innings_pitched": float(r[8] or 0),
                    "pitches": r[9] or 0,
                    "batters_faced": r[10] or 0,
                    "strikeouts": r[11] or 0,
                    "walks": r[12] or 0,
                    "hit_batters": r[13] or 0,
                    "hits_allowed": r[14] or 0,
                    "singles": r[15] or 0,
                    "doubles": r[16] or 0,
                    "triples": r[17] or 0,
                    "home_runs": r[18] or 0,
                    "runs_allowed": r[19] or 0,
                    "earned_runs": r[20] or 0,
                    "fly_outs": r[21] or 0,
                    "ground_outs": r[22] or 0,
                    "line_outs": r[23] or 0,
                    "stolen_bases_allowed": r[24] or 0,
                    "wild_pitches": r[25] or 0,
                    "balks": r[26] or 0,
                    "remarks": r[27] or ""
                }
            }

            if r[5] == home_team_id:
                home_players.append(player_data)
            else:
                away_players.append(player_data)

        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "home_players": home_players,
            "away_players": away_players
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/pitching/add", methods=["POST"])
def add_match_pitching():
    data = request.get_json()
    records = data.get("records")

    if not records or len(records) == 0:
        return jsonify({"success": False, "error": "沒有有效的投球數據可以更新"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        for r in records:
            record_id = r.get("record_id")
            if not record_id:
                continue

            pitching_role = r.get("pitching_role", "")
            pitch_result = r.get("pitch_result", "")
            innings_pitched = r.get("innings_pitched", 0)
            pitches = r.get("pitches", 0)
            batters_faced = r.get("batters_faced", 0)
            strikeouts = r.get("strikeouts", 0)
            walks = r.get("walks", 0)
            hit_batters = r.get("hit_batters", 0)
            hits_allowed = r.get("hits_allowed", 0)
            singles = r.get("singles", 0)
            doubles = r.get("doubles", 0)
            triples = r.get("triples", 0)
            home_runs = r.get("home_runs", 0)
            runs_allowed = r.get("runs_allowed", 0)
            earned_runs = r.get("earned_runs", 0)
            fly_outs = r.get("fly_outs", 0)
            ground_outs = r.get("ground_outs", 0)
            line_outs = r.get("line_outs", 0)
            stolen_bases_allowed = r.get("stolen_bases_allowed", 0)
            wild_pitches = r.get("wild_pitches", 0)
            balks = r.get("balks", 0)
            remarks = r.get("remarks", "")

            # 檢查是否已存在
            cur.execute("SELECT 1 FROM PitchingRecord WHERE record_id = %s", (record_id,))
            exists = cur.fetchone()

            if exists:
                cur.execute("""
                    UPDATE PitchingRecord
                    SET pitching_role=%s, pitch_result=%s, innings_pitched=%s, pitches=%s, batters_faced=%s,
                        strikeouts=%s, walks=%s, hit_batters=%s, hits_allowed=%s, singles=%s, doubles=%s,
                        triples=%s, home_runs=%s, runs_allowed=%s, earned_runs=%s, fly_outs=%s, ground_outs=%s,
                        line_outs=%s, stolen_bases_allowed=%s, wild_pitches=%s, balks=%s, remarks=%s
                    WHERE record_id=%s
                """, (pitching_role, pitch_result, innings_pitched, pitches, batters_faced,
                      strikeouts, walks, hit_batters, hits_allowed, singles, doubles,
                      triples, home_runs, runs_allowed, earned_runs, fly_outs, ground_outs,
                      line_outs, stolen_bases_allowed, wild_pitches, balks, remarks, record_id))
            else:
                cur.execute("""
                    INSERT INTO PitchingRecord (
                        record_id, pitching_role, pitch_result, innings_pitched, pitches, batters_faced,
                        strikeouts, walks, hit_batters, hits_allowed, singles, doubles, triples,
                        home_runs, runs_allowed, earned_runs, fly_outs, ground_outs, line_outs,
                        stolen_bases_allowed, wild_pitches, balks, remarks
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (record_id, pitching_role, pitch_result, innings_pitched, pitches, batters_faced,
                      strikeouts, walks, hit_batters, hits_allowed, singles, doubles, triples,
                      home_runs, runs_allowed, earned_runs, fly_outs, ground_outs, line_outs,
                      stolen_bases_allowed, wild_pitches, balks, remarks))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "投球數據已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/fielding", methods=["GET"])
def get_match_fielding():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"success": False, "error": "缺少 match_id"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 取得主客隊
        cur.execute("SELECT home_team_id, away_team_id FROM Match WHERE match_id = %s", (match_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "找不到比賽"})
        home_team_id, away_team_id = row

        # 查球員及守備紀錄
        cur.execute("""
            SELECT mp.record_id, mp.player_id, p.name, mp.position, mp.is_starting, p.team_id,
                   fr.fielding_chances, fr.putouts, fr.assists, fr.errors, fr.remarks
            FROM Match_Player mp
            LEFT JOIN Player p ON mp.player_id = p.player_id
            LEFT JOIN FieldingRecord fr ON mp.record_id = fr.record_id
            WHERE mp.match_id = %s
            ORDER BY mp.position, mp.player_id
        """, (match_id,))

        home_players = []
        away_players = []

        for r in cur.fetchall():
            player_data = {
                "player_id": r[1],
                "name": r[2],
                "fielding_record": {
                    "record_id": r[0],
                    "position": r[3],
                    "is_starting": r[4],
                    "fielding_chances": r[6] or 0,
                    "putouts": r[7] or 0,
                    "assists": r[8] or 0,
                    "errors": r[9] or 0,
                    "remarks": r[10] or ""
                }
            }

            if r[5] == home_team_id:
                home_players.append(player_data)
            else:
                away_players.append(player_data)

        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "home_players": home_players,
            "away_players": away_players
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/admin/match/fielding/add", methods=["POST"])
def add_match_fielding():
    data = request.get_json()
    records = data.get("records")

    if not records or len(records) == 0:
        return jsonify({"success": False, "error": "沒有有效的守備數據可以更新"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        for r in records:
            record_id = r.get("record_id")
            if not record_id:
                continue

            fielding_chances = r.get("fielding_chances", 0)
            putouts = r.get("putouts", 0)
            assists = r.get("assists", 0)
            errors = r.get("errors", 0)
            remarks = r.get("remarks", "")

            # 檢查是否已存在
            cur.execute("SELECT 1 FROM FieldingRecord WHERE record_id = %s", (record_id,))
            exists = cur.fetchone()

            if exists:
                cur.execute("""
                    UPDATE FieldingRecord
                    SET fielding_chances=%s, putouts=%s, assists=%s, errors=%s, remarks=%s
                    WHERE record_id=%s
                """, (fielding_chances, putouts, assists, errors, remarks, record_id))
            else:
                cur.execute("""
                    INSERT INTO FieldingRecord (record_id, fielding_chances, putouts, assists, errors, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (record_id, fielding_chances, putouts, assists, errors, remarks))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "守備數據已更新"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
