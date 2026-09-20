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
from google.protobuf.message import Message


# ============================================================
#  PART 1 — FreeFire_pb2 (inlined)
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
#  PART 2 — Settings & Region Configs
# ============================================================

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
RELEASEVERSION = "OB55"
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/"

# Region-specific configuration for GetLoginData
REGIONS = {
    "IND": {
        "get_login_data_url": "https://client.ind.freefiremobile.com/GetLoginData",
        "client_host": "client.ind.freefiremobile.com",
        "release_version": "OB55",
    },
    "BD": {
        "get_login_data_url": "https://client.bd.freefiremobile.com/GetLoginData",
        "client_host": "client.bd.freefiremobile.com",
        "release_version": "OB55",
    },
    "SG": {
        "get_login_data_url": "https://client.sg.freefiremobile.com/GetLoginData",
        "client_host": "client.sg.freefiremobile.com",
        "release_version": "OB55",
    },
    "ID": {
        "get_login_data_url": "https://client.id.freefiremobile.com/GetLoginData",
        "client_host": "client.id.freefiremobile.com",
        "release_version": "OB55",
    },
    "TH": {
        "get_login_data_url": "https://client.th.freefiremobile.com/GetLoginData",
        "client_host": "client.th.freefiremobile.com",
        "release_version": "OB55",
    },
    "VN": {
        "get_login_data_url": "https://client.vn.freefiremobile.com/GetLoginData",
        "client_host": "client.vn.freefiremobile.com",
        "release_version": "OB55",
    },
    "BR": {
        "get_login_data_url": "https://client.br.freefiremobile.com/GetLoginData",
        "client_host": "client.br.freefiremobile.com",
        "release_version": "OB55",
    },
    "ME": {
        "get_login_data_url": "https://client.me.freefiremobile.com/GetLoginData",
        "client_host": "client.me.freefiremobile.com",
        "release_version": "OB55",
    },
    "PK": {
        "get_login_data_url": "https://client.pk.freefiremobile.com/GetLoginData",
        "client_host": "client.pk.freefiremobile.com",
        "release_version": "OB55",
    },
    "EG": {
        "get_login_data_url": "https://client.eg.freefiremobile.com/GetLoginData",
        "client_host": "client.eg.freefiremobile.com",
        "release_version": "OB55",
    },
}

# HTTP client with connection pooling
HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
_http_client = httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT)


# ============================================================
#  PART 3 — Flask App
# ============================================================

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ============================================================
#  PART 4 — Core Activation Engine (from activator file)
# ============================================================

class AccountActivator:
    """Merged activator + JWT generator."""

    def __init__(self, region="IND"):
        self.region = region
        self.regions = REGIONS
        self.key = MAIN_KEY
        self.iv = MAIN_IV
        self.stats_lock = threading.Lock()
        self.successful = 0
        self.failed = 0
        self.successful_accounts = []
        self.failed_accounts = []

    # ---------- Protobuf helpers ----------
    def varint_encode(self, n):
        out = []
        while True:
            b = n & 0x7F
            n >>= 7
            if n:
                b |= 0x80
            out.append(b)
            if not n:
                break
        return bytes(out)

    def build_field(self, field_num, value):
        if isinstance(value, int):
            return self.varint_encode((field_num << 3) | 0) + self.varint_encode(value)
        elif isinstance(value, (str, bytes)):
            data = value.encode('utf-8') if isinstance(value, str) else value
            return self.varint_encode((field_num << 3) | 2) + self.varint_encode(len(data)) + data
        else:
            raise TypeError(f"Unsupported type for field {field_num}: {type(value)}")

    def assemble_proto(self, fields):
        packet = b''
        for k, v in fields.items():
            idx = int(k)
            if isinstance(v, list):
                for item in v:
                    packet += self.build_field(idx, item)
            else:
                packet += self.build_field(idx, v)
        return packet

    def aes_encrypt(self, plain):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        pad_len = 16 - (len(plain) % 16)
        if pad_len == 0:
            pad_len = 16
        return cipher.encrypt(plain + bytes([pad_len]) * pad_len)

    def parse_proto(self, data):
        from google.protobuf.internal.decoder import _DecodeVarint, _DecodeVarint32
        pos, length = 0, len(data)
        result = {}
        while pos < length:
            key, pos = _DecodeVarint(data, pos)
            field = key >> 3
            wire = key & 7
            if wire == 0:
                val, pos = _DecodeVarint(data, pos)
            elif wire == 2:
                size, pos = _DecodeVarint32(data, pos)
                raw = data[pos:pos + size]
                pos += size
                try:
                    val = raw.decode('utf-8')
                except Exception:
                    val = raw.hex()
            elif wire == 5:
                val = int.from_bytes(data[pos:pos + 4], 'little')
                pos += 4
            elif wire == 1:
                val = int.from_bytes(data[pos:pos + 8], 'little')
                pos += 8
            else:
                raise Exception(f"Unknown wire type {wire}")
            result[field] = val
        return result

    # ---------- JWT generation (from file 2) ----------
    def get_access_token(self, uid, password):
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
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

    def json_to_proto(self, json_data, proto_message):
        json_format.ParseDict(json.loads(json_data), proto_message)
        return proto_message.SerializeToString()

    def _try_parse_login_res(self, data):
        try:
            msg = LoginRes()
            msg.ParseFromString(data)
            if msg.account_id and msg.account_id > 0:
                return json.loads(json_format.MessageToJson(msg))
        except Exception:
            pass
        return None

    def extract_login_res(self, raw):
        parsed = self._try_parse_login_res(raw)
        if parsed:
            return parsed

        idx = 0
        while True:
            idx = raw.find(b"\x08", idx)
            if idx == -1:
                break
            parsed = self._try_parse_login_res(raw[idx:])
            if parsed:
                return parsed
            idx += 1

        jwt_marker = raw.find(b"eyJhbGciOiJIUzI1NiIs")
        if jwt_marker != -1:
            for i in range(jwt_marker - 1, max(jwt_marker - 300, -1), -1):
                if raw[i] == 0x42:
                    parsed = self._try_parse_login_res(raw[i:])
                    if parsed:
                        return parsed
                    break

        raise Exception(f"Could not parse LoginRes. Raw: {raw[:200]}")

    def generate_jwt_token(self, uid, password):
        """Full JWT generation pipeline."""
        start_time = time.time()

        token_val, open_id = self.get_access_token(uid, password)
        if token_val == "0" or open_id == "0":
            raise Exception("Invalid UID or Password — access token not received")

        body = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": token_val,
            "orign_platform_type": "4",
        })
        proto_bytes = self.json_to_proto(body, LoginReq())
        payload = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV).encrypt(
            proto_bytes + bytes([16 - len(proto_bytes) % 16]) * (16 - len(proto_bytes) % 16)
        )

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

        elapsed = time.time() - start_time

        return {
            "access_token": token_val,
            "open_id": open_id,
            "real_uid": str(msg.get("accountId", "")),
            "status": "success",
            "time": f"{elapsed:.2f}s",
            "token": msg.get("token", ""),
            "jwt": msg.get("token", ""),
        }

    # ---------- GetLoginData (activator) ----------
    def build_getlogindata_payload(self, jwt, uid, region='IND'):
        try:
            parts = jwt.split('.')
            if len(parts) != 3:
                raise Exception("Invalid JWT format")

            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))

            external_id = decoded.get('external_id')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            fields = {
                3: now,
                4: "free fire",
                5: 1,
                7: "1.126.15",
                8: "Android OS 10 / API-29 (QP1A.190711.020/1617006012)",
                9: "Handheld",
                10: "Vi India",
                11: "WIFI",
                12: 1600,
                13: 720,
                14: "320",
                15: "ARM64 FP ASIMD AES | 2301 | 8",
                16: 2799,
                17: "PowerVR Rogue GE8320",
                18: "OpenGL ES 3.2 build 1.1@5425693",
                19: f"Google|{uid}",
                20: "27.59.69.226",
                21: "en",
                22: external_id,
                23: 4,
                24: "Handheld",
                25: "realme RMX2189",
                26: region,
                29: jwt,
                30: 1,
                41: "Vi India",
                42: "WIFI",
                57: "7428b253defc164018c604a1ebbfebdf",
                60: 19799,
                61: 1198,
                62: 5056,
                64: 1430,
                65: 19999,
                66: 1198,
                67: 19799,
                70: 4,
                73: 2,
                76: 1,
                78: 6,
                79: 2,
                81: "64",
                83: "2019120816",
                86: "OpenGLES2",
                87: 3071,
                88: 8,
                90: "New Delhi",
                91: "DL",
                92: 13080,
                93: "3rd_party",
                94: "KqsHTw+Xui+7NiknuVG39jBvqfcBIE++vNayjgpDtOGFORTYgMixv5qmFWsOvq136YMoizYxRRPFTZxTOkFnCjln760=",
                95: 111207,
                96: '{"cur_rate":null,"support_etc2":false}',
                97: 1,
                99: "30",
                100: "38",
                102: "47504412000e085134"
            }

            plain = self.assemble_proto(fields)
            return self.aes_encrypt(plain)

        except Exception as e:
            logging.error(f"Error building GetLoginData payload: {e}")
            return None

    def get_login_data(self, jwt, uid, region='IND'):
        region_config = self.regions.get(region, self.regions['IND'])
        url = region_config['get_login_data_url']
        client_host = region_config['client_host']
        release_version = region_config['release_version']

        payload = self.build_getlogindata_payload(jwt, uid, region)
        if not payload:
            return False, "Payload build failed"

        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {jwt}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': release_version,
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': client_host,
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        for attempt in range(3):
            try:
                response = _http_client.post(url, headers=headers, data=payload, timeout=12)
                if response.status_code == 200:
                    logging.info(f"✅ GetLoginData successful! (UID: {uid}, Region: {region})")
                    return True, "OK"
                elif response.status_code == 401:
                    logging.error(f"❌ 401 Unauthorized for UID: {uid}")
                    return False, "401 Unauthorized"
                else:
                    logging.warning(f"⚠️ GetLoginData attempt {attempt+1} failed: {response.status_code}")
                    time.sleep(1)
            except Exception as e:
                logging.warning(f"⚠️ GetLoginData attempt {attempt+1} error: {e}")
                time.sleep(1)

        return False, "All attempts failed"

    # ---------- Full activation ----------
    def activate_account(self, uid, password, region=None):
        region = region or self.region

        logging.info(f"🔄 Activating UID: {uid} (Region: {region})")

        # Step 1: Generate JWT
        try:
            jwt_data = self.generate_jwt_token(uid, password)
            jwt = jwt_data.get("jwt") or jwt_data.get("token")
            if not jwt:
                raise Exception("JWT token missing in response")
        except Exception as e:
            with self.stats_lock:
                self.failed += 1
                self.failed_accounts.append({
                    'uid': uid, 'password': password, 'region': region,
                    'error': f'JWT generation failed: {e}'
                })
            return {"status": "error", "stage": "jwt", "error": str(e)}

        # Step 2: GetLoginData
        ok, msg = self.get_login_data(jwt, uid, region)

        if ok:
            with self.stats_lock:
                self.successful += 1
                self.successful_accounts.append({
                    'uid': uid, 'password': password, 'region': region,
                    'jwt': jwt, 'status': 'activated'
                })
            logging.info(f"✅ Account activated: {uid}")
            return {
                "status": "success",
                "uid": uid,
                "real_uid": jwt_data.get("real_uid"),
                "region": region,
                "jwt": jwt,
                "access_token": jwt_data.get("access_token"),
                "open_id": jwt_data.get("open_id"),
                "time": jwt_data.get("time"),
            }
        else:
            with self.stats_lock:
                self.failed += 1
                self.failed_accounts.append({
                    'uid': uid, 'password': password, 'region': region,
                    'error': f'GetLoginData failed: {msg}'
                })
            return {
                "status": "error",
                "stage": "get_login_data",
                "error": msg,
                "jwt": jwt,
                "real_uid": jwt_data.get("real_uid"),
            }


# Singleton activator instance
activator = AccountActivator()


# ============================================================
#  PART 5 — Routes
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "endpoints": {
            "jwt_only": "/token?uid=UID&password=PASS",
            "activate": "/activate?uid=UID&password=PASS&region=IND",
            "stats": "/stats",
            "regions": "/regions",
        },
        "example": "/activate?uid=18097039025&password=yourpass&region=IND",
    }), 200


@app.route("/token", methods=["GET"])
def get_jwt_token():
    """Generate JWT only (no activation)."""
    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({
            "status": "error",
            "error": "Both uid and password parameters are required"
        }), 400

    try:
        token_data = activator.generate_jwt_token(uid, password)
        return jsonify(token_data), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to generate token: {str(e)}"
        }), 500


@app.route("/activate", methods=["GET", "POST"])
def activate():
    """Generate JWT + call GetLoginData to activate the account."""
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        uid = body.get("uid") or request.form.get("uid")
        password = body.get("password") or request.form.get("password")
        region = body.get("region") or request.form.get("region", "IND")
    else:
        uid = request.args.get("uid")
        password = request.args.get("password")
        region = request.args.get("region", "IND")

    if not uid or not password:
        return jsonify({
            "status": "error",
            "error": "Both uid and password parameters are required"
        }), 400

    region = region.upper()
    if region not in REGIONS:
        return jsonify({
            "status": "error",
            "error": f"Unsupported region: {region}",
            "supported": list(REGIONS.keys())
        }), 400

    try:
        result = activator.activate_account(uid, password, region)
        status_code = 200 if result.get("status") == "success" else 500
        return jsonify(result), status_code
    except Exception as e:
        logging.exception("Activation failed")
        return jsonify({
            "status": "error",
            "error": f"Activation failed: {str(e)}"
        }), 500


@app.route("/stats", methods=["GET"])
def stats():
    return jsonify({
        "successful": activator.successful,
        "failed": activator.failed,
        "successful_accounts": activator.successful_accounts,
        "failed_accounts": activator.failed_accounts,
    }), 200


@app.route("/regions", methods=["GET"])
def regions():
    return jsonify({
        "supported_regions": list(REGIONS.keys()),
        "default": "IND",
    }), 200


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    logging.info("🚀 Free Fire Activator + JWT Generator running on port 5002")
    app.run(host="0.0.0.0", port=5002, debug=False)
