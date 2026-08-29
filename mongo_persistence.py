"""
MongoDB Persistence Layer for SIF Precursor Intelligence.
Provides persistent storage for reports, risk scores, and audit logs.
Falls back to JSON file if MongoDB is unavailable.
"""
import os
import json
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "sif_precursor")

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        print('[mongo] Connected to MongoDB')
        return _db
    except Exception as e:
        print(f'[mongo] MongoDB unavailable ({e}), using JSON fallback')
        return None

def save_reports(reports):
    db = get_db()
    if db is None:
        _save_json(reports)
        return
    try:
        collection = db['reports']
        collection.delete_many({})
        if reports:
            cleaned = []
            for r in reports:
                entry = json.loads(json.dumps(r, default=str))
                cleaned.append(entry)
            collection.insert_many(cleaned)
        print(f'[mongo] Saved {len(reports)} reports')
    except Exception as e:
        print(f'[mongo] Save failed: {e}')
        _save_json(reports)

def load_reports():
    db = get_db()
    if db is None:
        return _load_json()
    try:
        collection = db['reports']
        docs = list(collection.find({}, {'_id': 0}))
        if docs:
            print(f'[mongo] Loaded {len(docs)} reports')
            return docs
        return _load_json()
    except Exception as e:
        print(f'[mongo] Load failed: {e}')
        return _load_json()

def save_audit_log(entry):
    db = get_db()
    if db is None:
        return
    try:
        collection = db['audit_logs']
        entry['timestamp'] = datetime.now().isoformat()
        collection.insert_one(entry)
    except Exception as e:
        print(f'[mongo] Audit log failed: {e}')

def get_audit_logs(limit=50):
    db = get_db()
    if db is None:
        return []
    try:
        collection = db['audit_logs']
        return list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))
    except Exception:
        return []

STATE_FILE = "api_state.json"

def _save_json(reports):
    try:
        serializable = [json.loads(json.dumps(r, default=str)) for r in reports]
        with open(STATE_FILE, "w") as f:
            json.dump({"total_reports": len(serializable), "reports": serializable}, f, indent=2)
    except Exception as e:
        print(f'[json] Save failed: {e}')

def _load_json():
    if not os.path.exists(STATE_FILE):
        return []
    try:
        with open(STATE_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            return data.get("reports", [])
    except Exception as e:
        print(f'[json] Load failed: {e}')
        return []
