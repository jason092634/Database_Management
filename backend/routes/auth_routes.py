import psycopg2
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG, ADMIN_SECRET_KEY

auth_bp = Blueprint("auth_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")  # 前端已 hash
    email = data.get("email")
    admin_key = data.get("admin_key", "")

    if not username or not password or not email:
        return jsonify({"success": False, "error": "所有欄位皆需填寫"})

    # 判斷身份
    role = "User"
    if admin_key:
        if admin_key == ADMIN_SECRET_KEY:
            role = "Admin"
        else:
            return jsonify({"success": False, "error": "Admin 密鑰錯誤"})

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 檢查 username 是否存在
        cur.execute('SELECT COUNT(*) FROM "User" WHERE username = %s', (username,))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "使用者名稱已存在"})

        # 檢查 email 是否存在
        cur.execute('SELECT COUNT(*) FROM "User" WHERE email = %s', (email,))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "電子郵件已存在"})

        # 新增使用者
        cur.execute(
            'INSERT INTO "User" (username, password, email, role) VALUES (%s, %s, %s, %s)',
            (username, password, email, role)
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "role": role})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@auth_bp.route("/login", methods=["POST"])
def login_api():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "欄位不可為空"})

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, password, role
            FROM "User"
            WHERE username = %s;
        """, (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({"success": False, "error": "此帳號不存在"})

        user_id, hashed_password, role = user

        if password != hashed_password:
            return jsonify({"success": False, "error": "密碼錯誤"})

        return jsonify({
            "success": True,
            "user_id": user_id,
            "role": role
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
