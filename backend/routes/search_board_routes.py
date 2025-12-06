from flask import Blueprint, request, jsonify, current_app
import psycopg2
from config import DB_CONFIG, REDIS_CONFIG

searchboard_bp = Blueprint("searchboard", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ------------------------------------
# 取得排行榜（包含名稱）
# ------------------------------------
@searchboard_bp.route("/api/ranking/<category>", methods=["GET"])
def get_ranking(category):
    if category not in ["players", "teams", "matches"]:
        return jsonify({"error": "Category must be players/teams/matches"}), 400

    redis_key_map = {
        "players": "ranking:player",
        "teams": "ranking:team",
        "matches": "ranking:match"
    }
    redis_key = redis_key_map[category]

    top = request.args.get("top", default=10, type=int)
    # 取出 Redis 排行榜
    data = current_app.redis.zrevrange(redis_key, 0, top - 1, withscores=True)

    if not data:
        return jsonify({"type": category, "top": top, "data": []}), 200

    # --------------------------
    # 連 DB 取得名稱
    # --------------------------
    id_list = [int(member) for member, score in data]

    try:
        conn = get_connection()
        cur = conn.cursor()

        result = []
        if category == "players":
            cur.execute(
                "SELECT player_id, name FROM player WHERE player_id = ANY(%s)",
                (id_list,)
            )
            id_name_map = {str(pid): name for pid, name in cur.fetchall()}

            for member, score in data:
                result.append({
                    "player_id": member,
                    "name": id_name_map.get(member, member),
                    "count": int(score)
                })

        elif category == "teams":
            cur.execute(
                "SELECT team_id, team_name FROM team WHERE team_id = ANY(%s)",
                (id_list,)
            )
            id_name_map = {str(tid): name for tid, name in cur.fetchall()}

            for member, score in data:
                result.append({
                    "team_id": member,
                    "name": id_name_map.get(member, member),
                    "count": int(score)
                })

        elif category == "matches":
            # 可以用 home vs away 當名稱
            cur.execute(
                """
                SELECT m.match_id, ht.team_name, at.team_name
                FROM match m
                JOIN team ht ON m.home_team_id = ht.team_id
                JOIN team at ON m.away_team_id = at.team_id
                WHERE m.match_id = ANY(%s)
                """,
                (id_list,)
            )
            id_name_map = {str(mid): f"{home} vs {away}" for mid, home, away in cur.fetchall()}

            for member, score in data:
                result.append({
                    "match_id": member,
                    "name": id_name_map.get(member, member),
                    "count": int(score)
                })

        conn.close()
        return jsonify({
            "type": category,
            "top": top,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------
# 清空排行榜
# ------------------------------------
@searchboard_bp.route("/api/ranking/<category>", methods=["DELETE"])
def clear_ranking(category):
    if category not in ["players", "teams", "matches"]:
        return jsonify({"error": "Invalid category"}), 400

    redis_key_map = {
        "players": "ranking:player",
        "teams": "ranking:team",
        "matches": "ranking:match"
    }
    redis_key = redis_key_map[category]

    current_app.redis.delete(redis_key)
    return jsonify({"message": f"{category} ranking cleared"}), 200