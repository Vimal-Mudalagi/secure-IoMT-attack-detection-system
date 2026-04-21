import paho.mqtt.client as mqtt
import json
import time
import uuid
import base64
import hashlib
import hmac

from Crypto.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

# ===================== KEYS =====================

AES_KEY = b'1234567890123456'
HMAC_KEY = b'supersecretkey'

# Legit device key (for VALID + REPLAY + TAMPER base)
with open("device_private.pem", "rb") as f:
    legit_private_key = serialization.load_pem_private_key(f.read(), password=None)

# Fake device key (for UNAUTHORIZED attack)
fake_private_key = ec.generate_private_key(ec.SECP256R1())

# ===================== FUNCTIONS =====================

def encrypt_data(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    iv = cipher.iv

    data_bytes = str(data).encode()
    pad_len = 16 - len(data_bytes) % 16
    data_bytes += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data_bytes)
    return base64.b64encode(iv + ciphertext).decode()

def compute_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def compute_hmac(data):
    return hmac.new(HMAC_KEY, data.encode(), hashlib.sha256).hexdigest()

def sign_data(data, private_key):
    sig = private_key.sign(data.encode(), ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(sig).decode()

# ===================== MQTT =====================

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("\n🚀 STARTING FULL ATTACK DEMO...\n")

# =========================================================
# 1. ✅ NORMAL PACKET (VALID)
# =========================================================

encrypted = encrypt_data(72)

packet = {
    "device_id": "HRM_01",
    "timestamp": int(time.time()),
    "nonce": str(uuid.uuid4()),
    "encrypted_data": encrypted,
    "encrypted_key": None,
    "hash_value": compute_hash(encrypted),
    "hmac_value": compute_hmac(encrypted),
    "signature": sign_data(encrypted, legit_private_key)
}

client.publish("iot/heart_rate", json.dumps(packet))
print("✅ VALID packet sent")
time.sleep(3)

# =========================================================
# 2. 🔴 REPLAY ATTACK
# =========================================================

print("\n🚨 REPLAY ATTACK")

payload = json.dumps(packet)

for i in range(2):
    client.publish("iot/heart_rate", payload)
    print(f"Replay sent {i+1}")
    time.sleep(2)

time.sleep(3)

# =========================================================
# 3. 🟠 TAMPERING ATTACK
# =========================================================

print("\n🚨 TAMPERING ATTACK")

encrypted = encrypt_data(85)

tampered = encrypted[:-3] + "XYZ"  # break ciphertext

packet = {
    "device_id": "HRM_01",
    "timestamp": int(time.time()),
    "nonce": str(uuid.uuid4()),
    "encrypted_data": tampered,  # 🔥 tampered
    "encrypted_key": None,
    "hash_value": compute_hash(encrypted),  # original
    "hmac_value": compute_hmac(encrypted),  # original
    "signature": sign_data(encrypted, legit_private_key)
}

client.publish("iot/heart_rate", json.dumps(packet))
print("Tampered packet sent")

time.sleep(3)

# =========================================================
# 4. 🔵 UNAUTHORIZED DEVICE
# =========================================================

print("\n🚨 UNAUTHORIZED DEVICE ATTACK")

encrypted = encrypt_data(90)

packet = {
    "device_id": "FAKE_DEVICE",
    "timestamp": int(time.time()),
    "nonce": str(uuid.uuid4()),
    "encrypted_data": encrypted,
    "encrypted_key": None,
    "hash_value": compute_hash(encrypted),
    "hmac_value": compute_hmac(encrypted),
    "signature": sign_data(encrypted, fake_private_key)  # 🔥 fake sign
}

client.publish("iot/heart_rate", json.dumps(packet))
print("Unauthorized packet sent")

print("\n🎯 DEMO COMPLETE\n")