import os
from flask import Flask, render_template, request, redirect, url_for, abort, session
import bcrypt  # Direct bcrypt import instead of passlib
from email_validator import validate_email, EmailNotValidError
from flask_session import Session
import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
import requests
import hashlib

# load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Config from env
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/klickon_auth")
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_SITEKEY = os.environ.get("RECAPTCHA_SITE_KEY", "")

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Redis-backed sessions
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(REDIS_URL)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_KEY_PREFIX"] = "session:"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # HTTPS yoxdursa False qoy

# ✅ Fix: RedisSessionInterface override (cookie value bytes → str)
from flask_session.sessions import RedisSessionInterface

class FixedRedisSessionInterface(RedisSessionInterface):
    def _generate_sid(self):
        sid = super()._generate_sid()
        if isinstance(sid, bytes):
            return sid.decode("utf-8")
        return sid

Session(app)
app.session_interface = FixedRedisSessionInterface(
    app.config["SESSION_REDIS"], 
    app.config.get("SESSION_KEY_PREFIX", "session:")
)


# Rate limiter - Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=REDIS_URL
)

# MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
users_coll = db.get_collection("users")

def verify_recaptcha(response_token, remote_ip=None):
    if not RECAPTCHA_SECRET:
        return False
    payload = {"secret": RECAPTCHA_SECRET, "response": response_token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload, timeout=10)
        data = r.json()
        return data.get("success", False)
    except Exception:
        return False

def safe_hash_password(password):
    """
    Direct bcrypt usage with proper handling
    """
    try:
        password_str = str(password)
        password_bytes = password_str.encode('utf-8')
        
        if len(password_bytes) > 72:
            sha256_hash = hashlib.sha256(password_bytes).hexdigest()
            password_bytes = sha256_hash.encode('utf-8')
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
        
    except Exception as e:
        print(f"Hash error: {e}")
        try:
            password_str = str(password)
            sha256_hash = hashlib.sha256(password_str.encode('utf-8')).hexdigest()
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e2:
            print(f"Fallback hash error: {e2}")
            return None

def safe_verify_password(password, stored_hash):
    try:
        password_str = str(password)
        password_bytes = password_str.encode('utf-8')
        stored_hash_bytes = stored_hash.encode('utf-8')
        
        if len(password_bytes) <= 72:
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                return True
        
        sha256_hash = hashlib.sha256(password_bytes).hexdigest()
        return bcrypt.checkpw(sha256_hash.encode('utf-8'), stored_hash_bytes)
        
    except Exception as e:
        print(f"Verify error: {e}")
        return False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", message=None, recaptcha_sitekey=RECAPTCHA_SITEKEY)

@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    recaptcha_token = request.form.get("g-recaptcha-response", "")

    if not username or not email or not password:
        return render_template("index.html", message="Zəhmət olmasa bütün sahələri doldurun.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    if not verify_recaptcha(recaptcha_token, request.remote_addr):
        return render_template("index.html", message="reCAPTCHA doğrulanmadı. Yenidən cəhd edin.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return render_template("index.html", message="E-mail formatı düzgün deyil.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    if len(password) < 8:
        return render_template("index.html", message="Şifrə ən az 8 simvol olmalıdır.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    if len(password) > 200:
        return render_template("index.html", message="Şifrə çox uzundur. Maksimum 200 simvol ola bilər.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    try:
        pw_hash = safe_hash_password(password)
        if not pw_hash:
            raise Exception("Hash creation failed")
    except Exception as e:
        print(f"Password hashing error: {e}")
        return render_template("index.html", message="Sistem xətası baş verdi. Yenidən cəhd edin.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    try:
        users_coll.insert_one({"username": username, "email": email, "password_hash": pw_hash})
        print(f"User registered successfully: {email}")
    except Exception as e:
        print(f"Database insert error: {e}")
        return render_template("index.html", message="Bu e-mail ilə artıq qeydiyyat mövcuddur.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    return render_template("index.html", message="Qeydiyyat uğurludur. İndi daxil ola bilərsiniz.", recaptcha_sitekey=RECAPTCHA_SITEKEY)

@app.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    email = (request.form.get("email_login") or "").strip().lower()
    password = request.form.get("password_login") or ""
    
    if not email or not password:
        return render_template("index.html", message="E-mail və şifrə sahələrini doldurun.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
    
    try:
        user = users_coll.find_one({"email": email})
        if not user:
            return render_template("index.html", message="E-mail və ya şifrə yanlışdır.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
        
        stored_hash = user.get("password_hash")
        if not safe_verify_password(password, stored_hash):
            return render_template("index.html", message="E-mail və ya şifrə yanlışdır.", recaptcha_sitekey=RECAPTCHA_SITEKEY)
        
        session.clear()
        session["user_id"] = str(user.get("_id"))
        session["username"] = user.get("username")
        session["email"] = user.get("email")
        
        print(f"User logged in successfully: {email}")
        return render_template("dashboard.html", user={"username": user.get("username"), "email": user.get("email")})
    except Exception as e:
        print(f"Login error: {e}")
        return render_template("index.html", message="Sistem xətası baş verdi. Yenidən cəhd edin.", recaptcha_sitekey=RECAPTCHA_SITEKEY)

@app.route("/dashboard", methods=["GET"])
def dashboard_get():
    if not session.get("user_id"):
        abort(403)
    user = {"username": session.get("username"), "email": session.get("email")}
    return render_template("dashboard.html", user=user)

@app.route("/logout", methods=["POST","GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))

def ensure_indexes():
    try:
        users_coll.create_index("email", unique=True)
        print("MongoDB indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

if __name__ == "__main__":
    ensure_indexes()
    print("🚀 Klickon Auth Server starting...")
    print(f"📊 Redis URL: {REDIS_URL}")
    print(f"🗄️  MongoDB URI: {MONGO_URI}")
    print(f"🔐 reCAPTCHA configured: {'✅' if RECAPTCHA_SITEKEY else '❌'}")
    app.run(host="0.0.0.0", port=5000, debug=True)
