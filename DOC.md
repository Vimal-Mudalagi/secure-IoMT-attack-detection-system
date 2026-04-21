```markdown
# 📘 IoMT Security Framework — Detailed Documentation

---

## ⭐ Notes
This project is built for **learning, demonstration, and academic purposes** only.

---

## 1. 🧠 Overview

This project implements a secure communication pipeline for **Internet of Medical Things (IoMT)** devices using multiple cryptographic techniques.

**Goals:**
- Protect sensitive medical data
- Detect various cyber attacks
- Simulate a real-world IoMT system

---

## 2. 🏗️ System Architecture

```
[ IoMT Device ]
        ↓
  AES Encryption
        ↓
   Hash + HMAC
        ↓
 ECDSA Signature
        ↓
   MQTT Broker
        ↓
[ Gateway (Subscriber) ]
        ↓
 Verification Pipeline
        ↓
  Database (SQLite)
        ↓
   Flask Dashboard
```

---

## 3. 🔄 Workflow

### Sender Side (`pub.py`)

1. Generate heart rate data
2. Encrypt using AES
3. Compute SHA-256 hash
4. Generate HMAC
5. Sign using ECDSA
6. Build secure packet
7. Publish via MQTT

### Receiver Side (`sub.py`)

1. Receive packet from MQTT
2. Replay check (nonce + timestamp)
3. Verify HMAC
4. Verify hash
5. Verify ECDSA signature
6. Decrypt data
7. Classify packet (VALID / REPLAY / TAMPERED / UNAUTHORIZED)
8. Store in SQLite database
9. Display on Flask dashboard

---

## 4. 🔐 Cryptographic Components

### AES (Advanced Encryption Standard)
- **Purpose**: Confidentiality
- **Mode**: CBC
- Encrypts patient vital data

### SHA-256
- **Purpose**: Integrity
- Generates fixed-size hash to detect any data modification

### HMAC
- **Purpose**: Authenticity + Integrity
- Uses a shared secret key

### ECC (Elliptic Curve Cryptography)
- Lightweight public-key cryptography
- Used for digital signatures

### ECDSA
- **Purpose**: Non-repudiation & Sender Authentication
- Verifies the identity of the IoMT device

---

## 5. 📡 MQTT Protocol

- Lightweight **publish-subscribe** messaging protocol ideal for IoT
- **Topic used**: `iot/heart_rate`

**Components:**
- **Publisher** → IoMT Device (sends data)
- **Broker** → Routes messages
- **Subscriber** → Gateway (receives and processes data)

---

## 6. 🛡️ Security Pipeline (CORE)

**Order of Verification (Strict):**

1. Replay Attack Check (nonce + timestamp)
2. HMAC Validation
3. Hash Validation
4. ECDSA Signature Verification
5. AES Decryption

---

## 7. ⚔️ Attack Simulation

### 1. Replay Attack
- Same packet is resent
- Detected using nonce and timestamp

### 2. Tampering Attack
- Ciphertext is modified
- Detected by HMAC mismatch

### 3. Unauthorized Device Attack
- Fake or invalid key used
- Detected by ECDSA signature verification failure

---

## 8. 📊 Database Design

**Table**: `heart_rate_data`

**Fields:**
- `device_id`
- `heart_rate`
- `timestamp`
- `nonce`
- `encrypted_data`
- `hash_value`
- `hmac_value`
- `signature`
- `status` (VALID / REPLAY / TAMPERED / UNAUTHORIZED)

---

## 9. 🖥️ Dashboard

Built using **Flask**

**Features:**
- Live data table
- Security status display
- Heart rate trend graph
- Real-time updates

---

## 10. 🧪 Testing

**Test Cases:**
- Normal flow → `VALID`
- Replay attack → `REPLAY`
- Tampering attack → `TAMPERED`
- Fake/unauthorized device → `UNAUTHORIZED`

---

## 11. ⚙️ Integration Flow

```
Data → AES Encryption → Hash + HMAC → ECDSA Signature → Packet
        ↓
     MQTT Broker
        ↓
 Receiver → Verification Pipeline → Classification → SQLite DB → Flask Dashboard
```

---

## 12. 🧠 Key Concepts Learned

- Secure IoT / IoMT system design
- Layered cryptography approach
- Attack simulation and detection
- Real-time data pipelines
- Full-stack system integration (Device → Broker → Gateway → Dashboard)

---

## 13. 🚀 Conclusion

This project demonstrates a complete **secure IoMT communication pipeline** with strong cryptographic protections and real-world attack detection and monitoring capabilities.

---

**Built for educational and academic purposes.**
```

---
