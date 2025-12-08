import psycopg2
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

auth_bp = Blueprint("auth_bp", __name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# 註冊 API
@auth_bp.route("/register", methods=["POST"])
def register_api():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"success": False, "error": "欄位不可為空"})

    # 後端加密密碼
    hashed_password = generate_password_hash(password)

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO "User" (username, password, email)
            VALUES (%s, %s, %s)
            RETURNING user_id;
        """, (username, hashed_password, email))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "user_id": user_id})

    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        if "User_username_key" in str(e):
            return jsonify({"success": False, "error": "使用者名稱已被使用，請換一個"})
        elif "User_email_key" in str(e):
            return jsonify({"success": False, "error": "電子郵件已被使用，請換一個"})
        else:
            return jsonify({"success": False, "error": "註冊失敗，資料已存在"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 登入 API
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
            SELECT user_id, password 
            FROM "User" 
            WHERE username = %s;
        """, (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({"success": False, "error": "此帳號不存在"})

        user_id, hashed_password = user

        if not check_password_hash(hashed_password, password):
            return jsonify({"success": False, "error": "密碼錯誤"})

        return jsonify({"success": True, "user_id": user_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

'''
# 登入路由
@auth_bp.route('/login', methods=['POST'])
def login():
    db = DB_manager()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    admin_code = data.get('adminCode')

    if not username or not password:
        return jsonify({"message": "缺少帳號或密碼"}), 400

    # 使用明文密碼檢查用戶
    user = db.check_user(username, password) 

    if not user:
        return jsonify({"message": "帳號或密碼錯誤"}), 401

    # 檢查管理員碼 (如果提供了)
    is_admin = False
    if admin_code:
        is_admin = db.check_admin_code(admin_code)
        if not is_admin:
            # 即使普通用戶驗證成功，但管理員碼錯誤，也認為是登入失敗
            return jsonify({"message": "管理員碼錯誤"}), 401 
            
    # 返回用戶信息
    user_info = {"id": user[0], "username": user[1], "isAdmin": is_admin}
    return jsonify({"message": "登入成功", "user": user_info}), 200
'''