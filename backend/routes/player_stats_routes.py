from flask import Blueprint, request, jsonify
import psycopg2
from config import DB_CONFIG

playerstats_bp = Blueprint("playerstats_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@playerstats_bp.route("/search/player_stats", methods=["POST"])
def search_player_stats():
    data = request.json
    player_name = data.get("player_name", "").strip()
    start_date = data.get("start_date", "").strip()
    end_date = data.get("end_date", "").strip()

    if not player_name or not start_date or not end_date:
        return jsonify({"success": False, "error": "請輸入完整的查詢資訊（球員姓名、起始日、結束日）"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                p.player_id,
                p.name AS player_name,
                SUM(COALESCE(b.at_bats, 0)) AS total_at_bats,
                SUM(COALESCE(b.plate_appearance, 0)) AS total_plate_appearance,
                SUM(COALESCE(b.hits, 0)) AS total_hits,
                SUM(COALESCE(b.doubles, 0)) AS total_doubles,
                SUM(COALESCE(b.triples, 0)) AS total_triples,
                SUM(COALESCE(b.home_runs, 0)) AS total_home_runs,
                SUM(COALESCE(b.rbis, 0)) AS total_rbis,
                SUM(COALESCE(b.runs, 0)) AS total_runs,
                SUM(COALESCE(b.strikeouts, 0)) AS total_batting_strikeouts,
                SUM(COALESCE(b.walks, 0)) AS total_walks,
                SUM(COALESCE(b.hit_by_pitch, 0)) AS total_hbp,
                SUM(COALESCE(b.stolen_bases, 0)) AS total_stolen_bases,
                SUM(COALESCE(b.caught_stealing, 0)) AS total_caught_stealing,
                SUM(COALESCE(pr.innings_pitched, 0)) AS total_innings_pitched,
                SUM(COALESCE(pr.pitches, 0)) AS total_pitches,
                SUM(COALESCE(pr.batters_faced, 0)) AS total_batters_faced,
                SUM(COALESCE(pr.strikeouts, 0)) AS total_pitching_strikeouts,
                SUM(COALESCE(pr.walks, 0)) AS total_pitching_walks,
                SUM(COALESCE(pr.hits_allowed, 0)) AS total_hits_allowed,
                SUM(COALESCE(pr.home_runs, 0)) AS total_pitching_home_runs,
                SUM(COALESCE(pr.runs_allowed, 0)) AS total_runs_allowed,
                SUM(COALESCE(pr.earned_runs, 0)) AS total_earned_runs,
                SUM(COALESCE(f.fielding_chances, 0)) AS total_fielding_chances,
                SUM(COALESCE(f.putouts, 0)) AS total_putouts,
                SUM(COALESCE(f.assists, 0)) AS total_assists,
                SUM(COALESCE(f.errors, 0)) AS total_errors
            FROM player p
            JOIN match_player mp ON mp.player_id = p.player_id
            JOIN match m ON m.match_id = mp.match_id
            LEFT JOIN battingrecord b ON b.record_id = mp.record_id
            LEFT JOIN pitchingrecord pr ON pr.record_id = mp.record_id
            LEFT JOIN fieldingrecord f ON f.record_id = mp.record_id
            WHERE p.name ILIKE %s
              AND m.date BETWEEN %s AND %s
            GROUP BY p.player_id, p.name
            ORDER BY p.name;
        """

        cur.execute(query, (f"%{player_name}%", start_date, end_date))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({"success": False, "error": "查無此球員在指定期間內的紀錄"})

        result_list = []
        for row in rows:
            result_list.append({
                "player_id": row[0],
                "player_name": row[1],
                "total_at_bats": row[2],
                "total_plate_appearance": row[3],
                "total_hits": row[4],
                "total_doubles": row[5],
                "total_triples": row[6],
                "total_home_runs": row[7],
                "total_rbis": row[8],
                "total_runs": row[9],
                "total_batting_strikeouts": row[10],
                "total_walks": row[11],
                "total_hbp": row[12],
                "total_stolen_bases": row[13],
                "total_caught_stealing": row[14],
                "total_innings_pitched": row[15],
                "total_pitches": row[16],
                "total_batters_faced": row[17],
                "total_pitching_strikeouts": row[18],
                "total_pitching_walks": row[19],
                "total_hits_allowed": row[20],
                "total_pitching_home_runs": row[21],
                "total_runs_allowed": row[22],
                "total_earned_runs": row[23],
                "total_fielding_chances": row[24],
                "total_putouts": row[25],
                "total_assists": row[26],
                "total_errors": row[27],
            })

        return jsonify({"success": True, "result": result_list})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})