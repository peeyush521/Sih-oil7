"""
JWT Authentication for SAFEGUARD AI
- Email/password signup & login
- JWT token generation & verification
- MongoDB user store
- Password hashing with bcrypt
"""
import os
import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient

# ── Config ──────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "safeguard-ai-secret-key-change-in-production-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 72

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "safeguard_ai"

# ── Password Hashing ────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ── Security ────────────────────────────────────────────────
security = HTTPBearer()

# ── MongoDB ─────────────────────────────────────────────────
_client: Optional[AsyncIOMotorClient] = None
_db = None

async def get_db():
    global _client, _db
    if _db is None:
        try:
            _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            await _client.admin.command("ping")
            _db = _client[DB_NAME]
            print("[auth] Connected to MongoDB")
        except Exception as e:
            print(f"[auth] MongoDB unavailable ({e}), using in-memory user store")
            _db = None
    return _db

# ── In-Memory Fallback ──────────────────────────────────────
_users_store = {}  # email -> {email, hashed_password, role, created_at}

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
    
    db = await get_db()
    hashed = hash_password(req.password)
    user_data = {
        "email": req.email.lower().strip(),
        "hashed_password": hashed,
        "role": req.role,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    
    if db is not None:
        # MongoDB
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        await db.users.insert_one(user_data)
    else:
        # In-memory fallback
        if user_data["email"] in _users_store:
            raise HTTPException(status_code=400, detail="Email already registered")
        _users_store[user_data["email"]] = user_data
    
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
    email = req.email.lower().strip()
    
    db = await get_db()
    user = None
    
    if db is not None:
        user = await db.users.find_one({"email": email})
    else:
        user = _users_store.get(email)
    
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
