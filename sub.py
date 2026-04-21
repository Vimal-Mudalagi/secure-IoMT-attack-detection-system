# ===================== IMPORTS =====================

import paho.mqtt.client as mqtt
import json
import base64
import hashlib
import hmac
import time
import sqlite3
import os

from Crypto.Cipher import AES

# ECDSA
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# ===================== KEYS =====================

AES_KEY = b'1234567890123456'
HMAC_KEY = b'supersecretkey'

# ===================== LOAD PUBLIC KEY =====================

PUBLIC_KEY_FILE = "device_public.pem"

if not os.path.exists(PUBLIC_KEY_FILE):
    print("❌ ERROR: device_public.pem not found. Run publisher first.")
    exit()

with open(PUBLIC_KEY_FILE, "rb") as f:
    device_public_key = serialization.load_pem_public_key(f.read())

# ===================== DATABASE =====================

conn = sqlite3.connect("iomt.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS heart_rate_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    heart_rate INTEGER,
    timestamp INTEGER,
    nonce TEXT,
    encrypted_data TEXT,
    hash_value TEXT,
    hmac_value TEXT,
    signature TEXT,
    status TEXT
)
""")

conn.commit()

# ===================== REPLAY PROTECTION =====================

seen_nonces = set()
MAX_DELAY = 10  # seconds

# ===================== AES =====================

def decrypt_data(encrypted_data):
    raw = base64.b64decode(encrypted_data)

    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=iv)
    decrypted = cipher.decrypt(ciphertext)

    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode()

# ===================== HASH =====================

def compute_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# ===================== HMAC =====================

def compute_hmac(data):
    return hmac.new(HMAC_KEY, data.encode(), hashlib.sha256).hexdigest()

# ===================== SIGNATURE VERIFY =====================

def verify_signature(data, signature):
    try:
        device_public_key.verify(
            base64.b64decode(signature),
            data.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False

# ===================== DATABASE INSERT =====================

def store_data(device_id, heart_rate, timestamp, nonce,
               encrypted, hash_val, hmac_val, signature, status):

    cursor.execute("""
        INSERT INTO heart_rate_data 
        (device_id, heart_rate, timestamp, nonce, encrypted_data,
         hash_value, hmac_value, signature, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (device_id, heart_rate, timestamp, nonce,
          encrypted, hash_val, hmac_val, signature, status))

    conn.commit()

# ===================== FINAL VERIFIER =====================

def classify_packet(packet):
    """
    🔥 CORE SECURITY PIPELINE (YOUR MODULE)

    Flow:
    1. Replay Check
    2. Integrity Check (HMAC + HASH)
    3. Authentication (Signature)
    4. Decryption
    """

    encrypted = packet["encrypted_data"]
    hmac_val = packet["hmac_value"]
    hash_val = packet["hash_value"]
    signature = packet["signature"]
    nonce = packet["nonce"]
    timestamp = packet["timestamp"]

    # ================= REPLAY =================
    if nonce in seen_nonces:
        return "REPLAY", None

    if abs(int(time.time()) - timestamp) > MAX_DELAY:
        return "REPLAY", None

    seen_nonces.add(nonce)

    # ================= HMAC =================
    if compute_hmac(encrypted) != hmac_val:
        return "TAMPERED", None

    # ================= HASH =================
    if compute_hash(encrypted) != hash_val:
        return "TAMPERED", None

    # ================= SIGNATURE =================
    if not verify_signature(encrypted, signature):
        return "UNAUTHORIZED", None

    # ================= DECRYPT =================
    try:
        heart_rate = int(decrypt_data(encrypted))
        return "VALID", heart_rate
    except:
        return "ERROR", None


# ===================== MQTT MESSAGE =====================

def on_message(client, userdata, msg):
    packet = json.loads(msg.payload.decode())

    print("\n📦 FULL PACKET RECEIVED:")
    print(json.dumps(packet, indent=2))

    device_id = packet["device_id"]

    # 🔥 FINAL CLASSIFICATION
    status, heart_rate = classify_packet(packet)

    # ================= DISPLAY =================
    if status == "VALID":
        print(f"💓 HEART RATE: {heart_rate}")
    else:
        print(f"⚠️ STATUS: {status}")

    # ================= STORE =================
    store_data(
        device_id,
        heart_rate,
        packet["timestamp"],
        packet["nonce"],
        packet["encrypted_data"],
        packet["hash_value"],
        packet["hmac_value"],
        packet["signature"],
        status
    )

    print(f"💾 STORED ({status})")

# ===================== MQTT =====================

client = mqtt.Client()
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.subscribe("iot/heart_rate")

print("📡 Final Verifier Running (Attack Detection Active)")

client.loop_forever()