# ============================================================
#  FREE FIRE — JWT / ACTIVATE / BOTH API
#  Endpoints:
#    /token    → JWT only
#    /activate → JWT + GetLoginData
#    /spin     → JWT + activate + spin-ready token
#  Run: python app.py   (port 5002)
# ============================================================

import time
import json
import base64
import logging
import threading
from datetime import datetime

import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES

from google.protobuf import json_format
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder


# ============================================================
#  PART 1 — FreeFire_pb2 (inline)
# ============================================================

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 6, 30, 0, "", "FreeFire.proto",
)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x46reeFire.proto"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t'
    b'\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d '
    b'\x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t"]\n\x10\x42lacklist'
    b'InfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n'
    b'\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 '
    b'\x01(\r"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12'
    b'\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18'
    b'\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08"\xa0\x03\n\x08'
    b'LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region'
    b'\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_'
    b'region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t'
    b'\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_'
    b'regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl'
    b'\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mul'
    b'ator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.'
    b'BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueue'
    b'Info\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18'
    b'\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city'
    b'\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n'
    b'\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17'
    b'\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_'
    b'REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n'
    b'\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME'
    b'_AUTO_NEW\x10\xf6\x07\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FreeFire_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_BANREASON"]._serialized_start = 738
    _globals["_BANREASON"]._serialized_end = 906
    _globals["_LOGINREQ"]._serialized_start = 18
    _globals["_LOGINREQ"]._serialized_end = 117
    _globals["_BLACKLISTINFORES"]._serialized_start = 119
    _globals["_BLACKLISTINFORES"]._serialized_end = 212
    _globals["_LOGINQUEUEINFO"]._serialized_start = 214
    _globals["_LOGINQUEUEINFO"]._serialized_end = 316
    _globals["_LOGINRES"]._serialized_start = 319
    _globals["_LOGINRES"]._serialized_end = 735

LoginReq = _globals["LoginReq"]
LoginRes = _globals["LoginRes"]


# ============================================================
#  PART 2 — Settings
# ============================================================

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV  = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
RELEASEVERSION = "OB55"
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/"

# Modern Garena hosts (Blueshark)
REGIONS = {
    "IND": {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "BD":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "SG":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "ID":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "TH":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "VN":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "ME":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "PK":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "EU":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "MY":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "PH":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "RU":  {"host": "clientbp.ggpolarbear.com", "release": "OB55"},
    "BR":  {"host": "client.us.freefiremobile.com", "release": "OB55"},
    "US":  {"host": "client.us.freefiremobile.com", "release": "OB55"},
    "SAC": {"host": "client.us.freefiremobile.com", "release": "OB55"},
    "NA":  {"host": "client.us.freefiremobile.com", "release": "OB55"},
}

HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpx.Timeout(20.0, connect=8.0)
_http_client = httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT)


# ============================================================
#  PART 3 — Flask App
# ============================================================

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ============================================================
#  PART 4 — Engine
# ============================================================

class FFEngine:
    def __init__(self):
        self.regions = REGIONS
        self.key = MAIN_KEY
        self.iv = MAIN_IV
        self.stats_lock = threading.Lock()
        self.stats = {
            "token_ok": 0, "token_fail": 0,
            "activate_ok": 0, "activate_fail": 0,
        }

    # ---------- Crypto ----------
    def aes_encrypt(self, plain: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        pad_len = 16 - (len(plain) % 16)
        if pad_len == 0:
            pad_len = 16
        return cipher.encrypt(plain + bytes([pad_len]) * pad_len)

    def json_to_proto(self, json_data: str, proto_message):
        json_format.ParseDict(json.loads(json_data), proto_message)
        return proto_message.SerializeToString()

    # ---------- Protobuf manual encoder (for GetLoginData) ----------
    def _varint(self, n):
        out = []
        while True:
            b = n & 0x7F
            n >>= 7
            if n: b |= 0x80
            out.append(b)
            if not n: break
        return bytes(out)

    def _field(self, num, val):
        if isinstance(val, int):
            return self._varint((num << 3) | 0) + self._varint(val)
        if isinstance(val, (str, bytes)):
            data = val.encode() if isinstance(val, str) else val
            return self._varint((num << 3) | 2) + self._varint(len(data)) + data
        raise TypeError(f"field {num}: bad type {type(val)}")

    def _assemble(self, fields: dict) -> bytes:
        out = b""
        for k, v in fields.items():
            if isinstance(v, list):
                for it in v: out += self._field(int(k), it)
            else:
                out += self._field(int(k), v)
        return out

    # ---------- Step 1: OAuth access token ----------
    def get_access_token(self, uid: str, password: str):
        url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
        payload = (
            f"uid={uid}&password={password}"
            + "&response_type=token&client_type=2"
            + "&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
            + "&client_id=100067"
        )
        headers = {
            "User-Agent": USERAGENT,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = _http_client.post(url, data=payload, headers=headers)
        try:
            data = resp.json()
        except Exception:
            raise Exception(f"OAuth not JSON: {resp.text[:150]}")
        return data.get("access_token", "0"), data.get("open_id", "0")

    # ---------- Step 2: parse LoginRes ----------
    def _parse_res(self, data: bytes):
        try:
            msg = LoginRes()
            msg.ParseFromString(data)
            if msg.account_id and msg.account_id > 0:
                return json.loads(json_format.MessageToJson(msg))
        except Exception:
            pass
        return None

    def extract_login_res(self, raw: bytes) -> dict:
        p = self._parse_res(raw)
        if p: return p

        idx = 0
        while True:
            idx = raw.find(b"\x08", idx)
            if idx == -1: break
            p = self._parse_res(raw[idx:])
            if p: return p
            idx += 1

        jwt_marker = raw.find(b"eyJhbGciOiJIUzI1NiIs")
        if jwt_marker != -1:
            for i in range(jwt_marker - 1, max(jwt_marker - 300, -1), -1):
                if raw[i] == 0x42:
                    p = self._parse_res(raw[i:])
                    if p: return p
                    break
        raise Exception(f"Could not parse LoginRes. Raw: {raw[:150]}")

    # ---------- STEP A: JWT only ----------
    def generate_jwt(self, uid: str, password: str) -> dict:
        start = time.time()
        token_val, open_id = self.get_access_token(uid, password)
        if token_val == "0" or open_id == "0":
            raise Exception("Invalid UID or Password")

        body = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": token_val,
            "orign_platform_type": "4",
        })
        proto_bytes = self.json_to_proto(body, LoginReq())
        payload = self.aes_encrypt(proto_bytes)

        headers = {
            "User-Agent": USERAGENT,
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "X-Ga-Sv": "1789534056",
            "Authorization": "Bearer",
            "X-Ga": "v1 1",
            "Releaseversion": RELEASEVERSION,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2018.4.12f1",
            "PlAy_VeR": "1.132.1",
            "Ob_VeR": RELEASEVERSION,
        }

        resp = _http_client.post(f"{LOGIN_URL}MajorLogin", data=payload, headers=headers)
        msg = self.extract_login_res(resp.content)

        return {
            "status": "success",
            "uid": uid,
            "real_uid": str(msg.get("accountId", "")),
            "access_token": token_val,
            "open_id": open_id,
            "jwt": msg.get("token", ""),
            "token": msg.get("token", ""),
            "ttl": msg.get("ttl", 0),
            "server_url": msg.get("serverUrl", ""),
            "lock_region": msg.get("lockRegion", ""),
            "time": f"{time.time() - start:.2f}s",
        }

    # ---------- STEP B: GetLoginData payload ----------
    def build_getlogindata_payload(self, jwt: str, uid: str, region: str = "IND"):
        parts = jwt.split('.')
        if len(parts) != 3:
            raise Exception("Invalid JWT format")

        body = parts[1] + '=' * (-len(parts[1]) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(body))

        external_id = decoded.get('external_id')
        lock_region = decoded.get('lock_region') or region

        if not external_id:
            raise Exception("JWT missing external_id — regen with /token")

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        fields = {
            3: now, 4: "free fire", 5: 1,
            7: "1.126.15",
            8: "Android OS 10 / API-29 (QP1A.190711.020/1617006012)",
            9: "Handheld", 10: "Vi India", 11: "WIFI",
            12: 1600, 13: 720, 14: "320",
            15: "ARM64 FP ASIMD AES | 2301 | 8",
            16: 2799, 17: "PowerVR Rogue GE8320",
            18: "OpenGL ES 3.2 build 1.1@5425693",
            19: f"Google|{uid}",
            20: "27.59.69.226", 21: "en",
            22: external_id, 23: 4, 24: "Handheld",
            25: "realme RMX2189",
            26: lock_region,           # align to JWT
            29: jwt, 30: 1,
            41: "Vi India", 42: "WIFI",
            57: "7428b253defc164018c604a1ebbfebdf",
            60: 19799, 61: 1198, 62: 5056, 64: 1430,
            65: 19999, 66: 1198, 67: 19799,
            70: 4, 73: 2, 76: 1, 78: 6, 79: 2,
            81: "64", 83: "2019120816",
            86: "OpenGLES2", 87: 3071, 88: 8,
            90: "New Delhi", 91: "DL", 92: 13080,
            93: "3rd_party",
            94: "KqsHTw+Xui+7NiknuVG39jBvqfcBIE++vNayjgpDtOGFORTYgMixv5qmFWsOvq136YMoizYxRRPFTZxTOkFnCjln760=",
            95: 111207,
            96: '{"cur_rate":null,"support_etc2":false}',
            97: 1, 99: "30", 100: "38",
            102: "47504412000e085134",
        }

        plain = self._assemble(fields)
        return self.aes_encrypt(plain)

    # ---------- STEP C: GetLoginData request ----------
    def call_getlogindata(self, jwt: str, uid: str, region: str = "IND"):
        cfg = self.regions.get(region, self.regions["IND"])
        host = cfg["host"]
        release_version = cfg["release"]

        try:
            payload = self.build_getlogindata_payload(jwt, uid, region)
        except Exception as e:
            return False, f"payload: {e}"

        url = f"https://{host}/GetLoginData"

        headers = {
            'Authorization': f'Bearer {jwt}',
            'X-Unity-Version': '2018.4.12f1',
            'X-Ga': 'v1 1',
            'ReleaseVersion': release_version,
            'Content-Type': 'application/octet-stream',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': host,
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        }

        last_err = "no attempt"
        for attempt in range(1, 3):
            try:
                r = _http_client.post(url, headers=headers, content=payload, timeout=15.0)
                if r.status_code == 200:
                    return True, "OK"
                if r.status_code in (401, 403):
                    return False, f"{r.status_code} Unauthorized"
                if r.status_code == 404:
                    return False, f"404 wrong host {host}"
                last_err = f"HTTP {r.status_code}"
                time.sleep(0.5)
            except httpx.ReadTimeout:
                last_err = "read timeout"
            except Exception as e:
                last_err = str(e)
                time.sleep(0.5)

        return False, last_err

    # ---------- STEP D: Full activation ----------
    def activate(self, uid: str, password: str, region: str = "BD"):
        # 1) get JWT
        try:
            jwt_data = self.generate_jwt(uid, password)
            with self.stats_lock:
                self.stats["token_ok"] += 1
        except Exception as e:
            with self.stats_lock:
                self.stats["token_fail"] += 1
            return {"status": "error", "stage": "jwt", "error": str(e)}

        jwt = jwt_data["jwt"]

        # 2) GetLoginData
        ok, msg = self.call_getlogindata(jwt, uid, region)

        if ok:
            with self.stats_lock:
                self.stats["activate_ok"] += 1
            return {
                "status": "success",
                "uid": uid,
                "real_uid": jwt_data["real_uid"],
                "region": region,
                "jwt": jwt,
                "access_token": jwt_data["access_token"],
                "open_id": jwt_data["open_id"],
                "time": jwt_data["time"],
            }
        else:
            with self.stats_lock:
                self.stats["activate_fail"] += 1
            return {
                "status": "error",
                "stage": "get_login_data",
                "error": msg,
                "jwt": jwt,
                "real_uid": jwt_data["real_uid"],
                "region": region,
            }


engine = FFEngine()


# ============================================================
#  PART 5 — Routes
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "endpoints": {
            "token":    "/token?uid=UID&password=PASS              → JWT only",
            "activate": "/activate?uid=UID&password=PASS&region=BD → JWT + GetLoginData",
            "spin":     "/spin?uid=UID&password=PASS&region=BD     → ready-to-spin JWT",
            "stats":    "/stats",
            "regions":  "/regions",
        },
    }), 200


@app.route("/token", methods=["GET"])
def route_token():
    """JWT ONLY — no activation."""
    uid = request.args.get("uid")
    password = request.args.get("password")
    if not uid or not password:
        return jsonify({"status": "error",
                        "error": "uid and password required"}), 400
    try:
        return jsonify(engine.generate_jwt(uid, password)), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 200


@app.route("/activate", methods=["GET", "POST"])
def route_activate():
    """JWT + GetLoginData."""
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        uid = body.get("uid") or request.form.get("uid")
        password = body.get("password") or request.form.get("password")
        region = (body.get("region") or request.form.get("region", "BD")).upper()
    else:
        uid = request.args.get("uid")
        password = request.args.get("password")
        region = (request.args.get("region", "BD")).upper()

    if not uid or not password:
        return jsonify({"status": "error",
                        "error": "uid and password required"}), 400
    if region not in REGIONS:
        return jsonify({"status": "error",
                        "error": f"unsupported region {region}",
                        "supported": list(REGIONS.keys())}), 400

    return jsonify(engine.activate(uid, password, region)), 200


@app.route("/spin", methods=["GET", "POST"])
def route_spin():
    """
    Ready-to-spin: returns JWT even if GetLoginData soft-fails.
    Ideal for the Naruto spinner.
    """
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        uid = body.get("uid") or request.form.get("uid")
        password = body.get("password") or request.form.get("password")
        region = (body.get("region") or request.form.get("region", "BD")).upper()
    else:
        uid = request.args.get("uid")
        password = request.args.get("password")
        region = (request.args.get("region", "BD")).upper()

    if not uid or not password:
        return jsonify({"status": "error",
                        "error": "uid and password required"}), 400

    result = engine.activate(uid, password, region)

    # /spin always returns a usable token, even on activate failure
    return jsonify({
        "status": "success" if result.get("status") == "success" else "partial",
        "jwt": result.get("jwt"),
        "uid": uid,
        "real_uid": result.get("real_uid"),
        "region": region,
        "access_token": result.get("access_token"),
        "open_id": result.get("open_id"),
        "activation": result.get("status"),
        "activation_error": result.get("error"),
        "time": result.get("time"),
    }), 200


@app.route("/stats", methods=["GET"])
def route_stats():
    return jsonify(engine.stats), 200


@app.route("/regions", methods=["GET"])
def route_regions():
    return jsonify({
        "supported": list(REGIONS.keys()),
        "default": "BD",
    }), 200


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    logging.info("🚀 FF API — /token  /activate  /spin  (port 5002)")
    app.run(host="0.0.0.0", port=5002, debug=False)
