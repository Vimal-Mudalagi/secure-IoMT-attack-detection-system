```markdown
# 🛡️ IoMT Secure Communication Framework

A lightweight cryptographic framework for securing communication in **Internet of Medical Things (IoMT)** systems using encryption, authentication, and attack detection.

---

## 🚀 What This Project Does

This project simulates a real-world IoMT pipeline:

**Device → Encrypt → Secure → Send → Verify → Store → Visualize**

It ensures:

- 🔐 **Data confidentiality** (AES encryption)
- 🧾 **Data integrity** (SHA-256 + HMAC)
- 👤 **Device authentication** (ECDSA)
- 🔁 **Replay attack protection** (timestamp + nonce)
- 🚨 **Attack detection** (tampered / replay / unauthorized)
- 📊 **Real-time monitoring dashboard**

---

## 🧠 Features

- AES-128 encryption (CBC mode)
- ECC-based key handling (ECDSA)
- SHA-256 hashing
- HMAC-SHA256 verification
- ECDSA digital signatures
- Replay attack detection (nonce + timestamp)
- MQTT-based publish/subscribe communication
- SQLite database storage
- Flask web dashboard with real-time updates
- Attack simulation scripts (replay, tampering, unauthorized)

---

## 🧱 Project Structure

```
iomt/
 ├── pub.py                  # IoMT device (publisher) - encrypts & signs data
 ├── sub.py                  # Gateway + verification pipeline (verifier)
 ├── app.py                  # Flask dashboard (real-time UI)
 ├── attack_demo_all.py      # 1-click attack simulation
 ├── iomt.db                 # SQLite database (auto-created)
 ├── device_private.pem      # Private key (for publisher)
 ├── device_public.pem       # Public key (for subscriber)
 ├── README.md               # This file
 └── DOC.md                  # Detailed documentation (optional)
```

---

## ⚙️ Installation

### 1. Install Python dependencies

```bash
pip install paho-mqtt pycryptodome cryptography flask matplotlib
```

### 2. Install MQTT Broker (Mosquitto)

- **Windows**: Download and install from [mosquitto.org](https://mosquitto.org/download/)
- **Linux** (Ubuntu/Debian):

```bash
sudo apt update && sudo apt install mosquitto mosquitto-clients
```

- Start the broker:

```bash
mosquitto
```

(Or run in background: `mosquitto -d`)

---

## ▶️ How to Run

### Step 1: Start Subscriber (Gateway + Verifier)

```bash
python sub.py
```

### Step 2: Start Dashboard

```bash
python app.py
```

Open in browser: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Step 3: Start Publisher (IoMT Device)

```bash
python pub.py
```

The publisher will send secure heart-rate data every few seconds.

---

## ⚔️ Attack Simulation

Run the attack demo:

```bash
python attack_demo_all.py
```

This script simulates:

- Replay attack
- Data tampering attack
- Unauthorized device injection

The dashboard and logs will show real-time detection.

---

## 📊 Dashboard

The Flask dashboard displays:

- Device ID
- Heart Rate
- Status (**VALID** / **TAMPERED** / **REPLAY** / **UNAUTHORIZED**)
- Timestamp
- Live updating table and graph

### Status Meanings

| Status        | Meaning                          |
|---------------|----------------------------------|
| **VALID**     | Normal, secure packet            |
| **TAMPERED**  | Data was modified (HMAC/Hash fail)|
| **REPLAY**    | Duplicate or delayed packet      |
| **UNAUTHORIZED** | Invalid signature (fake device) |
| **ERROR**     | Decryption or processing failure |

---

## 📸 Screenshots

*(Add your screenshots here when ready)*

- **Dashboard UI**
- **Attack Detection in Action**
- **Database Output**

---

## 🧪 Testing Strategy

- Normal end-to-end data flow
- Replay attack detection
- Data tampering simulation
- Unauthorized device injection
- Full pipeline validation (publish → verify → store → visualize)

---

## 🧠 Key Learnings

- Real-world cryptographic pipeline design
- Layered security (encryption + integrity + authentication)
- Practical attack detection in IoT
- MQTT protocol usage with security overlays
- Integration of Flask dashboard with MQTT

---

## 📌 Future Improvements

- Upgrade to **AES-GCM** (authenticated encryption)
- Device registration & key management system
- Cloud deployment (AWS/Azure)
- Integration with real hardware (ESP32, Raspberry Pi)
- Support for more vital signs (SpO2, ECG, etc.)

---

## 👨‍💻 Author

**Vimal Mudalagi**  
MSc CS Cybersecurity

---

**Made with ❤️ for secure healthcare IoT**
```
