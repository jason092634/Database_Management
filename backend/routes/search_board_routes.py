from flask import Blueprint, request, jsonify
import redis

# ---------------------------
#  Redis 連線設定
# ---------------------------
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True      # 讓回傳字串自動變為 str
)

searchboard_bp = Blueprint("searchboard", __name__)

# ===========================
#  📌 1. 通用：更新查詢次數
# ===========================
@searchboard_bp.route("/api/query-log", methods=["POST"])
def update_query_count():
    data = request.get_json()

    if "type" not in data or "id" not in data:
        return jsonify({"error": "Missing 'type' or 'id'"}), 400

    query_type = data["type"]
    item_id = data["id"]

    redis_key = f"ranking:{query_type}"

    if query_type not in ["player", "team", "match"]:
        return jsonify({"error": "Invalid type. Must be player/team/match"}), 400

    r.zincrby(redis_key, 1, item_id)

    return jsonify({
        "message": "Query count updated",
        "type": query_type,
        "id": item_id
    }), 200


# ===========================
#  📌 2. 取得排行榜 Top-K
# ===========================
@searchboard_bp.route("/api/ranking/<category>", methods=["GET"])
def get_ranking(category):
    if category not in ["players", "teams", "matches"]:
        return jsonify({"error": "Category must be players/teams/matches"}), 400

    # 前端用複數，Redis key 用單數
    key_map = {
        "players": "player",
        "teams": "team",
        "matches": "match"
    }

    redis_key = f"ranking:{key_map[category]}"

    top = request.args.get("top", default=10, type=int)

    data = r.zrevrange(redis_key, 0, top - 1, withscores=True)

    # 格式化
    formatted = []
    for member, score in data:
        formatted.append({
            key_map[category] + "_id": member,
            "count": int(score)
        })

    return jsonify({
        "type": key_map[category],
        "top": top,
        "data": formatted
    }), 200


# ===========================
#  📌 3. 查詢某個 ID 的查詢次數
# ===========================
@searchboard_bp.route("/api/ranking/count", methods=["GET"])
def get_single_count():
    query_type = request.args.get("type")
    item_id = request.args.get("id")

    if query_type not in ["player", "team", "match"]:
        return jsonify({"error": "Invalid type"}), 400

    if item_id is None:
        return jsonify({"error": "Missing id"}), 400

    redis_key = f"ranking:{query_type}"

    score = r.zscore(redis_key, item_id)
    score = int(score) if score is not None else 0

    return jsonify({
        "type": query_type,
        "id": item_id,
        "count": score
    })


# ===========================
#  📌 4. 清空排行榜
# ===========================
@searchboard_bp.route("/api/ranking/<category>", methods=["DELETE"])
def clear_ranking(category):
    if category not in ["player", "team", "match"]:
        return jsonify({"error": "Invalid category"}), 400

    redis_key = f"ranking:{category}"
    r.delete(redis_key)

    return jsonify({
        "message": f"{category} ranking cleared"
    }), 200