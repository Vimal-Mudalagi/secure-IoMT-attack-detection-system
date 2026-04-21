import os
import paho.mqtt.client as mqtt
import json
import time
import random
import uuid
import base64
import hashlib
import hmac

from Crypto.Cipher import AES

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# ===================== KEYS =====================

AES_KEY = b'1234567890123456'
HMAC_KEY = b'supersecretkey'

PRIVATE_KEY_FILE = "device_private.pem"
PUBLIC_KEY_FILE = "device_public.pem"

# ===================== ECC KEY HANDLING (FIXED) =====================
# WHY ECC?
# - small key size (lightweight for IoMT devices)
# - strong security vs RSA
# - used for digital identity (sign/verify device authenticity)

if os.path.exists(PRIVATE_KEY_FILE):
    print("🔐 Loading existing device key...")
    with open(PRIVATE_KEY_FILE, "rb") as f:
        device_private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
else:
    print("🆕 Generating new device key...")
    device_private_key = ec.generate_private_key(ec.SECP256R1())

    # save private key
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(device_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # save public key
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(device_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("✅ Keys saved")

# ===================== AES (CBC MODE - SIMPLE IoMT MODE) =====================
# WHY CBC?
# - lightweight
# - widely used in embedded systems
# - deterministic padding-based encryption for demo

def encrypt_data(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    iv = cipher.iv

    data_bytes = str(data).encode()

    pad_len = 16 - len(data_bytes) % 16
    data_bytes += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data_bytes)

    return base64.b64encode(iv + ciphertext).decode()

# ===================== HMAC (INTEGRITY + AUTHENTICATION) =====================

def compute_hmac(data):
    return hmac.new(HMAC_KEY, data.encode(), hashlib.sha256).hexdigest()

# ===================== ECDSA SIGN (DEVICE AUTHENTICITY) =====================
# WHY ECDSA?
# - proves packet came from legit device
# - prevents spoofing
# - lightweight digital signature system

def sign_data(data):
    signature = device_private_key.sign(
        data.encode(),
        ec.ECDSA(hashes.SHA256())
    )
    return base64.b64encode(signature).decode()

# ===================== MQTT =====================

client = mqtt.Client()
client.connect("localhost", 1883, 60)

while True:
    heart_rate = random.randint(60, 100)

    # STEP 1: Encrypt
    encrypted_hr = encrypt_data(heart_rate)

    # STEP 2: Integrity (HMAC)
    hmac_value = compute_hmac(encrypted_hr)

    # STEP 3: Identity (ECDSA signature)
    signature = sign_data(encrypted_hr)

    # STEP 4: FULL PACKET (NO FIELDS REMOVED)
    packet = {
        "device_id": "HRM_01",
        "timestamp": int(time.time()),
        "nonce": str(uuid.uuid4()),
        "encrypted_data": encrypted_hr,
        "encrypted_key": None,
        "hash_value": hashlib.sha256(encrypted_hr.encode()).hexdigest(),
        "hmac_value": hmac_value,
        "signature": signature
    }

    # IMPORTANT: full visibility maintained
    print("\n📦 FULL PACKET SENT:")
    print(json.dumps(packet, indent=2))

    client.publish("iot/heart_rate", json.dumps(packet))

    time.sleep(2)
