"""
JWT Authentication for SAFEGUARD AI
- Email/password signup & login
- JWT token generation & verification
- SQLite user store (persists across restarts)
- Password hashing with bcrypt
"""
import os
import sqlite3
import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import bcrypt
from jose import JWTError, jwt

# ── Config ──────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "safeguard-ai-secret-key-change-in-production-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 72
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# ── Password Hashing ────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# ── Security ────────────────────────────────────────────────
security = HTTPBearer()

# ── SQLite Setup ────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'worker',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[auth] SQLite database ready at {DB_PATH}")

init_db()

def get_user(email: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(email: str, hashed_password: str, role: str) -> dict:
    created_at = datetime.datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO users (email, hashed_password, role, created_at) VALUES (?, ?, ?, ?)",
        (email.lower().strip(), hashed_password, role, created_at)
    )
    conn.commit()
    conn.close()
    return {"email": email.lower().strip(), "role": role, "created_at": created_at}

# ── Models ──────────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: str
    password: str
    role: str = "worker"  # worker, safety_officer, admin

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    role: str
    created_at: str

# ── Token Creation ──────────────────────────────────────────
def create_token(email: str, role: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ── Current User Dependency ─────────────────────────────────
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    return {"email": payload["sub"], "role": payload.get("role", "worker")}

# ── Auth Endpoints ──────────────────────────────────────────
async def signup(req: SignupRequest):
    """Register a new user."""
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = get_user(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(req.password)
    user_data = create_user(req.email, hashed, req.role)

    token = create_token(user_data["email"], user_data["role"])
    return {
        "token": token,
        "user": {
            "email": user_data["email"],
            "role": user_data["role"],
            "created_at": user_data["created_at"],
        }
    }

async def login(req: LoginRequest):
    """Login with email and password."""
    user = get_user(req.email)

    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["email"], user["role"])
    return {
        "token": token,
        "user": {
            "email": user["email"],
            "role": user["role"],
            "created_at": user.get("created_at", ""),
        }
    }

async def get_me(user=Depends(get_current_user)):
    """Get current user info from token."""
    return {"user": user}
