from flask import Blueprint, request, jsonify
from config import DB_CONFIG
import psycopg2

match_bp = Blueprint("matches_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@match_bp.route("/search/matches", methods=["POST"])
def search_matches():
    data = request.json
    date = data.get("date")
    team_name = data.get("team_name")

    if not date:
        return jsonify({"success": False, "error": "日期不可為空"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
        SELECT
            m.match_id,
            m.date,
            m.start_time,
            m.location,
            m.status,
            m.weather,
            m.temperature,
            m.attendance,
            ht.team_name AS home_team_name,
            m.home_score,
            at.team_name AS away_team_name,
            m.away_score
        FROM match m
        JOIN team ht ON m.home_team_id = ht.team_id
        JOIN team at ON m.away_team_id = at.team_id
        WHERE m.date = %s
        """

        params = [date]

        if team_name:
            query += " AND (ht.team_name = %s OR at.team_name = %s)"
            params.extend([team_name, team_name])

        query += " ORDER BY m.start_time, m.match_id"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            match = {
                "match_id": row[0],
                "date": row[1].isoformat(),
                "start_time": row[2].strftime("%H:%M:%S"),
                "location": row[3],
                "status": row[4],
                "weather": row[5],
                "temperature": row[6],
                "attendance": row[7],
                "home_team_name": row[8],
                "home_score": row[9],
                "away_team_name": row[10],
                "away_score": row[11]
            }
            result.append(match)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
