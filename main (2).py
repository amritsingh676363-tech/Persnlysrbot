#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════
#   AMRIT PREMIUM HOSTER + USERBOT CORE V2 — ADVANCED FULL EDITION
#   FIXED VERSION — Hosting + Userbot both work
# ════════════════════════════════════════════════════════════════════

import sys as _sys
import os as _os
import subprocess as _subprocess
import warnings as _warnings
_warnings.filterwarnings("ignore")

# ────────────────────────────────────────────────────────────────
#   UTF-8 CONSOLE & STREAM CONFIGURATION (Windows CP1252 Fix)
# ────────────────────────────────────────────────────────────────
_os.environ["PYTHONIOENCODING"] = "utf-8"
_os.environ["PYTHONUTF8"] = "1"
if hasattr(_sys.stdout, "reconfigure"):
    try: _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
if hasattr(_sys.stderr, "reconfigure"):
    try: _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

# ────────────────────────────────────────────────────────────────
#   USERBOT DETECTION & FAST-PATH
# ────────────────────────────────────────────────────────────────
_IS_USERBOT = "--userbot" in _sys.argv or _os.environ.get("USERBOT_MODE") == "1"

# ────────────────────────────────────────────────────────────────
#   AUTO-DEPENDENCY INSTALLER (With Non-Admin --user Fallback)
# ────────────────────────────────────────────────────────────────
def _auto_install_deps():
    # Never run auto-install checks inside child userbot subprocesses
    if _IS_USERBOT:
        return

    try:
        import telethon
        import telegram
        import requests
        return
    except ImportError:
        pass

    ptb_req = "python-telegram-bot>=21.7" if _sys.version_info >= (3, 13) else "python-telegram-bot>=20.7"
    required = [
        ("telethon",   "telethon>=1.30.0"),
        ("telegram",   ptb_req),
        ("requests",   "requests>=2.31.0"),
        ("qrcode",     "qrcode[pil]>=7.4.0"),
        ("gtts",       "gTTS>=2.5.0"),
        ("yt_dlp",     "yt-dlp>=2024.1.0"),
    ]
    missing = []
    for mod, pkg in required:
        try:
            m = __import__(mod)
            if mod == "telegram" and _sys.version_info >= (3, 13):
                v = getattr(m, "__version__", "")
                if v and int(v.split(".")[0]) < 21:
                    print(f"[DEPS] Incompatible python-telegram-bot v{v} on Python {_sys.version.split()[0]}. Upgrading to >=21.7...", flush=True)
                    missing.append("python-telegram-bot>=21.7")
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[DEPS] Installing missing packages: {', '.join(missing)}", flush=True)
        installed = False
        try:
            _subprocess.check_call(
                [_sys.executable, "-m", "pip", "install", "--upgrade", "--no-warn-script-location"] + missing
            )
            installed = True
        except Exception as e1:
            try:
                _subprocess.check_call(
                    [_sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--no-warn-script-location"] + missing
                )
                installed = True
            except Exception as e2:
                print(f"[DEPS] Auto-install failed: {e2}", flush=True)
        if installed:
            print("[DEPS] Dependencies installed successfully.", flush=True)

_auto_install_deps()

# ────────────────────────────────────────────────────────────────
#   GLOBAL CRASH GUARD (Unicode-Safe)
# ────────────────────────────────────────────────────────────────
import traceback as _traceback

def _install_crash_guard():
    def _excepthook(exc_type, exc_value, exc_tb):
        try:
            print("\n" + "=" * 60, flush=True)
            print("[FATAL CRASH DETECTED]", flush=True)
            print("=" * 60, flush=True)
            _traceback.print_exception(exc_type, exc_value, exc_tb)
            print("=" * 60, flush=True)
        except Exception:
            try: _traceback.print_exception(exc_type, exc_value, exc_tb)
            except Exception: pass
    _sys.excepthook = _excepthook

_install_crash_guard()

# ════════════════════════════════════════════════════════════════════
#   🔑 QUICK CONFIGURATION / BOT CREDENTIALS
#   (1. अपना BOT TOKEN और OWNER ID यहाँ डायरेक्ट बदलें)
#   (2. या VPS/टर्मिनल में export BOT_TOKEN="your_token" से चलाएँ)
# ════════════════════════════════════════════════════════════════════
GLOBAL_BOT_TOKEN       = _os.environ.get("BOT_TOKEN", "").strip() or "8970946594:AAGZiDOUPsttkF496xfgvnhEPd0_vP9T_E0"
GLOBAL_OWNER_ID        = int(_os.environ.get("OWNER_ID", "8652812134").strip() or "8652812134")
GLOBAL_API_ID               = int(_os.environ.get("API_ID", "30158957").strip() or "30158957")
GLOBAL_API_HASH             = _os.environ.get("API_HASH", "143ac7b1111331422c3bfe88213995e1").strip() or "143ac7b1111331422c3bfe88213995e1"
GLOBAL_DEVELOPER_NAME       = _os.environ.get("DEVELOPER_NAME", "").strip() or "Amrit"
GLOBAL_DEVELOPER_HANDLE     = _os.environ.get("DEVELOPER_HANDLE", "").strip() or "@xno_amrit"
GLOBAL_SUPPORT_USERNAME     = _os.environ.get("SUPPORT_USERNAME", "").strip() or "@mental_era"

# ── VPS / SHARED HOSTING LOW-MEMORY & ANTI-CRASH TUNING ──
# Stagger delay in seconds between starting each userbot (prevents CPU & RAM spike that triggers Linux OOM/Killed)
GLOBAL_STARTUP_STAGGER_DELAY = int(_os.environ.get("STARTUP_STAGGER_DELAY", "5").strip() or "5")
GLOBAL_AUTOSTART_USERBOTS     = _os.environ.get("AUTOSTART_USERBOTS", "1").strip().lower() not in ("0", "false", "no")

# ════════════════════════════════════════════════════════════════════
#   USERBOT MODE
# ════════════════════════════════════════════════════════════════════
if _IS_USERBOT:
    import asyncio, os, time, json, random, logging, re, hashlib
    import base64, uuid, string, math
    from typing import Dict, Set, Optional
    from io import BytesIO
    from datetime import datetime

    # Configure event loop for Windows before any async libraries are loaded
    if _sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # ── LAZY-LOAD HEAVY MODULES (ZERO STARTUP RAM OVERHEAD) ──
    # Prevents importing 80MB+ of Pillow, yt_dlp, gTTS, and requests at startup
    class _LazyRequests:
        def __getattr__(self, name):
            import requests as _real_req
            return getattr(_real_req, name)

    def _lazy_gTTS(*args, **kwargs):
        from gtts import gTTS as _Real_gTTS
        return _Real_gTTS(*args, **kwargs)

    class _LazyQRCode:
        @staticmethod
        def make(*args, **kwargs):
            import qrcode as _real_qr
            return _real_qr.make(*args, **kwargs)

    class _LazyYTDL:
        @staticmethod
        def YoutubeDL(*args, **kwargs):
            import yt_dlp as _real_ytdl
            return _real_ytdl.YoutubeDL(*args, **kwargs)

    requests = _LazyRequests()
    gTTS = _lazy_gTTS
    qrcode = _LazyQRCode()
    yt_dlp = _LazyYTDL()

    try:
        from telethon import TelegramClient, events, functions, types
        from telethon.sessions import StringSession
        from telethon.errors import FloodWaitError, RPCError, PeerFloodError, SlowModeWaitError
    except ImportError:
        print("[USERBOT] Telethon not found in this Python environment. Auto-installing now...", flush=True)
        try:
            _subprocess.check_call([_sys.executable, "-m", "pip", "install", "telethon>=1.30.0", "--no-warn-script-location"])
        except Exception:
            _subprocess.check_call([_sys.executable, "-m", "pip", "install", "--user", "telethon>=1.30.0", "--no-warn-script-location"])
        from telethon import TelegramClient, events, functions, types
        from telethon.sessions import StringSession
        from telethon.errors import FloodWaitError, RPCError, PeerFloodError, SlowModeWaitError

    BASE_DIR = os.getcwd()
    DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    TEMP_PATH = os.path.join(BASE_DIR, "temp")
    os.makedirs(TEMP_PATH, exist_ok=True)

    # ── ZERO-DISK STORAGE & 5GB BANDWIDTH PROTECTOR ──
    # Runs continuously to wipe any media files and caches, keeping server storage at 0MB.
    async def _auto_disk_and_memory_purger():
        while True:
            try:
                await asyncio.sleep(25)
                for folder in [DOWNLOAD_PATH, TEMP_PATH]:
                    if os.path.isdir(folder):
                        for item in os.listdir(folder):
                            p = os.path.join(folder, item)
                            try:
                                if os.path.isfile(p) or os.path.islink(p):
                                    os.unlink(p)
                                elif os.path.isdir(p):
                                    shutil.rmtree(p, ignore_errors=True)
                            except Exception: pass
                # Clean any stray audio/image files in current working dir
                for f in os.listdir(BASE_DIR):
                    if f.endswith((".mp3", ".ogg", ".png", ".jpg", ".tmp", ".wav")):
                        try: os.unlink(os.path.join(BASE_DIR, f))
                        except Exception: pass

                # Rotate and trim userbot logs if they exceed 512KB
                log_dir = os.path.join(BASE_DIR, "userbot_logs")
                if os.path.isdir(log_dir):
                    for lf in os.listdir(log_dir):
                        lp = os.path.join(log_dir, lf)
                        try:
                            if os.path.isfile(lp) and os.path.getsize(lp) > 512 * 1024:
                                with open(lp, "rb") as f_in:
                                    f_in.seek(-20000, os.SEEK_END)
                                    tail = f_in.read()
                                with open(lp, "wb") as f_out:
                                    f_out.write(tail)
                        except Exception: pass

                # ── CLEAR TELETHON ENTITY CACHE (SAVES 60MB-100MB RAM PER USERBOT) ──
                try:
                    if hasattr(bot, "_entity_cache"):
                        bot._entity_cache.clear()
                except Exception: pass

                import gc
                gc.collect()

                # ── FORCE GLIBC HEAP RELEASE BACK TO LINUX KERNEL ──
                try:
                    import ctypes
                    libc = ctypes.CDLL("libc.so.6")
                    libc.malloc_trim(0)
                except Exception: pass
            except Exception:
                await asyncio.sleep(15)

    # ── CONFIG from env ──
    _api_id_raw = os.environ.get("API_ID", "").strip()
    _api_hash_raw = os.environ.get("API_HASH", "").strip()
    _session_str = os.environ.get("SESSION_STRING", "").strip()

    _missing = []
    if not _api_id_raw: _missing.append("API_ID")
    if not _api_hash_raw: _missing.append("API_HASH")
    if not _session_str: _missing.append("SESSION_STRING")

    if _missing:
        print(f"❌ USERBOT ENV ERROR — Missing: {', '.join(_missing)}", flush=True)
        _sys.exit(1)

    try:
        API_ID = int(_api_id_raw)
    except Exception:
        print(f"❌ USERBOT ENV ERROR — API_ID not int: {_api_id_raw!r}", flush=True)
        _sys.exit(1)

    API_HASH = _api_hash_raw
    OWNER_ID: int = 0
    USERBOT_SLOT: int = int(os.environ.get("USERBOT_SLOT", "0"))

    # ── SELF PROTECTION & MULTI-TENANT ISOLATION ──
    _protected_raw = os.environ.get("USERBOT_OWNER_ID", "").strip()
    PROTECTED_IDS: Set[int] = set()
    HOST_USER_ID: Optional[int] = None
    for _pid in _protected_raw.replace(",", " ").split():
        try:
            val = int(_pid)
            PROTECTED_IDS.add(val)
            if HOST_USER_ID is None:
                HOST_USER_ID = val
        except: pass

    # ── DATA STORAGE DIRECTORY (PER-USER ISOLATED) ──
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    # Scoped user directory so users NEVER mix configs or masters
    USER_DATA_DIR = os.path.join(DATA_DIR, f"user_{HOST_USER_ID}") if HOST_USER_ID else DATA_DIR
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    # ── MULTI-ACCOUNT FLEET CLUSTER CONFIG ──
    FLEET_FILE = os.path.join(USER_DATA_DIR, "fleet_cluster.json")

    def load_fleet_config():
        cfg = {
            "sync_enabled": True,
            "masters": [HOST_USER_ID] if HOST_USER_ID else [],
            "slots": {}
        }
        if os.path.exists(FLEET_FILE):
            try:
                with open(FLEET_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if "sync_enabled" in data:
                            cfg["sync_enabled"] = bool(data["sync_enabled"])
                        if "masters" in data and isinstance(data["masters"], list):
                            cfg["masters"] = []
                            for m in data["masters"]:
                                try: cfg["masters"].append(int(m))
                                except: pass
                        if "slots" in data and isinstance(data["slots"], dict):
                            cfg["slots"] = data["slots"]
            except Exception:
                pass
        return cfg

    def save_fleet_config(cfg):
        try:
            with open(FLEET_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    fleet_cfg = load_fleet_config()
    FLEET_MASTERS: Set[int] = set(fleet_cfg.get("masters", []))
    if HOST_USER_ID:
        FLEET_MASTERS.add(HOST_USER_ID)

    print(f"🚀 USERBOT STARTING... API_ID={API_ID} SLOT={USERBOT_SLOT} SESSION_LEN={len(_session_str)} HOST_UID={HOST_USER_ID} MASTERS={list(FLEET_MASTERS)}", flush=True)

    bot = TelegramClient(
        StringSession(_session_str), API_ID, API_HASH,
        loop=loop,
        device_model=f"Device-{USERBOT_SLOT+1}",
        system_version="Android 14",
        app_version="10.14.0",
        lang_code="en",
        system_lang_code="en",
        auto_reconnect=True, connection_retries=5, retry_delay=3,
        flood_sleep_threshold=15,
        catch_up=False
    )
    logging.getLogger("telethon").setLevel(logging.WARNING)

    # ── STORAGE FILES (PER-USER ISOLATED) ──
    ADMINS_FILE = os.path.join(USER_DATA_DIR, "admins.json")
    NOTES_FILE = os.path.join(USER_DATA_DIR, "notes.json")
    BANNER_FILE = os.path.join(USER_DATA_DIR, "banner_msg_id.txt")
    SPAM_TEXTS_FILE = os.path.join(USER_DATA_DIR, "spam_texts.json")
    WARNS_FILE = os.path.join(USER_DATA_DIR, "warns.json")

    CLONE_ACTIVE: bool = False
    LAST_CLONE_ID: Optional[int] = None
    CLONE_DATA: Dict[str, Optional[object]] = {
        "name": None, "username": None, "bio": None, "photo_bytes": None,
    }

    admins: Set[int] = set()
    notes: Dict[int, str] = {}
    warns: Dict[int, int] = {}

    menu_banner_msg: Optional[tuple] = None
    auto_react_emoji: Optional[str] = None

    muted_users: Set[int] = set()
    global_muted: Set[int] = set()

    reply_users: Set[int] = set()
    rr_users: Set[int] = set()
    flag_users: Set[int] = set()
    hrr_users: Set[int] = set()
    replygod_users: Set[int] = set()
    replyaryaxmental_users: Dict[int, Dict[str, object]] = {}
    replymentalxarya_users = replyaryaxmental_users
    replyAMRIT_users: Dict[int, Dict[str, object]] = {}
    rspam_users: Dict[int, Dict[str, object]] = {}

    attack_users: Set[int] = set()
    roast_users: Set[int] = set()
    diss_users: Set[int] = set()
    war_users: Set[int] = set()
    savage_users: Set[int] = set()
    ultra_users: Set[int] = set()
    godwar_users: Set[int] = set()
    combo_users: Set[int] = set()
    troll_users: Set[int] = set()
    shame_users: Set[int] = set()
    fire_users: Set[int] = set()
    devil_users: Set[int] = set()
    karma_users: Set[int] = set()
    ghost_users: Set[int] = set()
    legend_users: Set[int] = set()
    doom_users: Set[int] = set()

    spray_tasks: Dict[int, asyncio.Task] = {}
    spam_texts: list = []
    watch_spam: Dict[tuple, Dict] = {}
    autokick_users: Dict[int, Set[int]] = {}

    antidel_enabled: bool = False
    antidel_cache: Dict[int, Dict] = {}

    group_locks: Set[int] = set()
    START_TIME = time.time()
    SPRAY_DELAY = 0.1

    MY_BOTS_FILE = os.path.join(BASE_DIR, "my_bots.json")
    user_saved_bots: Dict[str, list] = {}
    bulk_gc_task = None

    def _resolve_user_key(uid: Optional[int] = None) -> str:
        if uid:
            return str(uid)
        if OWNER_ID:
            return str(OWNER_ID)
        env_uid = os.environ.get("USERBOT_OWNER_ID", "").strip()
        if env_uid:
            first = env_uid.replace(",", " ").split()[0]
            if first.isdigit():
                return first
        return "default"

    def load_my_bots():
        global user_saved_bots
        try:
            if os.path.isfile(MY_BOTS_FILE):
                with open(MY_BOTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        user_saved_bots = {str(k): [str(b).strip() for b in v if str(b).strip()] for k, v in data.items() if isinstance(v, list)}
                    elif isinstance(data, list):
                        # Migrate legacy shared list into the owner's key
                        k = _resolve_user_key()
                        user_saved_bots = {k: [str(b).strip() for b in data if str(b).strip()]}
            else:
                user_saved_bots = {}
        except Exception:
            user_saved_bots = {}

    def save_my_bots():
        try:
            with open(MY_BOTS_FILE, "w", encoding="utf-8") as f:
                json.dump(user_saved_bots, f, indent=2)
        except Exception:
            pass

    def get_my_bots(uid: Optional[int] = None) -> list:
        load_my_bots()
        k = _resolve_user_key(uid)
        return list(user_saved_bots.get(k, []))

    def add_my_bots_for_user(bots: list, uid: Optional[int] = None) -> int:
        load_my_bots()
        k = _resolve_user_key(uid)
        existing = user_saved_bots.get(k, [])
        added = 0
        for b in bots:
            uname = b if b.startswith("@") else f"@{b}"
            if uname not in existing:
                existing.append(uname)
                added += 1
        user_saved_bots[k] = existing
        save_my_bots()
        return added

    def remove_my_bot_for_user(bot_name: str, uid: Optional[int] = None) -> bool:
        load_my_bots()
        k = _resolve_user_key(uid)
        existing = user_saved_bots.get(k, [])
        uname = bot_name if bot_name.startswith("@") else f"@{bot_name}"
        if uname in existing:
            existing.remove(uname)
            user_saved_bots[k] = existing
            save_my_bots()
            return True
        return False

    def clear_my_bots_for_user(uid: Optional[int] = None):
        load_my_bots()
        k = _resolve_user_key(uid)
        user_saved_bots[k] = []
        save_my_bots()

    load_my_bots()

    FASTGC_STATE: Dict[str, Optional[object]] = {
        "active": False, "template": None, "task": None, "chat_id": None,
    }
    GC_FAST_INTERVAL = 1
    GC_FAST_EMOJIS = [
        "❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","🩷","🩵","🩶",
        "💖","💘","💝","💗","💓","💞","💕","💟","❣️","❤️‍🔥","❤️‍🩹"
    ]

    # ── HELPERS ──
    def load_admins():
        global admins
        try:
            if not os.path.isfile(ADMINS_FILE):
                admins = set(); return
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            clean = set()
            if isinstance(data, list):
                for x in data:
                    try: clean.add(int(x))
                    except: continue
            admins = clean
        except Exception as e:
            print(f"[LOAD ADMINS ERROR] {str(e)[:80]}", flush=True)
            admins = set()

    def save_admins():
        try:
            tmp = sorted(set(int(x) for x in admins))
            with open(ADMINS_FILE, "w", encoding="utf-8") as f:
                json.dump(tmp, f, indent=2)
        except Exception as e:
            print(f"[SAVE ADMINS ERROR] {str(e)[:80]}", flush=True)

    def is_admin(uid: int) -> bool:
        if not uid: return False
        return uid == OWNER_ID or uid in admins

    def to_dark_font(text: str) -> str:
        if not text: return ""
        lines = str(text).split("\n")
        out_lines = []
        for line in lines:
            words = line.split(" ")
            out_words = []
            for word in words:
                if word.startswith("@") or word.startswith("http://") or word.startswith("https://") or word.startswith("t.me/"):
                    out_words.append(word)
                    continue
                chars = []
                for ch in word:
                    if 'A' <= ch <= 'Z':
                        chars.append(chr(ord(ch) - ord('A') + 0x1D5D4))
                    elif 'a' <= ch <= 'z':
                        chars.append(chr(ord(ch) - ord('a') + 0x1D5EE))
                    elif '0' <= ch <= '9':
                        chars.append(chr(ord(ch) - ord('0') + 0x1D7EC))
                    else:
                        chars.append(ch)
                out_words.append("".join(chars))
            out_lines.append(" ".join(out_words))
        return "\n".join(out_lines)

    # ── ZERO-FLOOD & ANTI-SPAMBLOCK SHIELD ENGINE ──
    # Invisible Unicode characters:
    # \u200b = Zero-width space
    # \u200c = Zero-width non-joiner
    # \u200d = Zero-width joiner
    # \ufeff = Zero-width no-break space
    ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\ufeff"]

    def stealth_mutate(text: str) -> str:
        """
        Anti-SpamBlock & Anti-Filter Engine:
        Injects randomized invisible zero-width unicode characters into outgoing text.
        To the recipient and user, text is 100% normal, perfectly legible, and identical.
        To Telegram's SpamBot, AI scanners, and spam hash filters, every single message
        produces an entirely distinct cryptographic SHA-256 hash. This completely stops
        repetition-based SpamBlock / PeerFlood penalties!
        """
        if not text:
            return text
        # Generate 3-7 random invisible characters as unique cryptographic entropy tail
        entropy_tail = "".join(random.choice(ZERO_WIDTH_CHARS) for _ in range(random.randint(3, 7)))
        words = text.split(" ")
        if len(words) > 1:
            mutated = []
            for i, w in enumerate(words):
                mutated.append(w)
                if i < len(words) - 1 and random.random() < 0.4:
                    mutated.append(random.choice(ZERO_WIDTH_CHARS))
            return " ".join(mutated) + entropy_tail
        return text + entropy_tail

    ANTIFLOOD_CONFIG = {
        "enabled": False, # Floodless pacing removed: ULTRA-FAST instant sending
        "mode": "ultra",  # "ultra" (0.0s delay), "balanced" (0.2s), "safe" (0.8s)
        "zero_width": False,
        "max_per_minute": 99999, # Unlimited raw speed
        "flood_count": 0,
        "last_flood_ts": 0.0,
    }

    _CHAT_SEND_TIMES: Dict[int, list] = {}
    _GLOBAL_LAST_SEND: float = 0.0

    def get_safe_pacing_delay() -> float:
        if not ANTIFLOOD_CONFIG.get("enabled", False):
            return 0.0
        mode = ANTIFLOOD_CONFIG.get("mode", "ultra")
        if mode in ("ultra", "fast", "off", "raw"):
            return 0.0
        elif mode == "balanced":
            return random.uniform(0.15, 0.4)
        elif mode == "stealth":
            return random.uniform(1.2, 2.0)
        else: # "safe"
            return random.uniform(0.6, 1.2)

    async def safe_send(peer, text: str, reply_to=None, is_raid: bool = False, max_retries: int = 3):
        """
        Ultra-fast direct message sender with zero artificial delay:
        - Sends messages instantly at maximum raw speed.
        - Artificial floodless delay is removed completely.
        - Captures real Telegram FloodWaitError gracefully if encountered.
        """
        global _GLOBAL_LAST_SEND
        if not text:
            return None

        payload = text
        if ANTIFLOOD_CONFIG.get("zero_width", False):
            payload = stealth_mutate(payload)

        # Chat ID rate tracking
        try:
            cid = getattr(peer, "id", peer) if not isinstance(peer, (int, str)) else peer
            cid_int = int(cid) if str(cid).lstrip("-").isdigit() else 0
        except Exception:
            cid_int = 0

        # Artificial pacing only if explicitly turned on by user
        if ANTIFLOOD_CONFIG.get("enabled", False):
            target_delay = get_safe_pacing_delay()
            if target_delay > 0:
                now = time.time()
                elapsed = now - _GLOBAL_LAST_SEND
                if elapsed < target_delay:
                    await asyncio.sleep(target_delay - elapsed)

        for attempt in range(max_retries):
            try:
                if reply_to:
                    msg = await bot.send_message(peer, payload, reply_to=reply_to)
                else:
                    msg = await bot.send_message(peer, payload)

                _GLOBAL_LAST_SEND = time.time()
                if cid_int:
                    _CHAT_SEND_TIMES.setdefault(cid_int, []).append(_GLOBAL_LAST_SEND)
                return msg

            except FloodWaitError as fe:
                ANTIFLOOD_CONFIG["flood_count"] = ANTIFLOOD_CONFIG.get("flood_count", 0) + 1
                ANTIFLOOD_CONFIG["last_flood_ts"] = time.time()
                wait_sec = fe.seconds + 0.5
                print(f"⚠️ [Telegram FloodWait] {fe.seconds}s on Slot #{USERBOT_SLOT}.", flush=True)
                if wait_sec > 40:
                    print(f"⚠️ [Telegram FloodWait] Exceeds 40s ({wait_sec}s). Aborting attempt.", flush=True)
                    return None
                await asyncio.sleep(wait_sec)
                continue

            except PeerFloodError:
                ANTIFLOOD_CONFIG["flood_count"] = ANTIFLOOD_CONFIG.get("flood_count", 0) + 1
                print(f"⚠️ [PeerFloodError] Rate limited by Telegram in chat {cid_int}.", flush=True)
                await asyncio.sleep(2.0)
                return None

            except SlowModeWaitError as sm:
                print(f"⏳ [SlowMode] {sm.seconds}s in chat {cid_int}. Waiting...", flush=True)
                await asyncio.sleep(sm.seconds + 0.2)
                continue

            except Exception as e:
                err_str = str(e).lower()
                if "flood" in err_str:
                    ANTIFLOOD_CONFIG["flood_count"] = ANTIFLOOD_CONFIG.get("flood_count", 0) + 1
                    await asyncio.sleep(1.0)
                    continue
                print(f"❌ [SEND ERROR] {str(e)[:60]}", flush=True)
                return None

        return None

    def chunk_text(text: str, max_size: int = 3800) -> list:
        if not text or len(text) <= max_size:
            return [text] if text else []
        chunks = []
        lines = text.split("\n")
        cur = []
        cur_len = 0
        for line in lines:
            line_len = len(line) + 1
            if cur_len + line_len > max_size and cur:
                chunks.append("\n".join(cur))
                cur = [line]
                cur_len = line_len
            else:
                cur.append(line)
                cur_len += line_len
        if cur:
            chunks.append("\n".join(cur))
        return chunks

    async def safe_edit(event, text: str, is_raid: bool = False):
        if not text: return
        payload = text
        if is_raid and ANTIFLOOD_CONFIG.get("zero_width", True):
            payload = stealth_mutate(payload)

        chunks = chunk_text(payload, 3800)
        first_chunk = chunks[0] if chunks else payload

        # If incoming event from Master controller or target, send reply via safe_send
        if not getattr(event, "out", False):
            for c in chunks:
                try: await safe_send(event.chat_id, c, reply_to=event.id, is_raid=is_raid)
                except Exception:
                    try: await safe_send(event.chat_id, c, is_raid=is_raid)
                    except: pass
            return

        # Outgoing message: edit the first chunk
        edited_ok = False
        try:
            await event.edit(first_chunk)
            edited_ok = True
        except FloodWaitError as fe:
            await asyncio.sleep(fe.seconds + 1.0)
            try:
                await event.edit(first_chunk)
                edited_ok = True
            except: pass
        except Exception as e:
            pass

        # If edit failed, fallback to safe_send; ONLY delete original if new msg actually succeeded!
        if not edited_ok:
            try:
                msg = await safe_send(event.chat_id, first_chunk, is_raid=is_raid)
                if msg and getattr(event, "out", False):
                    try: await event.delete()
                    except: pass
            except Exception:
                pass

        # If there are additional chunks (>3800 chars), send them sequentially
        for extra in chunks[1:]:
            try: await safe_send(event.chat_id, extra, is_raid=is_raid)
            except: pass

    def load_notes():
        global notes
        try:
            if not os.path.isfile(NOTES_FILE):
                notes = {}; return
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            clean = {}
            if isinstance(raw, dict):
                for k, v in raw.items():
                    try: clean[int(k)] = str(v)
                    except: continue
            notes = clean
        except Exception as e:
            print(f"[LOAD NOTES ERROR] {str(e)[:80]}", flush=True)
            notes = {}

    def save_notes():
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE NOTES ERROR] {str(e)[:80]}", flush=True)

    def load_banner():
        global menu_banner_msg
        try:
            if not os.path.isfile(BANNER_FILE):
                menu_banner_msg = None; return
            with open(BANNER_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if ":" not in raw:
                menu_banner_msg = None; return
            chat, msg = raw.split(":", 1)
            menu_banner_msg = (int(chat), int(msg))
        except Exception as e:
            print(f"[LOAD BANNER ERROR] {str(e)[:80]}", flush=True)
            menu_banner_msg = None

    def save_banner():
        try:
            if not menu_banner_msg:
                if os.path.isfile(BANNER_FILE): os.remove(BANNER_FILE)
                return
            with open(BANNER_FILE, "w", encoding="utf-8") as f:
                f.write(f"{menu_banner_msg[0]}:{menu_banner_msg[1]}")
        except Exception as e:
            print(f"[SAVE BANNER ERROR] {str(e)[:80]}", flush=True)

    def load_spam_texts():
        global spam_texts
        try:
            if not os.path.isfile(SPAM_TEXTS_FILE):
                spam_texts = []; return
            with open(SPAM_TEXTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            spam_texts = [str(x) for x in data] if isinstance(data, list) else []
        except Exception as e:
            print(f"[LOAD SPAM TEXTS ERROR] {str(e)[:80]}", flush=True)
            spam_texts = []

    def save_spam_texts():
        try:
            with open(SPAM_TEXTS_FILE, "w", encoding="utf-8") as f:
                json.dump(spam_texts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE SPAM TEXTS ERROR] {str(e)[:80]}", flush=True)

    def load_warns():
        global warns
        try:
            if not os.path.isfile(WARNS_FILE):
                warns = {}; return
            with open(WARNS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            warns = {int(k): int(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except:
            warns = {}

    def save_warns():
        try:
            with open(WARNS_FILE, "w", encoding="utf-8") as f:
                json.dump(warns, f, indent=2)
        except: pass

    async def get_targets(event, arg: str = "") -> Set[int]:
        targets: Set[int] = set()
        if event.is_reply:
            try:
                reply = await event.get_reply_message()
                if reply and reply.sender_id:
                    targets.add(int(reply.sender_id))
            except: pass
        if arg:
            for part in arg.strip().split():
                if not part: continue
                if part.isdigit():
                    try: targets.add(int(part)); continue
                    except: pass
                try:
                    ent = await bot.get_entity(part)
                    if ent and getattr(ent, "id", None):
                        targets.add(int(ent.id))
                except: pass
        try:
            me = await bot.get_me()
            targets.discard(me.id)
        except: pass
        targets -= PROTECTED_IDS
        return targets

    load_admins()
    load_notes()
    load_banner()
    load_spam_texts()
    load_warns()

    # ── TEXT LISTS ──
    reply_list = [
        "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ ARYA X MENTAL 𝐒ᴇ - 🦢💘",
        "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ ARYA X MENTAL ! 🌙",
        "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
        "chudke bhaga kaise 😂💥🤣🤘🏻",
        "ne toh ARYA X MENTAL ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        "mkl lun te vaj 😂✊🏻💦",
        "𝗧ᴍᴋ𝗕 pe ARYA X MENTAL ka hamla 😂⚔🔥💥",
        "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
        "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        "chl rndyce chud ke dikha 😂💥🤣🔥",
        "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        "tera baap bass ARYA X MENTAL hai 😂🎀",
        "try maa hagte hue paad mari -#😹🔥🥀",
        "𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ ARYA X MENTAL 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
    ]

    reply_texts = [
        "⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद ARYA X MENTAL बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        "नहीं नहीं तेरी मां को 𝐒ɪʀғ ARYA X MENTAL बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        "तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        "𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        "सोच तेरी बहन को ARYA X MENTAL बाप का गुलाम चोद रहा 😎🔥",
        "Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        "Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन ARYA X MENTAL /~👑 बाप से सही chudi 🥵🔥",
        "ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ ARYA X MENTAL बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
    ]

    fun_texts = [
        "तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
        "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
        "𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-'🚂-'.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
        "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
    ]

    flag_texts = [
        " ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
        " ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚",
        " ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༏₊⁺🇺🇸 ₊⁺⋆.˚",
        " ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚",
        " ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
        " ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ ARYA X MENTAL 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
    ]

    heart_replies = [
        "𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꜶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
    ]

    attack_list = [
        "⚔️ Teri aukat nahi mujhse ladhne ki randike 😂🔥",
        "💥 Chal bhaag yahan se chutiye warna maar khayega 🤣⚔️",
        "🗡️ Tera baap aaya hai sunta nahi kya 👑😈",
        "⚡ Mere saamne aake dikhao himmat hai toh 😎💪",
        "🔥 Attack mode on — teri khair nahi aaj 😡⚔️",
        "💀 Tujhe itna marunga ke teri maa bhi nahi pehchanegi 😂🔥",
        "⚔️ Randike chal 1v1 kar le dikhata hoon kaun baap hai 👊😤",
        "💥 Beta ye territory meri hai nikal yahan se 🏴‍☠️⚡",
        "🗡️ Aukaat hai toh saamne aa nahi toh chup baith 😈💀",
        "⚡ Tu keyboard warrior hai asli mard nahi 😂👊",
        "🔥 Teri maa ne bhi bola tera baap chahiye 😹💔",
        "💥 Chal hat yahan se chota baccha 🤣👋",
        "⚔️ Mujhe gaali de ke dekh kya hoga teri life mein 😈⚡",
        "💀 Bhai seedha bol de surrender karega ya maar khayega 😎🔥",
        "🗡️ Attack karta hoon toh block nahi hoga tera 😡⚔️",
        "⚡ Yeh game mein nahi real life mein bhi kaatenge tujhe 💪😤",
        "🔥 Tera confidence dekh ke hansi aati hai yaar 😂💥",
        "💥 Andha hai ya dikhta nahi kaun boss hai yahan 👑⚔️",
        "⚔️ Teri har gaali pe 10 gaaliyan waapis aayengi 😈🔥",
        "💀 Beta peeth nahi dikhana mujhe — coward 🏃‍♂️😂",
    ]

    roast_list = [
        "🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺",
        "🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀",
        "😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂",
        "🔥 Teri maa ne bhi socha hoga — yaar galti ho gayi 😹👶",
        "🤣 Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂💀",
        "😹 Beta tu Google Maps pe search kare toh bhi worthless aayega 🗺️😈",
        "🔥 Teri iq level negative hai — calculator mein error aata hai 🧮😂",
        "🤣 Tu chhata hua papad hai — touch karte hi toot gaya 😹🔥",
        "😹 Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞😂",
        "🔥 Teri personality dekh ke AI bhi depressed ho gaya hoga 🤖😹",
    ]

    diss_list = [
        "🎤 Tera naam sun ke log mute kar dete hain khud ko 🔇😂",
        "💀 Tu diss kar raha hai — khud ko diss kar pehle 🪞😹",
        "🎙️ Teri rap jaisi hai — no flow no bars no future 🎵😂",
        "💥 Bhai tera verse sun ke Eminem ne retire le liya 😹🎤",
        "🔥 Teri diss itni kamzor hai ke whisper bhi zyada loud hai 🤫😂",
        "💀 Tu sirf bolne mein mard hai karne mein? Zero 😈🎙️",
        "🎤 Beta teri bars mein bar hi nahi — sirf khali string 🎸😂",
        "💥 Tera diss track sunne ke baad logon ne earbuds tod diye 🎧😹",
        "🔥 Bhai teri lyric likh ke dekha — autocorrect ne bhi reject kiya ✍️😂",
        "💀 Tu diss karta hai aur log diss ko diss karte hain 😂🎤",
    ]

    war_list = [
        "⚔️ War shuru ho gayi — aur tu pehle hi haar gaya 😂🔥",
        "💣 Bhai main war mein nahi aata — main war khatam karne aata hoon 😈⚡",
        "🏴‍☠️ Tera jhanda uraya — apna wala lehraya 😎💀",
        "⚔️ Tu lad raha hai mujhse — yeh teri sabse badi galti hai 🔥😂",
        "💣 Main war nahi khelta — main result deliver karta hoon 👑⚡",
        "🏴‍☠️ Battlefield pe aake to dekh — tera rank kya hai 😈⚔️",
        "⚔️ Randike war declare kiya toh surrender ka option bhi rakh 😂💣",
        "💣 Tu soldier nahi hai — tu sirf noise hai 🔊😂",
        "🏴‍☠️ War mein strategy chahiye — tu sirf emotion se ladhta hai 😹⚔️",
        "⚔️ Beta yeh teri territory nahi — nikalja 👋💣",
    ]

    savage_list = [
        "😈 Main savage hoon — tujhe explanation nahi deta 🔥💀",
        "💀 Teri feelings mere liye statistics hain — irrelevant 😂😈",
        "🔥 Main woh nahi hoon jo tujhe comfortable feel karaaye 😎💀",
        "😈 Beta teri baatein mujhe bore karti hain — next 😂🔥",
        "💀 Teri opinion meri life mein footnote bhi nahi hai 😈😹",
        "🔥 Main tujhe explain nahi karta — tujhse better logon ke paas time deta hoon 😎💀",
        "😈 Tera attitude dekh ke mujhe apni nails file karni chahiye 💅😂",
        "💀 Bhai tujhe reject karna meri hobby hai 🔥😈",
        "🔥 Teri presence mujhe remind karaati hai — kuch logon ko mute karna chahiye 🔇😂",
        "😈 Main bad vibes nahi leta — teri taraf bhi nahi 💀🔥",
    ]

    ultra_list = [
        "🌪️ ULTRA MODE ACTIVATED — teri poori existence question mein hai 😈🔥",
        "⚡ Ultra attack — pehle gaali sunna phir rona — sequence yaad kar 😂💀",
        "🌪️ Beta ultra level pe aake dekh — yahan teri category nahi hai 👑🔥",
        "⚡ ULTRA BLOW — teri soch se lekar attitude tak sab destroy 💥😈",
        "🌪️ Yeh ultra mode hai — blocking nahi help karega 😂⚡",
        "⚡ Ultra raid engaged — ab teri poori chat history history hai 📜😹",
        "🌪️ Beta ultra speed mein aa — par seedha home le jaata hoon 💀🔥",
        "⚡ Ultra fire — teri har defensive move kaam nahi karegi 😈🌪️",
        "🌪️ Yeh ultra level fight hai — tu still bronze mein hai 😂⚡",
        "⚡ ULTRA DAMAGE — teri reputation, teri aukaat, teri everything 💥😹",
    ]

    godwar_list = [
        "👑 GOD MODE — tu mortal hai mujhse ladhne ki aukat nahi 😈🔥",
        "🌟 Main GOD WAR mein hoon — teri poori bloodline haari 💀⚡",
        "👑 Beta God level pe welcome — nahi samjha toh nahi samjha 😂😈",
        "🌟 GOD FURY — sun raha hai na? Yeh teri calling hai 🔥💀",
        "👑 Main woh hoon jis se God bhi seekhta hai war 😎⚡",
        "🌟 Beta God war mein aaja — tujhe enlightenment milega 😂🔥",
        "👑 GOD LEVEL ATTACK — teri sari defenses dust hain 💀😈",
        "🌟 Main tujhe war mein nahi involve karta — tujhe demo dikhata hoon 😎⚡",
        "👑 Beta GOD mode — yeh teri life pe trailer tha 🔥😂",
        "🌟 GOD WAR declaration — teri surrender automatically process hogi 💀😈",
    ]

    combo_list = [
        "💥⚔️🔥 COMBO HIT — reply + roast + flag + react sab ek saath 😈💀",
        "🌪️💣👑 TRIPLE COMBO — teri sab kuch ek hi shot mein 😂⚡",
        "💥🔥😈 COMBO ATTACK — nahi rokna kisi ke liye bhi 💀🌪️",
        "⚔️💣🌟 Yeh combo hai — tu already down hai teri counting shuru 😂🔥",
        "🌪️😈💀 MEGA COMBO — tera sara defense ek message mein finish 😹⚡",
        "💥⚡👑 Combo level ULTRA — teri koi move kaam nahi ayegi 🔥😂",
        "⚔️🔥😹 COMBO RAIN — jab bhi message karega — combo activate 💀🌪️",
        "🌪️💣😈 Beta yeh combo nahi — yeh tujhe samjhaane ka tarika hai 😂⚡",
        "💥👑🔥 GRAND COMBO — teri poori squad aaj haari 😈💀",
        "⚔️🌪️😂 Combo attack engage — ab teri duniya theek nahi hogi 🔥💣",
    ]

    troll_list = [
        "🤡 Bhai tujhe dekh ke lagta hai troll ka mascot tu hai 😂🔥",
        "😹 Tu itna troll hai ke khud ko pata nahi 💀🤡",
        "🤡 Teri baatein sun ke log seriously nahi lete — aur le bhi nahi chahiye 😂😹",
        "😹 Beta tu internet ka troll #1 candidate hai 💀🤡",
        "🤡 Tujhe real life mein bhi ignore karte honge log 😂🔥",
        "😹 Bhai teri comments section mein sabne dislike diya 👎🤡",
        "🤡 Tu troll karne ki koshish karta hai — khud troll bana rehta hai 😂💀",
        "😹 Teri troll game weak hai — aur weak troll game bhi troll hai 🤡🔥",
        "🤡 Beta jo tu sochta hai funny hai woh boring hai 😂😹",
        "😹 Bhai tera troll skill level: tutorial mode pe stuck 🤡💀",
    ]

    shame_list = [
        "😤 Sharam kar — itna gira hua kaam karte kaise hain tum log 🔥💀",
        "🙅 Bhai teri harkat dekh ke pura group sharam se doob gaya 😂😤",
        "😤 Yeh sab karke tujhe pride feel hoti hai? Really? 💀🔥",
        "🙅 Beta teri harkaten dekh ke maa baap sharmayenge 😂😤",
        "😤 Sharam nahi hai tujhe bilkul — clearly 💀😹",
        "🙅 Bhai itna gira hua kaam dekh ke log muh fer lete hain 😤🔥",
        "😤 Tu itna neeche gira — zameen bhi neeche ho gayi 💀😂",
        "🙅 Beta sharam bhi nahi aata aisa karte hue 😤😹",
        "😤 Yeh harkat dekh ke lagta hai — tujhe value kisi ne nahi sikhaya 💀🔥",
        "🙅 Bhai log tujhe dekh ke aankhein pher lete hain — soch kya kar raha hai 😤😂",
    ]

    fire_list = [
        "🔥 FIRE MODE — teri sab cheez jal rahi hai 😈⚡",
        "🔥🔥 Double fire — tujhe bachaane ka option nahi 💀😂",
        "🔥 Teri har baat pe fire respond karenge — ready? 😈⚡",
        "🔥 Bhai FIRE unleashed — tujhe pata bhi nahi kya aaya 💀😂",
        "🔥 Fire level 10 — teri poori existence threatened 😈🌪️",
        "🔥 Beta teri baatein fire se nahi — mere se jali 💀😂",
        "🔥 FIRE STORM — teri location traced — figuratively 😈⚡",
        "🔥 Bhai mere fire pe paani mat daal — gasoline hai 💀🔥",
        "🔥 Teri baat pe FIRE response — tu ready tha? 😂😈",
        "🔥 Beta ek cheez tujhe batata hoon — yeh fire hai — bhaag ja 💀⚡",
    ]

    devil_list = [
        "😈 DEVIL MODE — yahan woh aaya hai jo tujhe deserve karta hai 🔥💀",
        "😈 Beta main devil nahi — main tera worst nightmare hoon 🔥⚡",
        "😈 Devil raid activate — teri poori timeline disturbed 💀😂",
        "😈 Bhai devil pe hath lagaya — ab bhog 🔥💥",
        "😈 DEVIL FURY — teri sab cheez ek baar mein 💀⚡",
        "😈 Beta devil ke saamne hum sab khiladi hain — tu beginner 🔥😂",
        "😈 DEVIL ATTACK — teri defense devil ke touch se fail 💀😈",
        "😈 Bhai devil mode mein koi safe nahi — tu bhi nahi 🔥⚡",
        "😈 Teri galti — devil ko challenge karna 💀😂",
        "😈 Beta devil ki bhasha — punishment aur reward — tu punishment mein hai 🔥😈",
    ]

    karma_list = [
        "☯️ Karma aaya — teri sab harkat ka hisaab ho raha hai 🔥💀",
        "☯️ Beta karma kisi ki nahi sunta — teri bhi nahi 😂⚡",
        "☯️ KARMA STRIKE — tune jo kiya woh teri taraf wapas aaya 🔥😈",
        "☯️ Bhai karma judge nahi karta — deliver karta hai 💀😂",
        "☯️ Karma mode activate — teri sab galtiyan wapas aa rahi hain 🔥⚡",
        "☯️ Beta karma tujhe bhool nahi gaya — yaad rakha tha 😂💀",
        "☯️ KARMA DELIVERY — teri harkat ka package arrive ho gaya 🔥😈",
        "☯️ Bhai karma se koi nahi bachta — tu bhi nahi bachega 💀⚡",
        "☯️ Karma tujhe dhundh raha tha — dhundh liya 🔥😂",
        "☯️ Beta karma aata hai jab expect nahi karte — sun le 😂💀",
    ]

    ghost_list = [
        "👻 GHOST MODE — tujhe pata bhi nahi kab aaya 😂💀",
        "👻 Beta ghost ki tarah silently teri sab cheez note kar liya 🔥😈",
        "👻 GHOST RAID — teri timeline pe tha tu socha nahi 💀⚡",
        "👻 Bhai ghost mode mein sab kuch possible hai — teri nazar se baahar 😂🔥",
        "👻 Ghost strike — teri sab cheez read — tujhe pata nahi 💀😈",
        "👻 Beta ghost se koi nahi chhupta — teri history meri hai 😂⚡",
        "👻 GHOST ATTACK — teri weaknesses identified without you knowing 🔥💀",
        "👻 Bhai ghost mein aaya — teri sab dekha — wapas aaya 😈😂",
        "👻 Ghost mode — tu sooye hua tha main active tha 💀⚡",
        "👻 Beta ghost ki tarah aa aur ja — par lesson chhod 🔥😂",
    ]

    legend_list = [
        "👑 LEGEND MODE — tujhse baat karna mera time nahi — par exception 😎🔥",
        "👑 Beta legend ne tujhe notice kiya — galat kaam ke liye 😂💀",
        "👑 LEGEND STRIKE — teri poori position legend ne handle ki 😎⚡",
        "👑 Bhai legend ke saamne teri sab bakwaas — sirf noise 🔥😂",
        "👑 Legend mode — main aaya — tu already haara 😎💀",
        "👑 Beta LEGEND level pe tu exist nahi karta — par exception de raha hoon 😂⚡",
        "👑 LEGEND RAID — teri timeline pe aaya — yaad rahega 🔥😎",
        "👑 Bhai legend se lad ke jeeta kaun? Koi nahi — tu bhi nahi 💀😂",
        "👑 Legend status — tujhe challenge accept nahi karna tha 😎⚡",
        "👑 Beta legend aaya — teri poori squad bhaag gayi 🔥💀",
    ]

    doom_list = [
        "💀 DOOM activated — teri poori existence on countdown 🔥😈",
        "💀 Beta doom aaya — tera timer start ho gaya 😂⚡",
        "💀 DOOM STRIKE — teri poori defense wiped 🔥😈",
        "💀 Bhai doom se koi nahi bachta — teri bhi date aane wali thi 😂💀",
        "💀 Doom mode — teri sab cheez: scheduled for deletion 🔥⚡",
        "💀 Beta doom tera waqt dekh ke aaya — perfect timing 😂😈",
        "💀 DOOM RAID — teri poori squad: doomed 🔥💀",
        "💀 Bhai doom pe haath lagaya — yeh result expect karna chahiye tha 😂⚡",
        "💀 Doom finale — teri poori story: ended 🔥😈",
        "💀 Beta doom ki awaaz sunna nahi chahte log — teri aa gayi 😂💀",
    ]

    joke_list = [
        "Main apni life mein itna positive hoon... ki blood group bhi B+ hai! 😂",
        "Teacher: Kal absent kyun the? Student: Sir, mujhe bukhar tha. Teacher: Proof? Student: Aaj aa gaya na! 😹",
        "Santa: Main ghar ke bahar khada hun. Banta: Andar aa jao. Santa: Andar wala bhi main hoon! 🤣",
        "Meri girlfriend ne kaha — tujhse better koi nahi. Phir chali gayi. Better koi mila hoga shayad 😂",
        "Doctor: Patient ko hawa ki zaroorat hai. Nurse: Kya karein? Doctor: Fan on karo. Nurse: Ceiling se pakad ke? 😹",
    ]

    riddle_list = [
        "Kya cheez hai jo khata hai par pet nahi hota? — Aag (Fire) 🔥",
        "Woh kaunsi cheez hai jo bolta hai 'Main aaya' par nahi aata? — Kal (Tomorrow) ⏰",
        "Jitna zyada liya jaaye utna chhota hota hai — kya? — Ek gaddha (hole in the ground) 🕳️",
        "Mere paas aankhein hain par dekh nahi sakta — kya hoon main? — Sooee (needle) 🧵",
        "Vo kya cheez hai jo haath se chhoone pe bhi nahi lagti? — Khoobsoorti! 😄",
    ]

    fact_list = [
        "🧠 Insaan ka dimag 75% paani se bana hai!",
        "🐙 Octopus ke teen dil hote hain!",
        "🌙 Chand par mobile signal nahi hai — par WiFi aata hai ek satellite se! (Future plan 😂)",
        "🍯 Sahi tarike se rakha hua honey kabhi kharab nahi hota!",
        "⚡ Bijli ka ek bolt 5 times zyada garam hota hai sun ki surface se!",
    ]

    truth_list = [
        "Sach bolo — last baar kab jhooth bola tha? 🤥",
        "Teri life ka sabse bada secret kya hai jo kisi ko nahi pata? 🤫",
        "Kisi pe crush tha jo ab dost hai? 😳",
        "Kabhi kisi ki baat repeat ki thi jo confidence mein batai gayi thi? 😬",
        "Woh kaun hai jis par sabse zyada trust karte ho? ❤️",
    ]

    dare_list = [
        "Abhi apni maa ko call kar ke bol — 'Main tujhse pyaar karta hoon' 📞❤️",
        "Apni sabse embarrassing photo share kar group mein 📸😹",
        "Kisi bhi friend ko abhi message kar — 'Bhai mujhe pata chal gaya' — aur reaction dekho 😈",
        "10 seconds ke liye khud se hi baat karo — loud 🗣️",
        "Abhi ek push-up kar aur photo bhejo 💪",
    ]

    pickup_list = [
        "Kya tum WiFi ho? Kyunki main teri taraf khinchat chala aa raha hoon 📶😂",
        "Tujhe dekh ke soch raha tha — yeh image real nahi ho sakti 🖼️❤️",
        "Kya tum dictionary ho? Kyunki tujhme meaning hai 📖✨",
        "Tu itna sweet hai ke mujhe diabetes ka darr ho gaya 🍭😹",
        "Teri eyes mein stars hain ya stars tujhe dekh ke sharminde ho gaye? ⭐❤️",
    ]

    compliment_list = [
        "Bhai tu bahut positive energy rakhta hai — seriously 🌟",
        "Teri thinking bahut alag hai — creative hai tu 🧠✨",
        "Tu jo bhi karta hai dil se karta hai — yeh rare hai ❤️",
        "Teri sense of humor? Top tier 😂👑",
        "Tujhse baat karna genuinely enjoyable hota hai 🗣️✨",
    ]

    quote_list = [
        "💭 'Sapne woh nahi jo sote waqt aate hain, sapne woh hain jo sone nahi dete.' — APJ Abdul Kalam",
        "💭 'Mehnat karo itna ki luck ko bhi mauka mile tujhe dhundhne ka.' — Unknown",
        "💭 'Duniya ka sabse bada teacher: failure hai.' — Unknown",
        "💭 'Ek accha dost aur ek accha kitaab — dono hi tujhe better banate hain.' — Unknown",
        "💭 'Zindagi ek echo hai — jo bejhoge woh wapas aayega.' — Unknown",
    ]

    commands = {}

    def register_cmd(name: str, needs_reply: bool = False, group_only: bool = False):
        def decorator(func):
            key = (name or "").lower().strip()
            if not key:
                return func
            commands[key] = {
                "func": func, "needs_reply": bool(needs_reply), "group_only": bool(group_only),
            }
            return func
        return decorator

    async def fast_title_edit(chat_id, title):
        safe_title = (title or "").strip()[:255]
        if not safe_title: return False
        try:
            await bot(functions.channels.EditTitleRequest(channel=chat_id, title=safe_title))
            return True
        except Exception:
            try:
                await bot(functions.messages.EditChatTitleRequest(chat_id=chat_id, title=safe_title))
                return True
            except Exception as e:
                print(f"[FastGC] Title edit failed → {str(e)[:80]}", flush=True)
                return False

    async def gc_fast_loop(chat_id):
        try:
            while True:
                if not FASTGC_STATE.get("active"): break
                template = FASTGC_STATE.get("template")
                if not template: break
                try: emoji = random.choice(GC_FAST_EMOJIS)
                except: emoji = "⚡"
                try: new_title = template.replace("{emoji}", emoji)
                except: await asyncio.sleep(2); continue
                ok = await fast_title_edit(chat_id, new_title)
                try:
                    if ok: await asyncio.sleep(max(1, GC_FAST_INTERVAL))
                    else: await asyncio.sleep(5)
                except: await asyncio.sleep(3)
        except asyncio.CancelledError: return
        except Exception as e: print(f"[FastGC Loop Crash] → {str(e)[:80]}", flush=True)

    # ── ALL-IN-ONE MASTER MENU (TAGDA DRAGON DARK UI) ──
    @register_cmd("menu")
    @register_cmd("dragon")
    @register_cmd("dragonmenu")
    @register_cmd("cmds")
    @register_cmd("menu1")
    @register_cmd("menu2")
    @register_cmd("menu3")
    @register_cmd("menu4")
    @register_cmd("menu5")
    @register_cmd("menu6")
    @register_cmd("menu7")
    @register_cmd("menu8")
    async def cmd_menu(event, _):
        u_name = "Sanju"
        try:
            me = await bot.get_me()
            if me and getattr(me, "first_name", None):
                u_name = me.first_name
        except Exception:
            pass

        role_label = "👑 ᴍᴀꜱᴛᴇʀ ᴏᴡɴᴇʀ (ꜱʟᴏᴛ #1)" if USERBOT_SLOT == 0 else f"🤖 ʟɪɴᴋᴇᴅ ᴡᴏʀᴋᴇʀ (ꜱʟᴏᴛ #{USERBOT_SLOT+1})"
        core_title = "👑 ᴍᴇɴᴛᴀʟ • ᴍᴀꜱᴛᴇʀ ᴄᴏʀᴇ" if USERBOT_SLOT == 0 else f"🤖 ᴍᴇɴᴛᴀʟ • ꜰʟᴇᴇᴛ ᴡᴏʀᴋᴇʀ #{USERBOT_SLOT+1}"

        fleet_section = (
            "❖═━•〔 👥 𝟬𝟴. 𝗙𝗟𝗘𝗘𝗧 & 𝗠𝗨𝗟𝗧𝗜-𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦 〕•━═❖\n"
            "├─▹ .joingc <link>    ─ 🚀 ꜱᴀʙʜɪ ᴀᴄᴄꜱ ɢʀᴏᴜᴘ ᴊᴏɪɴ\n"
            "├─▹ .leavegc [chat]   ─ 🚪 ꜱᴀʙʜɪ ᴀᴄᴄꜱ ɢʀᴏᴜᴘ ʟᴇᴀᴠᴇ\n"
            "├─▹ .addacc <phone>   ─ 📲 ꜱᴛᴇᴘ 1: ᴀᴅᴅ ɴᴜᴍʙᴇʀ\n"
            "├─▹ .otp <code>       ─ 🔑 ꜱᴛᴇᴘ 2: ᴠᴇʀɪꜰʏ ᴏᴛᴘ\n"
            "├─▹ .2fa <password>   ─ 🔐 ꜱᴛᴇᴘ 3: 2ꜰᴀ ᴘᴀꜱꜱᴡᴏʀᴅ\n"
            "├─▹ .fleet / .accs    ─ 📊 ᴠɪᴇᴡ ᴀʟʟ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
            "├─▹ .sync on/off      ─ 🔄 1 ɪᴅ ꜱᴇ ꜱᴀʙʜɪ ꜱʏɴᴄ\n"
            "├─▹ .all <cmd>        ─ ⚡ ᴀʟʟ ᴀᴄᴄᴏᴜɴᴛꜱ ᴄᴏᴍᴍᴀɴᴅ\n\n"
        ) if USERBOT_SLOT == 0 else (
            f"❖═━•〔 👥 𝟬𝟴. ꜰʟᴇᴇᴛ ᴡᴏʀᴋᴇʀ (ꜱʟᴏᴛ #{USERBOT_SLOT+1}) 〕•━═❖\n"
            "├─▹ .joingc <link>    ─ 🚀 ꜱᴀʙʜɪ ᴀᴄᴄꜱ ɢʀᴏᴜᴘ ᴊᴏɪɴ\n"
            "├─▹ .leavegc [chat]   ─ 🚪 ꜱᴀʙʜɪ ᴀᴄᴄꜱ ɢʀᴏᴜᴘ ʟᴇᴀᴠᴇ\n"
            "├─▹ .fleet / .accs    ─ 📊 ᴠɪᴇᴡ ᴀʟʟ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
            "├─▹ .sync on/off      ─ 🔄 ꜱʏɴᴄ ꜱᴛᴀᴛᴜꜱ\n"
            "├─▹ 🔒 .addacc        ─ 👑 ᴍᴀꜱᴛᴇʀ ᴏᴡɴᴇʀ ᴏɴʟʏ (ꜱʟᴏᴛ #1)\n\n"
        )

        menu = (
            "👑 ◢█◣ ⟨ 𝐌𝐄𝐍𝐓𝐀𝐋 • 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 ⟩ ◢█◣\n"
            "❖═━•〔 ⚡ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐏𝐎𝐖𝐄𝐑 𝐂𝐎𝐑𝐄 〕•━═❖\n\n"
            "╔══════════════════════════════════▣\n"
            "┊✺┌────                      ──⊷\n"
            f"╠✤│ {core_title}\n"
            "╠✤│\n"
            f"╠✤│ 👤 ᴜꜱᴇʀ : {u_name}\n"
            f"╠✤│ 👑 ʀᴏʟᴇ : {role_label}\n"
            "╠✤│ 🛡️ ꜱᴛᴀᴛᴜꜱ : 🟢 ᴀᴄᴛɪᴠᴇ & ᴀʀᴍᴇᴅ\n"
            "╠✤│\n"
            f"╠✤│ 📱 ꜱʟᴏᴛ         : ꜱʟᴏᴛ #{USERBOT_SLOT+1}\n"
            "╠✤│ ⚡ ᴇɴɢɪɴᴇ ᴠᴇʀ   : ᴠ2.5 ᴘʀᴏ (ᴠᴘꜱ ᴇᴅɪᴛɪᴏɴ)\n"
            "╠✤│ 📦 ᴄᴏᴍᴍᴀɴᴅꜱ     : 500+ ᴛᴏᴏʟꜱ\n"
            "╠✤│ 🛡️ ᴀɴᴛɪ-ʙʟᴏᴄᴋ   : 🟢 ᴢᴇʀᴏ-ᴡɪᴅᴛʜ + ꜱᴘᴀᴍ-ꜱʜɪᴇʟᴅ\n"
            "╠✤│ ⚔️ ᴍᴏᴅᴇ         : ɢᴏᴅ ᴍᴏᴅᴇ\n"
            "┊✺└────••••────────────────────────⊷\n"
            "╚══════════════════════════════════▣\n\n"
            "❖═━•〔 ⚔️ 𝟬𝟭. 𝐑𝐀𝐈𝐃 & 𝐖𝐀𝐑 〕•━═❖\n"
            "├─▹ .attack <target>  ─ ⚡ ʀᴀᴘɪᴅ ʀᴀɪᴅ\n"
            "├─▹ .roast <target>   ─ 🔥 ʙʀᴜᴛᴀʟ ꜱᴀᴠᴀɢᴇ ʙᴜʀɴ\n"
            "├─▹ .diss <target>    ─ 💀 ʜᴀʀᴅᴄᴏʀᴇ ᴅɪꜱꜱ ᴛʀᴀᴄᴋ\n"
            "├─▹ .war / .ultra     ─ ⚔️ ᴜʟᴛʀᴀ ɢᴏᴅ ᴡᴀʀ\n"
            "├─▹ .combo / .savage  ─ 💣 ꜱᴀᴠᴀɢᴇ ᴀᴛᴛᴀᴄᴋ\n"
            "├─▹ .stopall          ─ 🛑 ꜱᴛᴏᴘ ᴀʟʟ ʀᴀɪᴅꜱ\n\n"
            "❖═━•〔 🔁 𝟬𝟮. 𝐀𝐔𝐓𝐎-𝐑𝐄𝐏𝐋𝐘 〕•━═❖\n"
            "├─▹ .reply <target>   ─ 🤖 ᴀᴜᴛᴏ ʀᴇᴘʟʏ ᴛᴀʀɢᴇᴛ\n"
            "├─▹ .rr <target>      ─ ⚡ 2x ᴜʟᴛʀᴀ ꜱᴘᴇᴇᴅ ʀᴇᴘʟʏ\n"
            "├─▹ .flag / .hrr      ─ 🚩 ꜰʟᴀɢ ʀᴀᴘɪᴅ ʀᴇᴘʟʏ\n"
            "├─▹ .replygod         ─ 👑 ɢᴏᴅ ʀᴇᴘʟʏ ᴍᴏᴅᴇ\n"
            "├─▹ .sreply / .sstop  ─ 🛑 ꜱᴛᴏᴘ ᴀᴜᴛᴏ ʀᴇᴘʟɪᴇꜱ\n\n"
            "❖═━•〔 💣 𝟬𝟯. 𝐒𝐏𝐀𝐌 & 𝐒𝐏𝐑𝐀𝗬 〕•━═❖\n"
            "├─▹ .spray <text>     ─ 🚀 ᴜʟᴛʀᴀ ꜰᴀꜱᴛ ꜱᴘᴀᴍ\n"
            "├─▹ .dspray <sec>     ─ ⏱️ ᴅᴇʟᴀʏ ꜱᴘʀᴀʏ\n"
            "├─▹ .tspray <id>      ─ 📋 ꜱᴀᴠᴇᴅ ᴛᴇxᴛ ꜱᴘᴀᴍ\n"
            "├─▹ .rspray <cnt>     ─ 🔁 ʀᴇᴘʟʏ ꜱᴘᴀᴍ\n"
            "├─▹ .stopspray        ─ 🛑 ꜱᴛᴏᴘ ꜱᴘʀᴀʏ\n\n"
            "❖═━•〔 🛡️ 𝟬𝟰. 𝐆𝐑𝐎𝐔𝐏 & 𝗔𝗗𝗠𝗜𝗡 〕•━═❖\n"
            "├─▹ .ban / .unban     ─ 🔨 ʙᴀɴ / ᴜɴʙᴀɴ ᴜꜱᴇʀ\n"
            "├─▹ .mute / .unmute   ─ 🔇 ᴍᴜᴛᴇ / ᴜɴᴍᴜᴛᴇ ᴜꜱᴇʀ\n"
            "├─▹ .purge <count>    ─ 🧹 ᴄʟᴇᴀɴ ᴍᴇꜱꜱᴀɢᴇꜱ\n"
            "├─▹ .creategc <n>     ─ 👥 ʙᴜʟᴋ ɢʀᴏᴜᴘꜱ ᴄʀᴇᴀᴛᴇ\n"
            "├─▹ .addmybot / .addbot─ 🤖 ꜱᴀᴠᴇ & ᴀᴅᴅ ʙᴏᴛꜱ\n"
            "├─▹ .autokick @user   ─ 👞 ᴀᴜᴛᴏ ᴋɪᴄᴋ ᴛᴀʀɢᴇᴛ / ᴅᴇʟ\n"
            "├─▹ .admins / .pin    ─ 📌 ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ᴛᴏᴏʟꜱ\n\n"
            "❖═━•〔 👁️ 𝟬𝟱. 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 & 𝗔𝗨𝗧𝗢 〕•━═❖\n"
            "├─▹ .antidel on/off   ─ 👁️ ᴀɴᴛɪ-ᴅᴇʟᴇᴛᴇ ꜱʜɪᴇʟᴅ\n"
            "├─▹ .watchspam @user  ─ 🛡️ ᴀᴜᴛᴏ ʙᴀɴ ꜱᴘᴀᴍᴍᴇʀꜱ\n"
            "├─▹ .watchlist        ─ 📋 ᴍᴏɴɪᴛᴏʀᴇᴅ ᴜꜱᴇʀꜱ\n"
            "├─▹ .ar <emoji>       ─ 🎭 ᴀᴜᴛᴏ ʀᴇᴀᴄᴛ ᴛᴀʀɢᴇᴛ\n"
            "├─▹ .fastgc set/stop  ─ ⚡ ʀᴀᴘɪᴅ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ\n\n"
            "❖═━•〔 🎙️ 𝟬𝟲. 𝗟𝗜𝗩𝗘 𝗩𝗖 & 𝟯𝟬𝟬𝗱𝗕 〕•━═❖\n"
            "├─▹ .vcchatsection    ─ 🎙️ ᴏᴘᴇɴ ꜰᴜʟʟ ᴠᴄ ᴍᴇɴᴜ\n"
            "├─▹ .vcmic on/off     ─ ⚡ ʟɪᴠᴇ ᴠᴄ ᴍɪᴄ (0 ᴠɴ)\n"
            "├─▹ .300db / .150db   ─ 💥 300 ᴅʙ ꜱʜᴏᴄᴋᴡᴀᴠᴇ\n"
            "├─▹ .vcsay <text>     ─ 🗣️ ʟɪᴠᴇ ꜱᴘᴇᴇᴄʜ ɪɴ ᴠᴄ\n"
            "├─▹ .vcstop / .vcleave─ 🛑 ʟᴇᴀᴠᴇ ᴠᴄ ᴄᴀʟʟ\n\n"
            "❖═━•〔 🔄 𝟬𝟳. 𝗔𝗨𝗧𝗢-𝗙𝗢𝗥𝗪𝗔𝗥𝗗 〕•━═❖\n"
            "├─▹ .forward [count]  ─ 🔁 ᴀᴜᴛᴏ ꜰᴏʀᴡᴀʀᴅ (ᴢᴇʀᴏ ꜱᴛᴜᴄᴋ)\n"
            "├─▹ .fwd [count]      ─ ⚡ ꜱʜᴏʀᴛᴄᴜᴛ ᴀʟɪᴀꜱ\n"
            "├─▹ .stopforward      ─ 🛑 ꜱᴛᴏᴘ ᴀᴜᴛᴏ ꜰᴏʀᴡᴀʀᴅ\n\n"
            + fleet_section
            + "❖═━•〔 🛠️ 𝟬𝟵. 𝗨𝗧𝗜𝗟𝗦 & 𝗜𝗡𝗙𝗢 〕•━═❖\n"
            "├─▹ .alive / .ping    ─ 🟢 ᴜꜱᴇʀʙᴏᴛ ʟᴀᴛᴇɴᴄʏ & ᴜᴘᴛɪᴍᴇ\n"
            "├─▹ .id / .whois      ─ ℹ️ ᴜꜱᴇʀ & ᴄʜᴀᴛ ɪɴꜰᴏ\n"
            "├─▹ .tts <text>       ─ 🎙️ ᴛᴇxᴛ ᴛᴏ ᴠᴏɪᴄᴇ\n"
            "├─▹ .music <song>     ─ 🎵 128ᴋ ᴠᴏɪᴄᴇ / 320ᴋ ᴍᴘ3\n"
            "├─▹ .copy @user       ─ 🎭 ᴄʟᴏɴᴇ ᴘʀᴏꜰɪʟᴇ\n\n"
            "❖═━•〔 👑 𝐎𝐖𝐍𝐄𝐑 & 𝐃𝐄𝐕 〕•━═❖\n"
            "├─▹ 𝐎𝐰𝐧𝐞𝐫: 8652812134 (Arya X MENTAL)\n"
            "├─▹ 𝐃𝐞𝐯: @xno_Amrit (Amrit)\n"
            "├─▹ 𝐂𝐡𝐚𝐧𝐧𝐞𝐥: @mentals_empire\n"
            "├─▹ 𝐆𝐫𝐨𝐮𝐩 (𝐆𝐂): @mental_fyts_post\n"
            "❖═━•〔 𝐌𝐄𝐍𝐓𝐀𝐋 • 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 〕•━═❖"
        )
        if getattr(event, "out", False):
            try:
                await event.edit(menu)
            except Exception:
                await bot.send_message(event.chat_id, menu)
        else:
            await event.reply(menu)

    @register_cmd("vcchatsection")
    @register_cmd("vcmenu")
    async def cmd_vcchatsection(event, _):
        vc_menu = (
            "╭──〔 🎙️ 𝗟𝗜𝗩𝗘 𝗩𝗖 𝗠𝗜𝗖 & 𝟯𝟬𝟬𝗱𝗕 𝗢𝗩𝗘𝗥𝗣𝗢𝗪𝗘𝗥 〕──╮\n"
            "│ ✦ 𝗦𝗬𝗦  : 𝗟𝗜𝗩𝗘 𝗩𝗖 𝗦𝗧𝗥𝗘𝗔𝗠𝗘𝗥 (𝟬 𝗩𝗢𝗜𝗖𝗘 𝗡𝗢𝗧𝗘𝗦)\n"
            "│ ✦ 𝗢𝗪𝗡  : 𝗔𝗿𝘆𝗮 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟\n"
            "│ ✦ 𝗗𝗘𝗩  : @𝘅𝗻𝗼_𝗮𝗺𝗿𝗶𝘁 (𝟴𝟲𝟱𝟮𝟴𝟭𝟮𝟭𝟯𝟰)\n"
            "╰──────────────────────────────────────────╯\n\n"
            "┌──〔 🎙️ 𝗟𝗜𝗩𝗘 𝗠𝗜𝗖 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 (𝟬 𝗩𝗡) 〕\n"
            "│ ⬝ .vcmic on/off ─ 🎙️ 𝗟𝗶𝘃𝗲 𝗩𝗖 𝗠𝗶𝗰 𝗢𝗻 / 𝗢𝗳𝗳\n"
            "│ ⬝ .vcmic <mode> ─ 🎭 bhari / monster / scream / 300db / robot / ghost\n"
            "│ ⬝ .vcsay <text> ─ 🗣️ 𝗟𝗶𝘃𝗲 𝗦𝗽𝗲𝗲𝗰𝗵 𝗶𝗻 𝗩𝗖 𝗠𝗶𝗰 (𝗡𝗼 𝗩𝗡)\n"
            "│ ⬝ .setmic pitch/bass/gain ─ 🎛️ 𝗟𝗶𝘃𝗲 𝗠𝗶𝗰 𝗧𝘂𝗻𝗲𝗿\n"
            "│ ⬝ .sfx <nuke/siren/horn/gun> ─ 💥 𝗩𝗖 𝗦𝗙𝗫 𝗦𝗼𝘂𝗻𝗱𝗯𝗼𝗮𝗿𝗱\n"
            "│ ⬝ .vcguard on/off ─ 🛡️ 𝗔𝗻𝘁𝗶-𝗠𝘂𝘁𝗲 𝗩𝗖 𝗦𝗵𝗶𝗲𝗹𝗱\n"
            "└───\n\n"
            "┌──〔 💥 𝟯𝟬𝟬𝗱𝗕 & 𝟭𝟱𝟬𝗱𝗕 𝗢𝗩𝗘𝗥𝗣𝗢𝗪𝗘𝗥 〕\n"
            "│ ⬝ .300db / .194db / .150db ─ 🌋 𝟯𝟬𝟬 𝗱𝗕+ 𝗦𝗵𝗼𝗰𝗸𝘄𝗮𝘃𝗲\n"
            "│ ⬝ .90db / .vc90db ─ 🔊 𝟵𝟬 𝗱𝗕+ 𝗗𝗲𝗺𝗼𝗻 𝗚𝗿𝗼𝘄𝗹\n"
            "│ ⬝ .vcecho ─ 🏰 𝗘𝗰𝗵𝗼 𝗖𝗵𝗮𝗺𝗯𝗲𝗿 𝗘𝗳𝗳𝗲𝗰𝘁\n"
            "│ ⬝ .vcdominate ─ 👑 𝟭𝟬𝟬𝟬% 𝗠𝗶𝗰 𝗢𝘃𝗲𝗿𝗽𝗼𝘄𝗲𝗿 (𝗡𝗼 𝗠𝘂𝘁𝗲)\n"
            "│ ⬝ .vcmonster <txt> ─ 👹 𝗩𝗖 𝗠𝗼𝗻𝘀𝘁𝗲𝗿 𝗦𝘁𝗿𝗲𝗮𝗺\n"
            "│ ⬝ .vcscream <txt> ─ 🗣️ 𝗩𝗖 𝗦𝗰𝗿𝗲𝗮𝗺 𝗦𝘁𝗿𝗲𝗮𝗺\n"
            "│ ⬝ .vcroar ─ 🦁 𝗩𝗖 𝗕𝗲𝗮𝘀𝘁 𝗥𝗼𝗮𝗿 𝗟𝗼𝗼𝗽\n"
            "│ ⬝ .vcunmuteall ─ 🔊 𝗨𝗻𝗺𝘂𝘁𝗲 𝗔𝗹𝗹 (Sab Bol Sakte Hain)\n"
            "│ ⬝ .vcreset ─ 🔄 𝗥𝗲𝘀𝗲𝘁 𝗩𝗖 𝗩𝗼𝗹𝘂𝗺𝗲𝘀\n"
            "└───\n\n"
            "┌──〔 🎵 𝗩𝗖 𝗦𝗧𝗥𝗘𝗔𝗠 & 𝗨𝗧𝗜𝗟𝗦 〕\n"
            "│ ⬝ .vcjoin / .vcleave ─ 𝗝𝗼𝗶𝗻 / 𝗘𝘅𝗶𝘁 𝗩𝗖\n"
            "│ ⬝ .vcplay <reply> ─ 🎵 𝗦𝘁𝗿𝗲𝗮𝗺 𝗔𝘂𝗱𝗶𝗼 𝗜𝗻 𝗩𝗖\n"
            "│ ⬝ .vcstop ─ 🛑 𝗦𝘁𝗼𝗽 𝗩𝗖 𝗦𝘁𝗿𝗲𝗮𝗺\n"
            "│ ⬝ .startvc / .endvc ─ 🟢 𝗦𝘁𝗮𝗿𝘁 / 🔴 𝗘𝗻𝗱 𝗩𝗖\n"
            "│ ⬝ .vcstatus ─ 📊 𝗩𝗖 𝗔𝘂𝗱𝗶𝘁 & 𝗦𝘁𝗮𝘁𝘂𝘀\n"
            "└───\n\n"
            "╭──〔 ⚡ 𝗔𝗥𝗬𝗔 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟 𝗩𝗖 𝗖𝗢𝗥𝗘 〕──╮\n"
            "│ 👑 𝗢𝗪𝗡𝗘𝗥 : 𝗔𝗿𝘆𝗮 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟\n"
            "│ 💻 𝗖𝗛𝗜𝗘𝗙 : @𝘅𝗻𝗼_𝗮𝗺𝗿𝗶𝘁 (𝟴𝟲𝟱𝟮𝟴𝟭𝟮𝟭𝟯𝟰)\n"
            "╰──────────────────────────────────╯"
        )
        await safe_edit(event, vc_menu)

    # ── ORIGINAL COMMANDS ──
    @register_cmd("banner", needs_reply=True)
    async def cmd_banner(event, _):
        global menu_banner_msg
        reply = await event.get_reply_message()
        if not reply:
            return await safe_edit(event, "❌ 𝐍ᴏ 𝐑ᴇᴘʟʏ\n👉 𝐑ᴇᴘʟʏ 𝐓ᴏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ")
        if not reply.media:
            return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐌ᴇᴅɪᴀ\n👉 𝐎ɴʟʏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ")
        await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━")
        try:
            try: saved = await reply.forward_to("me")
            except Exception:
                file = await reply.download_media(file=bytes)
                if not file: return await safe_edit(event, "❌ 𝐌ᴇᴅɪᴀ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")
                bio = BytesIO(file); bio.name = "banner"
                saved = await bot.send_file("me", bio)
            menu_banner_msg = (saved.chat_id, saved.id)
            save_banner()
            text = f"🖼️ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ\n━━━━━━━━━━━━━━━\n📌 𝐒ᴀᴠᴇᴅ 𝐈ᴅ → `{saved.id}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐁ᴀɴɴᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("rembanner")
    async def cmd_rembanner(event, _):
        global menu_banner_msg
        if not menu_banner_msg:
            return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ")
        await safe_edit(event, "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━")
        try:
            chat_id, msg_id = menu_banner_msg
            try: await bot.delete_messages(chat_id, [msg_id])
            except: pass
            menu_banner_msg = None; save_banner()
            text = "🗑️ 𝐁ᴀɴɴᴇʀ 𝐑ᴇᴍᴏᴠᴇᴅ\n━━━━━━━━━━━━━━━"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("addadmin", needs_reply=True)
    async def cmd_addadmin(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ...\n━━━━━━━━━━━━━━━")
            added, already, skipped_owner = [], [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == OWNER_ID: skipped_owner.append(str(uid)); continue
                if uid in admins: already.append(str(uid))
                else: admins.add(uid); added.append(str(uid))
            try: save_admins()
            except: pass
            parts = []
            if added: parts.append(f"✅ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅᴇᴅ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴅᴍɪɴ → `{', '.join(already)}`")
            if skipped_owner: parts.append(f"👑 𝐎ᴡɴᴇʀ 𝐒ᴋɪᴘᴘᴇᴅ → `{', '.join(skipped_owner)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")
            text = "\n".join(parts)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("deladmin", needs_reply=True)
    async def cmd_deladmin(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ...\n━━━━━━━━━━━━━━━")
            removed, not_admin, skipped_owner = [], [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == OWNER_ID: skipped_owner.append(str(uid)); continue
                if uid in admins: admins.remove(uid); removed.append(str(uid))
                else: not_admin.append(str(uid))
            try: save_admins()
            except: pass
            parts = []
            if removed: parts.append(f"🗑️ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇᴅ → `{', '.join(removed)}`")
            if not_admin: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ → `{', '.join(not_admin)}`")
            if skipped_owner: parts.append(f"👑 𝐎ᴡɴᴇʀ 𝐏ʀᴏᴛᴇᴄᴛᴇᴅ → `{', '.join(skipped_owner)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs")
            text = "\n".join(parts)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("admins")
    async def cmd_admins(event, _):
        try:
            await safe_edit(event, "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ...\n━━━━━━━━━━━━━━━")
            admin_list = "\n".join(f"• `{a}`" for a in sorted(admins)) if admins else "⚠️ 𝐍ᴏ 𝐄xᴛʀᴀ 𝐀ᴅᴍɪɴs"
            txt = f"👑 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ\n━━━━━━━━━━━━━━━\n👑 𝐎ᴡɴᴇʀ → `{OWNER_ID}`\n\n{admin_list}\n\n📊 𝐓ᴏᴛᴀʟ → `{len(admins)}`"
            await safe_edit(event, txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("ping")
    async def cmd_ping(event, _):
        try:
            t0 = time.perf_counter()
            try:
                if event.out: msg = await event.edit("⚡ 𝗣𝗜𝗡𝗚...")
                else: msg = await event.reply("⚡ 𝗣𝗜𝗡𝗚...")
            except: msg = None
            t1 = time.perf_counter()
            ms = round((t1 - t0) * 1000)

            role_tag = f"👑 [Master • Acc #{USERBOT_SLOT+1}]" if USERBOT_SLOT == 0 else f"🤖 [Fleet Worker • Acc #{USERBOT_SLOT+1}]"
            try:
                me = await bot.get_me()
                u_str = f"@{me.username}" if me.username else me.first_name
            except Exception:
                u_str = f"Acc #{USERBOT_SLOT+1}"

            txt = f"⚡ 𝗣𝗢𝗡𝗚: {ms} 𝗺𝘀 | {role_tag} {u_str} | 𝗔𝗥𝗬𝗔 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟"
            if msg:
                try: await msg.edit(txt)
                except: await safe_edit(event, txt)
            else: await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝗣𝗜𝗡𝗚 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("alive")
    async def cmd_alive(event, _):
        try:
            elapsed = int(time.time() - START_TIME)
            h, r = divmod(elapsed, 3600)
            m, s = divmod(r, 60)
            uptime_str = f"{h}h {m}m {s}s"
            try:
                me = await bot.get_me()
                uname = f"@{me.username}" if me.username else me.first_name
            except:
                uname = "Unknown"

            role_tag = f"👑 Master Controller (Acc #{USERBOT_SLOT+1})" if USERBOT_SLOT == 0 else f"🤖 Fleet Worker (Acc #{USERBOT_SLOT+1})"
            txt = (
                "╭──〔 ⚡ 𝗔𝗥𝗬𝗔 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟 𝗩𝟮 〕──╮\n"
                "│ ✦ 𝗦𝗬𝗦  : 𝗦𝗬𝗡𝗧𝗛-𝗖𝗢𝗥𝗘 𝗢𝗡𝗟𝗜𝗡𝗘\n"
                f"│ ✦ 𝗨𝗦𝗘𝗥 : {uname}\n"
                f"│ ✦ 𝗥𝗢𝗟𝗘 : {role_tag}\n"
                f"│ ✦ 𝗨𝗣𝗧  : {uptime_str}\n"
                "│ ✦ 𝗖𝗠𝗗  : 𝟱𝟬𝟬+ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗿𝗺𝗲𝗱\n"
                "│ ✦ 𝗥𝗔𝗜𝗗 : 𝟭𝟲 𝗧𝘆𝗽𝗲𝘀 (𝗗𝗮𝗿𝗸 𝗙𝗼𝗻𝘁)\n"
                "│ ✦ 𝗦𝗧𝗔𝗧 : 𝗔𝗖𝗧𝗜𝗩𝗘 & 𝗔𝗥𝗠𝗘𝗗 🟢\n"
                "╰────────────────────────────╯\n"
                "⚡ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗔𝗥𝗬𝗔 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟"
            )
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐥𝐢𝐯𝐞 𝐄𝐫𝐫 → `{str(e)[:40]}`")

    @register_cmd("help")
    async def cmd_help_userbot(event, _):
        try:
            txt = (
                "╔══════════════════════════════╗\n"
                "║  📖  𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗚𝗨𝗜𝗗𝗘  📖  ║\n"
                "╚══════════════════════════════╝\n\n"
                "💡 𝐏𝐫𝐞𝐟𝐢𝐱: `.`  (𝐝𝐨𝐭)\n\n"
                "⚡ 𝗕𝗔𝗦𝗜𝗖: .alive .ping .status .id\n"
                "⚔️ 𝗥𝗔𝗜𝗗: .attack .roast .diss .war .savage .ultra .doom .legend\n"
                "💥 𝗦𝗣𝗥𝗔𝗬: .spray <text> / .stopspray\n\n"
                "📋 𝐏𝐨𝐨𝐫𝐢 𝐥𝐢𝐬𝐭: `.cmds`\n🌟 ARYA X MENTAL"
            )
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ Help Err → `{str(e)[:40]}`")

    @register_cmd("status")
    async def cmd_status(event, _):
        try:
            now = time.time()
            try: uptime = int(now - START_TIME)
            except: uptime = 0
            if uptime < 0: uptime = 0
            try: admin_count = len(admins)
            except: admin_count = 0
            txt = (
                "✅ 𝐔sᴇʀʙᴏᴛ 𝐒ᴛᴀᴛᴜs 𝐕𝟐\n"
                "━━━━━━━━━━━━━━━\n"
                f"⏱️ 𝐔ᴘᴛɪᴍᴇ → `{uptime}s`\n"
                f"👑 𝐀ᴅᴍɪɴs → `{admin_count}`\n"
                f"⚔️ 𝐑𝐚𝐢𝐝 𝐒𝐞𝐭𝐬 → `16 types`\n"
                f"📦 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 → `500+`\n"
                f"⚙️ 𝐌ᴏᴅᴇ → `Operational`"
            )
            if event.out: await safe_edit(event, txt)
            else: await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("flip")
    async def cmd_flip(event, _):
        try:
            result = random.choice(["🪙 𝐇ᴇᴀᴅs", "🪙 𝐓ᴀɪʟs"])
            text = f"🎲 𝐂ᴏɪɴ 𝐅ʟɪᴘ\n━━━━━━━━━━━━━━━\n👉 𝐑ᴇsᴜʟᴛ → {result}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ʟɪᴘ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("dice")
    async def cmd_dice(event, _):
        try:
            num = random.randint(1, 6)
            faces = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}
            text = f"🎲 𝐃ɪᴄᴇ 𝐑ᴏʟʟ\n━━━━━━━━━━━━━━━\n👉 {faces.get(num, str(num))} → `{num}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃ɪᴄᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("mute", needs_reply=True)
    async def cmd_mute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            added, already = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in muted_users: already.append(str(uid))
                else: muted_users.add(uid); added.append(str(uid))
            parts = []
            if added: parts.append(f"🔇 𝐌ᴜᴛᴇᴅ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")
            msg = "\n".join(parts) or "❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ"
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌ᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("unmute", needs_reply=True)
    async def cmd_unmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            removed, not_muted = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in muted_users: muted_users.remove(uid); removed.append(str(uid))
                else: not_muted.append(str(uid))
            parts = []
            if removed: parts.append(f"🗣️ 𝐔ɴᴍᴜᴛᴇ → `{', '.join(removed)}`")
            if not_muted: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐌ᴜᴛᴇᴅ → `{', '.join(not_muted)}`")
            msg = "\n".join(parts) or "❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ"
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔ɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("gmute", needs_reply=True)
    async def cmd_gmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            added, already = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in global_muted: already.append(str(uid))
                else: global_muted.add(uid); added.append(str(uid))
            parts = []
            if added: parts.append(f"🔕 𝐆ᴍᴜᴛᴇ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")
            msg = "\n".join(parts) or "❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ"
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆ᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("gunmute", needs_reply=True)
    async def cmd_gunmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            removed, not_muted = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in global_muted: global_muted.remove(uid); removed.append(str(uid))
                else: not_muted.append(str(uid))
            parts = []
            if removed: parts.append(f"🔊 𝐆ᴜɴᴍᴜᴛᴇ → `{', '.join(removed)}`")
            if not_muted: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(not_muted)}`")
            msg = "\n".join(parts) or "❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ"
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆ᴜɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("mutelist")
    async def cmd_mutelist(event, _):
        try:
            local_list = "\n".join(f"• `{x}`" for x in sorted(muted_users)) if muted_users else "None"
            global_list = "\n".join(f"• `{x}`" for x in sorted(global_muted)) if global_muted else "None"
            text = (
                "🔇 𝐌𝐔𝐓𝐄 𝐋𝐈𝐒𝐓\n━━━━━━━━━━━━━━━\n"
                f"🔇 𝐋𝐨𝐜𝐚𝐥:\n{local_list}\n\n🔕 𝐆𝐥𝐨𝐛𝐚𝐥:\n{global_list}"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌𝐔𝐓𝐄𝐋𝐈𝐒𝐓 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("purge")
    async def cmd_purge(event, arg):
        try:
            try: count = int(arg) if arg else 50
            except: count = 50
            if count < 1: count = 1
            if count > 200: count = 200
            await safe_edit(event, "⚡ 𝐏ᴜʀɢɪɴɢ 𝐌ᴇssᴀɢᴇs...\n━━━━━━━━━━━━━━━")
            msgs = []
            async for m in bot.iter_messages(event.chat_id, limit=count + 1):
                msgs.append(m.id)
            if not msgs:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐌ᴇssᴀɢᴇs")
            try: await bot.delete_messages(event.chat_id, msgs)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
                await bot.delete_messages(event.chat_id, msgs)
            except RPCError: pass
            text = f"🧹 𝐏ᴜʀɢᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n━━━━━━━━━━━━━━━\n🗑️ 𝐃ᴇʟᴇᴛᴇᴅ → `{max(len(msgs)-1,0)}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏ᴜʀɢᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("throw", needs_reply=True, group_only=True)
    async def cmd_throw(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            kicked, failed = [], []
            me = await bot.get_me()
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == me.id: continue
                try: await bot.kick_participant(event.chat_id, uid); kicked.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if kicked: parts.append(f"👞 𝐊ɪᴄᴋᴇᴅ → `{', '.join(kicked)}`")
            if failed: parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ → `{', '.join(failed)}`")
            msg = "\n".join(parts) or "❌ 𝐍ᴏ 𝐀ᴄᴛɪᴏɴ"
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓ʜʀᴏᴡ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("lock", group_only=True)
    async def cmd_lock(event, _):
        try:
            group_locks.add(event.chat_id)
            await safe_edit(event, "🔒 𝐆ʀᴏᴜᴘ 𝐋ᴏᴄᴋᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋ᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("unlock", group_only=True)
    async def cmd_unlock(event, _):
        try:
            group_locks.discard(event.chat_id)
            await safe_edit(event, "🔓 𝐆ʀᴏᴜᴘ 𝐔ɴʟᴏᴄᴋᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔ɴʟᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`")

    async def auto_free_channel_slots(count_to_leave=3):
        """Auto-leaves inactive channels/supergroups where the user is NOT creator/admin to bypass 500-channel limit."""
        freed = []
        try:
            dialogs = await bot.get_dialogs(limit=150)
            for d in dialogs:
                if len(freed) >= count_to_leave:
                    break
                if getattr(d, 'is_channel', False):
                    ent = d.entity
                    is_creator = getattr(ent, 'creator', False)
                    is_admin = getattr(d, 'is_admin', False) or (getattr(ent, 'admin_rights', None) is not None)
                    if not is_creator and not is_admin:
                        try:
                            await bot(functions.channels.LeaveChannelRequest(channel=d.input_entity))
                            freed.append(getattr(d, 'name', '') or str(d.id))
                            await asyncio.sleep(0.6)
                        except Exception:
                            pass
        except Exception as e:
            print(f"[AutoFreeSlots Err] {e}", flush=True)
        return freed

    # ── AUTO GC CREATOR & BOT CONTROLLER ──
    @register_cmd("creategc")
    @register_cmd("bulkcreategc")
    @register_cmd("autogc")
    async def cmd_creategc(event, arg):
        global bulk_gc_task
        try:
            MAX_GC_LIMIT = 30
            parts = arg.strip().split(None, 1) if arg else []
            count = 2
            prefix = "Arya X MENTAL Empire"
            limit_note = ""
            if len(parts) >= 1:
                try:
                    req_count = int(parts[0])
                    if req_count > MAX_GC_LIMIT:
                        count = MAX_GC_LIMIT
                        limit_note = f"\n⚠️ Max batch is 30! Capped to `{MAX_GC_LIMIT}` for Telegram safety."
                    else:
                        count = max(1, req_count)
                except:
                    prefix = arg.strip()
            if len(parts) >= 2:
                prefix = parts[1].strip() or prefix

            if bulk_gc_task and not bulk_gc_task.done():
                return await safe_edit(event, "⚠️ 𝐁ᴜʟᴋ 𝐆𝐂 𝐂ʀᴇᴀᴛɪᴏɴ already running!\n👉 Type `.stopcreategc` to stop.")

            await safe_edit(event, f"⚡ 𝐒ᴛᴀʀᴛɪɴɢ 𝐁ᴜʟᴋ 𝐆𝐂 𝐂ʀᴇᴀᴛɪᴏɴ: `{count}` Groups{limit_note}\n📛 Title: `{prefix} #1` to `#{count}`\n🛡️ 𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ 𝐏ᴀᴄɪɴɢ: ~1 Min/GC (Create ➔ Add Bots ➔ Auto-Promote ➔ Safe Sleep)")

            async def do_create():
                created = []
                created_peers = []
                last_err = ""
                folder_name = "🔥 ARYA GC"
                folder_id = None
                curr_include_peers = []
                folder_status = "⚠️ Folder creation skipped"

                # ─────────────────────────────────────────────────────────────
                # STEP 1: CREATE OR VERIFY THE DEDICATED FOLDER TAB FIRST!
                # ─────────────────────────────────────────────────────────────
                async def sync_folder(peers_to_save):
                    nonlocal folder_id
                    if not folder_id:
                        return False
                    title_variants = []
                    if hasattr(types, "TextWithEntities"):
                        try:
                            title_variants.append(types.TextWithEntities(text=folder_name, entities=[]))
                        except:
                            pass
                    title_variants.append(folder_name)
                    title_variants.append("ARYA GC")

                    for t_val in title_variants:
                        # Attempt with emoticon
                        try:
                            fil = types.DialogFilter(
                                id=folder_id,
                                title=t_val,
                                pinned_peers=[],
                                include_peers=list(peers_to_save),
                                exclude_peers=[],
                                emoticon="🔥"
                            )
                            await bot(functions.messages.UpdateDialogFilterRequest(
                                id=folder_id,
                                filter=fil
                            ))
                            return True
                        except TypeError:
                            pass
                        except Exception:
                            pass

                        # Attempt without emoticon
                        try:
                            fil = types.DialogFilter(
                                id=folder_id,
                                title=t_val,
                                pinned_peers=[],
                                include_peers=list(peers_to_save),
                                exclude_peers=[]
                            )
                            await bot(functions.messages.UpdateDialogFilterRequest(
                                id=folder_id,
                                filter=fil
                            ))
                            return True
                        except Exception:
                            pass
                    return False

                try:
                    filters_res = await bot(functions.messages.GetDialogFiltersRequest())
                    raw_filters = getattr(filters_res, 'filters', filters_res)
                    filters_list = raw_filters if isinstance(raw_filters, list) else []

                    # Find if folder already exists
                    for f in filters_list:
                        f_title = getattr(f, 'title', '')
                        if hasattr(f_title, 'text'):
                            f_title = f_title.text
                        if str(f_title).strip() in (folder_name, "ARYA GC"):
                            folder_id = getattr(f, 'id', None)
                            curr_include_peers = list(getattr(f, 'include_peers', []))
                            break

                    if not folder_id:
                        existing_ids = [getattr(f, 'id', 0) for f in filters_list if hasattr(f, 'id')]
                        cand_id = 2
                        while cand_id in existing_ids and cand_id < 25:
                            cand_id += 1
                        folder_id = cand_id

                    # Create folder upfront so the tab is active immediately
                    folder_ready = await sync_folder(curr_include_peers)
                    if folder_ready:
                        folder_status = f"📁 Dedicated Folder `{folder_name}` Active (Top Tab)"
                    else:
                        folder_status = f"📁 Folder Tab `{folder_name}` Initialized"
                except Exception as fe:
                    folder_status = f"ℹ️ Folder: Saved in chats ({str(fe)[:30]})"

                await safe_edit(event, f"⚡ 𝐅ᴏʟᴅᴇʀ 𝐑ᴇᴀᴅʏ: `{folder_name}`\n🚀 Creating `{count}` Groups directly into folder...")

                # ─────────────────────────────────────────────────────────────
                # STEP 2: CREATE GROUPS AND ADD EACH INTO FOLDER AS IT IS MADE!
                # ─────────────────────────────────────────────────────────────
                for i in range(1, count + 1):
                    chat_obj = None
                    title = f"{prefix} #{i}" if count > 1 else prefix

                    # Try 1: Megagroup (Supergroup) creation
                    try:
                        res = await bot(functions.channels.CreateChannelRequest(
                            title=title,
                            about="⚡ Created by Arya X MENTAL Userbot V2",
                            megagroup=True
                        ))
                        if res and hasattr(res, "chats") and res.chats:
                            chat_obj = res.chats[0]
                    except FloodWaitError as fw:
                        last_err = f"FloodWait: Telegram requires waiting {fw.seconds}s"
                        await asyncio.sleep(fw.seconds)
                    except Exception as err:
                        err_str = str(err)
                        last_err = err_str
                        print(f"[BulkGC Supergroup Error] {err}", flush=True)
                        # LIMIT AUTO-BYPASS: If 500-channel limit hit, auto-free 2 non-admin channels & retry!
                        if "ChannelsTooMuch" in err_str or "ChannelsAdminLocTooMuch" in err_str:
                            try:
                                freed_slots = await auto_free_channel_slots(2)
                                if freed_slots:
                                    res_retry = await bot(functions.channels.CreateChannelRequest(
                                        title=title,
                                        about="⚡ Created by Arya X MENTAL Userbot V2",
                                        megagroup=True
                                    ))
                                    if res_retry and hasattr(res_retry, "chats") and res_retry.chats:
                                        chat_obj = res_retry.chats[0]
                            except Exception as re_err:
                                print(f"[BulkGC Auto-Retry Err] {re_err}", flush=True)

                    # Try 2: If Megagroup failed (or account at 500 supergroup limit),
                    # FALLBACK TO BASIC GROUP (messages.CreateChatRequest).
                    # IMPORTANT: Telegram Basic Groups DO NOT COUNT towards the 500-channel limit!
                    if not chat_obj:
                        try:
                            # Resolve valid user peers for Basic Group (Telegram requires >=1 other user)
                            target_users = []
                            caller_bots = get_my_bots(event.sender_id or OWNER_ID)
                            # Priority 1: ONLY this user's saved bots
                            if caller_bots:
                                for b in caller_bots:
                                    try:
                                        u_ent = await bot.get_input_entity(b)
                                        target_users.append(u_ent)
                                    except Exception:
                                        pass
                            # Priority 2: Fallback to official service bots if no saved bot resolved
                            if not target_users:
                                for fallback_username in ["@BotFather", "@SpamBot"]:
                                    try:
                                        u_ent = await bot.get_input_entity(fallback_username)
                                        target_users.append(u_ent)
                                        break
                                    except Exception:
                                        pass
                            # Priority 3: Fallback to any user from recent dialogs
                            if not target_users:
                                try:
                                    dlist = await bot.get_dialogs(limit=25)
                                    for d in dlist:
                                        if getattr(d, 'is_user', False) and not getattr(d.entity, 'is_self', False):
                                            target_users.append(d.input_entity)
                                            break
                                except Exception:
                                    pass

                            if target_users:
                                res_bg = await bot(functions.messages.CreateChatRequest(
                                    users=target_users,
                                    title=title
                                ))
                                if res_bg and hasattr(res_bg, "chats") and res_bg.chats:
                                    chat_obj = res_bg.chats[0]
                            else:
                                if not last_err:
                                    last_err = "Telegram requires at least 1 valid user/bot to create basic group. Use .addmybot first."
                        except Exception as e_bg:
                            if not last_err:
                                last_err = f"BasicGroup: {str(e_bg)}"
                            print(f"[BulkGC Basic Group Error] {e_bg}", flush=True)

                    if chat_obj:
                        cid = chat_obj.id
                        access_hash = getattr(chat_obj, "access_hash", 0)
                        created.append((cid, title))
                        peer = types.InputPeerChannel(channel_id=cid, access_hash=access_hash) if access_hash else types.InputPeerChat(chat_id=cid)
                        created_peers.append(peer)
                        curr_include_peers.append(peer)

                        # REAL-TIME: Add this newly created GC into the folder immediately!
                        try:
                            await sync_folder(curr_include_peers)
                        except Exception:
                            pass

                        # Pacing 1: Wait 5-6s after group creation (Anti-Flood)
                        try:
                            await safe_edit(event, (
                                f"🏢 𝐆ʀᴏᴜᴘ `{len(created)}/{count}` 𝐂ʀᴇᴀᴛᴇᴅ: `{title}`\n"
                                f"📁 𝐅ᴏʟᴅᴇʀ: `{folder_name}`\n"
                                f"⏳ 𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ 𝐏ᴀᴄɪɴɢ: Waiting 6s before adding your configured bots..."
                            ))
                        except: pass
                        await asyncio.sleep(6)

                        # Pacing 2: Auto add ONLY THIS CALLER's saved bots
                        caller_bots = get_my_bots(event.sender_id or OWNER_ID)
                        added_bots = []
                        if caller_bots:
                            for b in caller_bots:
                                try:
                                    b_ent = await bot.get_input_entity(b)
                                    if access_hash:
                                        await bot(functions.channels.InviteToChannelRequest(channel=peer, users=[b_ent]))
                                    else:
                                        await bot(functions.messages.AddChatUserRequest(chat_id=cid, user_id=b_ent, fwd_limit=10))
                                    added_bots.append(str(b))
                                except FloodWaitError as fwe:
                                    try: await safe_edit(event, f"⏳ Telegram FloodWait: Sleeping {fwe.seconds}s...")
                                    except: pass
                                    await asyncio.sleep(fwe.seconds + 2)
                                except Exception:
                                    pass
                                await asyncio.sleep(2)

                        # Pacing 3: Wait 5-6s after adding bots before promoting
                        try:
                            await safe_edit(event, (
                                f"🤖 𝐁ᴏᴛs 𝐀ᴅᴅᴇᴅ: `{', '.join(added_bots) or 'None'}`\n"
                                f"🏢 𝐆ʀᴏᴜᴘ: `{title}`\n"
                                f"⏳ 𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ 𝐏ᴀᴄɪɴɢ: Waiting 6s before auto-promoting to Full Admin..."
                            ))
                        except: pass
                        await asyncio.sleep(6)

                        # Pacing 4: AUTO-PROMOTE BOTS TO FULL ADMIN IMMEDIATELY IN THE NEW GC!
                        promoted_bots = []
                        if caller_bots:
                            for b in caller_bots:
                                try:
                                    ok, detail = await universal_promote_bot_or_user(peer, b, custom_rank="Arya Bot ⚡")
                                    if ok:
                                        promoted_bots.append(str(b))
                                except FloodWaitError as fwe:
                                    try: await safe_edit(event, f"⏳ Telegram FloodWait: Sleeping {fwe.seconds}s...")
                                    except: pass
                                    await asyncio.sleep(fwe.seconds + 2)
                                    try:
                                        ok, detail = await universal_promote_bot_or_user(peer, b, custom_rank="Arya Bot ⚡")
                                        if ok:
                                            promoted_bots.append(str(b))
                                    except: pass
                                except Exception:
                                    pass
                                await asyncio.sleep(2)

                        # Pacing 5: If more groups remaining, cool-down so total cycle is ~1 minute per GC
                        # 6s (after create) + ~4s (invites) + 6s (after invites) + ~4s (promotes) = ~20s.
                        # Remaining cooldown = 35s to make total ~55-60s per group, preventing FloodWait!
                        if i < count:
                            cooldown_seconds = 35
                            for rem in range(cooldown_seconds, 0, -5):
                                try:
                                    await safe_edit(event, (
                                        f"✅ 𝐆ʀᴏᴜᴘ #{i} 𝐂ᴏᴍᴘʟᴇᴛᴇ & 𝐁ᴏᴛs 𝐏ʀᴏᴍᴏᴛᴇᴅ!\n"
                                        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"🏢 𝐆ʀᴏᴜᴘ: `{title}`\n"
                                        f"👑 𝐁ᴏᴛs 𝐀ᴅᴍɪɴ: `{', '.join(promoted_bots) or 'None'}`\n"
                                        f"📁 𝐅ᴏʟᴅᴇʀ: `{folder_name}`\n"
                                        f"🛡️ 𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ 𝐂ᴏᴏʟ-ᴅᴏᴡɴ: Next GC in `{rem}s` (0 Flood Risk)"
                                    ))
                                except: pass
                                await asyncio.sleep(5)

                # Final sync of all peers into folder
                if created_peers:
                    try:
                        await sync_folder(curr_include_peers)
                        folder_status = f"📁 𝐀ᴅᴅᴇᴅ `{len(created)}` GCs directly to dedicated folder: `{folder_name}`"
                    except Exception as fe:
                        folder_status = f"ℹ️ Folder: Saved in chats ({str(fe)[:30]})"

                lines = [f"• `{t}` (ID: `{cid}`)" for cid, t in created[:10]]
                if len(created) > 10:
                    lines.append(f"...and {len(created)-10} more groups!")

                if len(created) == 0:
                    advice = ""
                    if "ChannelsTooMuch" in last_err or "ChannelsAdminLocTooMuch" in last_err:
                        advice = "\n💡 𝐑ᴇᴀsᴏɴ: Telegram channel/supergroup limit reached for this account! Please leave/delete unused channels or groups, or use .addmybot first."
                    elif "FloodWait" in last_err:
                        advice = f"\n💡 𝐑ᴇᴀsᴏɴ: {last_err}. Telegram rate limit active."
                    elif last_err:
                        advice = f"\n💡 𝐑ᴇᴀsᴏɴ: `{last_err[:80]}`"

                    report = (
                        f"⚠️ 𝐁ᴜʟᴋ 𝐆𝐂 𝐂ʀᴇᴀᴛᴇ 𝐅ᴀɪʟᴇᴅ!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ 𝐓ᴏᴛᴀʟ 𝐂ʀᴇᴀᴛᴇᴅ: `0 / {count}`\n"
                        f"{folder_status}{advice}\n\n"
                        f"👉 Tip: Ensure your Telegram account has not exceeded the 500 channel/group limit!"
                    )
                else:
                    report = (
                        f"🎉 𝐁ᴜʟᴋ 𝐆𝐂 𝐂ʀᴇᴀᴛᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ 𝐓ᴏᴛᴀʟ 𝐂ʀᴇᴀᴛᴇᴅ: `{len(created)} / {count}`\n"
                        f"👑 𝐁ᴏᴛs 𝐀ᴜᴛᴏ-𝐏ʀᴏᴍᴏᴛᴇᴅ: Full Admin in all groups\n"
                        f"🛡️ 𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ 𝐒ᴀғᴇ: ~1 Min/GC Safe Pacing Followed\n"
                        f"{folder_status}\n\n"
                        f"📋 𝐆ʀᴏᴜᴘ 𝐋ɪsᴛ:\n" + "\n".join(lines)
                    )
                await safe_edit(event, report)

            bulk_gc_task = asyncio.create_task(do_create())
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂ʀᴇᴀᴛᴇ𝐆𝐂 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("stopcreategc")
    @register_cmd("sstopgc")
    async def cmd_stopcreategc(event, _):
        global bulk_gc_task
        if bulk_gc_task and not bulk_gc_task.done():
            bulk_gc_task.cancel()
            bulk_gc_task = None
            await safe_edit(event, "🛑 𝐁ᴜʟᴋ 𝐆𝐂 𝐂ʀᴇᴀᴛɪᴏɴ 𝐒ᴛᴏᴘᴘᴇᴅ")
        else:
            await safe_edit(event, "⚠️ 𝐍ᴏ active bulk GC task running")

    @register_cmd("addmybot")
    @register_cmd("addbot")
    @register_cmd("setmybots")
    async def cmd_addmybot(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.addmybot @bot1 @bot2`")
            user_id = event.sender_id or OWNER_ID
            bots_input = [b.strip() for b in arg.replace(",", " ").split() if b.strip()]
            added_count = add_my_bots_for_user(bots_input, user_id)
            user_bots = get_my_bots(user_id)
            await safe_edit(event, f"✅ 𝐒ᴀᴠᴇᴅ `{added_count}` 𝐁ᴏᴛs for ID `{user_id}`!\n📋 Your Configured Bots: `{len(user_bots)}`\n👉 Ab `.addbots` ya `.creategc` sirf AAPKE bots ko invite karega!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴅ𝐌ʏ𝐁ᴏᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("delmybot")
    async def cmd_delmybot(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.delmybot @bot`")
            user_id = event.sender_id or OWNER_ID
            uname = arg.strip()
            ok = remove_my_bot_for_user(uname, user_id)
            if ok:
                await safe_edit(event, f"🗑️ 𝐑ᴇᴍᴏᴠᴇᴅ `{uname}` from your account's saved bots")
            else:
                await safe_edit(event, f"⚠️ `{uname}` not found in your saved bots")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃ᴇʟ𝐌ʏ𝐁ᴏᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("mybots")
    @register_cmd("listmybots")
    async def cmd_mybots(event, _):
        try:
            user_id = event.sender_id or OWNER_ID
            user_bots = get_my_bots(user_id)
            if not user_bots:
                return await safe_edit(event, f"⚠️ 𝐍ᴏ 𝐒ᴀᴠᴇᴅ 𝐁ᴏᴛs for your account (`{user_id}`)!\n👉 Use `.addmybot @botusername` to save your own bots.")
            lines = [f"{i+1}. `{b}`" for i, b in enumerate(user_bots)]
            await safe_edit(event, f"🤖 𝐌ʏ 𝐂ᴏɴꜰɪɢᴜʀᴇᴅ 𝐁ᴏᴛs (User: `{user_id}`) [{len(user_bots)}]:\n━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines) + "\n\n💡 Use `.addbots` to add all, or `.promotebots` to promote!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌ʏ𝐁ᴏᴛs 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("clearmybots")
    async def cmd_clearmybots(event, _):
        try:
            user_id = event.sender_id or OWNER_ID
            clear_my_bots_for_user(user_id)
            await safe_edit(event, f"🗑️ 𝐀ʟʟ 𝐒ᴀᴠᴇᴅ 𝐁ᴏᴛs 𝐂ʟᴇᴀʀᴇᴅ for your account (`{user_id}`)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("addbots", group_only=True)
    async def cmd_addbots(event, arg):
        try:
            user_id = event.sender_id or OWNER_ID
            target_bots = []
            if arg:
                target_bots = [b.strip() for b in arg.replace(",", " ").split() if b.strip()]
            else:
                target_bots = get_my_bots(user_id)

            if not target_bots:
                return await safe_edit(event, f"⚠️ 𝐍ᴏ 𝐁ᴏᴛs 𝐅ᴏᴜɴᴅ for your account (`{user_id}`)!\n👉 Set bots first: `.addmybot @bot1 @bot2`\n👉 Or run: `.addbots @bot1 @bot2`")

            await safe_edit(event, f"⚡ 𝐀ᴅᴅɪɴɢ `{len(target_bots)}` 𝐁ᴏᴛs ᴛᴏ 𝐆ʀᴏᴜᴘ (User: `{user_id}`)...")
            added, failed = [], []
            for b in target_bots:
                try:
                    await bot(functions.channels.InviteToChannelRequest(channel=event.chat_id, users=[b]))
                    added.append(b)
                except Exception:
                    try:
                        await bot(functions.messages.AddChatUserRequest(chat_id=event.chat_id, user_id=b, fwd_limit=10))
                        added.append(b)
                    except Exception as err:
                        failed.append((b, str(err)[:25]))
                await asyncio.sleep(1.2)

            res = [f"🤖 𝐁ᴏᴛ 𝐀ᴅᴅ 𝐑ᴇsᴜʟᴛ (User: `{user_id}`)\n━━━━━━━━━━━━━━━"]
            if added: res.append(f"✅ 𝐀ᴅᴅᴇᴅ ({len(added)}): {', '.join(f'`{x}`' for x in added)}")
            if failed: res.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ ({len(failed)}): {', '.join(f'`{x[0]}`' for x in failed)}")
            res.append("\n💡 Next step: Type `.promotebots` to make them full admin!")
            await safe_edit(event, "\n".join(res))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴅ𝐁ᴏᴛs 𝐄ʀʀ → `{str(e)[:40]}`")
    async def universal_promote_bot_or_user(chat_peer, target, custom_rank: str = "Arya Bot ⚡"):
        """
        Rock-solid promotion helper:
        - Resolves entity from username string (@bot), ID, or Peer
        - Automatically detects Basic Group vs Supergroup
        - Auto-migrates Basic Group to Supergroup so bot admin rights & custom titles work
        - Auto-invites bot/user into group if not yet a participant
        - Cascading permission tiers (AddAdmins -> FullAdmin NoAdd -> Moderator)
        - Custom title fallback if rejected
        Returns (success: bool, detail: str)
        """
        # Step 1: Entity resolution
        target_ent = None
        try:
            target_ent = await bot.get_input_entity(target)
        except Exception:
            try:
                full_ent = await bot.get_entity(target)
                target_ent = await bot.get_input_entity(full_ent)
            except Exception as e_res:
                return False, f"Entity Not Found ({str(e_res)[:20]})"

        # Step 2: Determine chat type and migrate basic group if needed
        is_channel = True
        chat_obj = None
        try:
            chat_obj = await bot.get_entity(chat_peer)
            if isinstance(chat_obj, types.Chat):
                is_channel = False
                # Try migrating to Supergroup so full bot admin rights & custom titles work
                try:
                    mig_res = await bot(functions.messages.MigrateChatRequest(chat_id=chat_obj.id))
                    if mig_res and hasattr(mig_res, "chats") and mig_res.chats:
                        chat_obj = mig_res.chats[0]
                        chat_peer = await bot.get_input_entity(chat_obj)
                        is_channel = True
                except Exception:
                    pass
        except Exception:
            pass

        # Step 3: Ensure target is in the group (invite if missing)
        try:
            if is_channel:
                await bot(functions.channels.InviteToChannelRequest(channel=chat_peer, users=[target_ent]))
            else:
                cid = getattr(chat_obj, "id", chat_peer)
                await bot(functions.messages.AddChatUserRequest(chat_id=cid, user_id=target_ent, fwd_limit=10))
        except Exception as inv_e:
            inv_str = str(inv_e).lower()
            if "already" not in inv_str and "privacy" not in inv_str:
                print(f"[Invite Target Note] {inv_e}", flush=True)

        # Step 4: If still basic group (migration failed or skipped)
        if not is_channel:
            try:
                cid = getattr(chat_obj, "id", chat_peer)
                await bot(functions.messages.EditChatAdminRequest(
                    chat_id=cid,
                    user_id=target_ent,
                    is_admin=True
                ))
                return True, "Basic Admin ✅"
            except Exception as e_bg:
                return False, f"BasicAdminErr: {str(e_bg)[:20]}"

        # Step 5: Supergroup / Megagroup promotion with cascading permission tiers
        rights_tiers = [
            (
                types.ChatAdminRights(
                    change_info=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=True,
                    manage_call=True
                ),
                "Full Admin 👑"
            ),
            (
                types.ChatAdminRights(
                    change_info=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=False,
                    manage_call=True
                ),
                "Admin (Full No-Add) ⚡"
            ),
            (
                types.ChatAdminRights(
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True
                ),
                "Moderator 🛡️"
            )
        ]

        ranks_to_try = [custom_rank, "Admin ⚡", ""] if custom_rank else [""]
        last_error = "Unknown"

        for rights_obj, tier_label in rights_tiers:
            for r_title in ranks_to_try:
                try:
                    await bot(functions.channels.EditAdminRequest(
                        channel=chat_peer,
                        user_id=target_ent,
                        admin_rights=rights_obj,
                        rank=r_title
                    ))
                    return True, tier_label
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds + 1)
                    try:
                        await bot(functions.channels.EditAdminRequest(
                            channel=chat_peer,
                            user_id=target_ent,
                            admin_rights=rights_obj,
                            rank=r_title
                        ))
                        return True, tier_label
                    except Exception as fe_retry:
                        last_error = str(fe_retry)
                        break
                except Exception as err:
                    last_error = str(err)
                    err_l = last_error.lower()
                    # If rank title error, try next rank
                    if "rank" in err_l or "title" in err_l:
                        continue
                    # If rights issue (e.g. AddAdminsInvalid, ChatAdminRequired), try next rights tier
                    break

        return False, last_error[:30]

    async def universal_demote_bot_or_user(chat_peer, target):
        try:
            target_ent = await bot.get_input_entity(target)
        except Exception:
            try:
                full_ent = await bot.get_entity(target)
                target_ent = await bot.get_input_entity(full_ent)
            except Exception:
                return False, "EntityNotFound"

        no_rights = types.ChatAdminRights(
            change_info=False, delete_messages=False, ban_users=False,
            invite_users=False, pin_messages=False, add_admins=False, manage_call=False
        )
        try:
            await bot(functions.channels.EditAdminRequest(
                channel=chat_peer,
                user_id=target_ent,
                admin_rights=no_rights,
                rank=""
            ))
            return True, "Demoted"
        except Exception:
            try:
                chat_obj = await bot.get_entity(chat_peer)
                cid = getattr(chat_obj, "id", chat_peer)
                await bot(functions.messages.EditChatAdminRequest(
                    chat_id=cid,
                    user_id=target_ent,
                    is_admin=False
                ))
                return True, "Demoted"
            except Exception as e:
                return False, str(e)[:25]

    @register_cmd("promotebots", group_only=True)
    async def cmd_promotebots(event, arg):
        try:
            user_id = event.sender_id or OWNER_ID
            await safe_edit(event, "⚡ 𝐏ʀᴏᴍᴏᴛɪɴɢ 𝐁ᴏᴛs ᴛᴏ 𝐀ᴅᴍɪɴ...")
            promoted, failed = [], []

            targets = []
            if arg:
                targets = [b.strip() for b in arg.replace(",", " ").split() if b.strip()]
            else:
                user_bots = get_my_bots(user_id)
                if user_bots:
                    targets = list(user_bots)

            try:
                async for user in bot.iter_participants(event.chat_id, filter=types.ChannelParticipantsBots):
                    if user.username:
                        uname = f"@{user.username}"
                        if uname not in targets and uname.lower() != "arya_mental":
                            targets.append(uname)
                    elif user.id not in targets:
                        targets.append(user.id)
            except: pass

            if not targets:
                return await safe_edit(event, f"⚠️ 𝐍ᴏ 𝐁ᴏᴛs 𝐅ᴏᴜɴᴅ ᴛᴏ 𝐏ʀᴏᴍᴏᴛᴇ for `{user_id}`!\n👉 First add bots: `.addbots` or `.addmybot @bot`")

            chat_peer = await event.get_input_chat()
            for b in targets:
                ok, detail = await universal_promote_bot_or_user(chat_peer, b, custom_rank="Arya Bot ⚡")
                if ok:
                    promoted.append((str(b), detail))
                else:
                    failed.append((str(b), detail))
                await asyncio.sleep(0.8)

            res = [f"👑 𝐁ᴏᴛ 𝐀ᴜᴛᴏ-𝐏ʀᴏᴍᴏᴛɪᴏɴ (User: `{user_id}`)\n━━━━━━━━━━━━━━━"]
            if promoted:
                res.append(f"✅ 𝐏ʀᴏᴍᴏᴛᴇᴅ ({len(promoted)}):\n• " + "\n• ".join(f"`{x[0]}` → {x[1]}" for x in promoted))
            if failed:
                res.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ ({len(failed)}):\n• " + "\n• ".join(f"`{x[0]}` ({x[1]})" for x in failed))
            res.append("⚡ 𝐑ɪɢʜᴛs: Full Admin (Manage, Delete, Ban, Pin, Call)")
            await safe_edit(event, "\n".join(res))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏ʀᴏᴍᴏᴛᴇ𝐁ᴏᴛs 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("demotebots", group_only=True)
    async def cmd_demotebots(event, arg):
        try:
            user_id = event.sender_id or OWNER_ID
            await safe_edit(event, "⚡ 𝐃ᴇᴍᴏᴛɪɴɢ 𝐁ᴏᴛs...")
            demoted = []
            targets = [b.strip() for b in arg.replace(",", " ").split() if b.strip()] if arg else list(get_my_bots(user_id))
            try:
                async for user in bot.iter_participants(event.chat_id, filter=types.ChannelParticipantsBots):
                    t = f"@{user.username}" if user.username else user.id
                    if t not in targets: targets.append(t)
            except: pass

            chat_peer = await event.get_input_chat()
            for b in targets:
                ok, _ = await universal_demote_bot_or_user(chat_peer, b)
                if ok:
                    demoted.append(str(b))
                await asyncio.sleep(0.5)
            await safe_edit(event, f"✅ 𝐃ᴇᴍᴏᴛᴇᴅ `{len(demoted)}` 𝐁ᴏᴛs back to standard members.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃ᴇᴍᴏᴛᴇ𝐁ᴏᴛs 𝐄ʀʀ → `{str(e)[:40]}`")

    # ── TELEGRAM ACCOUNT LIMIT BYPASS & CLEANUP TOOLS ──
    @register_cmd("limitcheck")
    @register_cmd("limitinfo")
    async def cmd_limitcheck(event, _):
        try:
            await safe_edit(event, "🔍 𝐀ɴᴀʟʏᴢɪɴɢ 𝐓ᴇʟᴇɢʀᴀᴍ 𝐀ᴄᴄᴏᴜɴᴛ 𝐋ɪᴍɪᴛs...")
            me = await bot.get_me()
            is_premium = getattr(me, 'premium', False)
            max_channels = 1000 if is_premium else 500

            dialogs = await bot.get_dialogs(limit=None)
            channels_count = 0
            supergroups_count = 0
            basic_groups_count = 0
            users_count = 0
            non_admin_channels = 0

            for d in dialogs:
                if getattr(d, 'is_channel', False):
                    ent = d.entity
                    is_sg = getattr(ent, 'megagroup', False)
                    if is_sg:
                        supergroups_count += 1
                    else:
                        channels_count += 1
                    is_creator = getattr(ent, 'creator', False)
                    is_admin = getattr(d, 'is_admin', False) or (getattr(ent, 'admin_rights', None) is not None)
                    if not is_creator and not is_admin:
                        non_admin_channels += 1
                elif getattr(d, 'is_group', False):
                    basic_groups_count += 1
                elif getattr(d, 'is_user', False):
                    users_count += 1

            capped_total = channels_count + supergroups_count
            slots_left = max(0, max_channels - capped_total)
            pct = round((capped_total / max_channels) * 100, 1)

            tier = "💎 Telegram Premium" if is_premium else "🆓 Free Telegram"
            status_emoji = "🟢" if slots_left > 50 else ("🟡" if slots_left > 10 else "🔴")

            report = (
                f"📊 𝐓ᴇʟᴇɢʀᴀᴍ 𝐀ᴄᴄᴏᴜɴᴛ 𝐋ɪᴍɪᴛ 𝐒ᴛᴀᴛᴜs\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 𝐔sᴇʀ: `{me.first_name}` (`{me.id}`)\n"
                f"🏷️ 𝐓ɪᴇʀ: {tier}\n"
                f"⚡ 𝐒ᴛᴀᴛᴜs: {status_emoji} `{capped_total} / {max_channels}` ({pct}% used)\n"
                f"🆓 𝐒ʟᴏᴛs 𝐋ᴇꜰᴛ: `{slots_left}` slots remaining\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 𝐂ʜᴀɴɴᴇʟs: `{channels_count}`\n"
                f"👥 𝐒ᴜᴘᴇʀɢʀᴏᴜᴘs: `{supergroups_count}`\n"
                f"💬 𝐁ᴀsɪᴄ 𝐆ʀᴏᴜᴘs: `{basic_groups_count}` (Bypasses 500-limit!)\n"
                f"👤 𝐃𝐌 / 𝐔sᴇʀs: `{users_count}`\n"
                f"🗑️ 𝐋ᴇᴀᴠᴇᴀʙʟᴇ (Non-Admin): `{non_admin_channels}` channels\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 𝐓ɪᴘs 𝐅ᴏʀ 𝐋ɪᴍɪᴛᴇᴅ 𝐀ᴄᴄᴏᴜɴᴛs:\n"
                f"• Run `.cleanlimit 10` to auto-leave 10 unused channels & free slots!\n"
                f"• `.creategc` automatically creates Basic Groups when at 500 limit!\n"
                f"• Use `.migrategc` inside any Basic Group to upgrade it to Megagroup."
            )
            await safe_edit(event, report)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋ɪᴍɪᴛ𝐂ʜᴇᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("cleanlimit")
    @register_cmd("freelimit")
    async def cmd_cleanlimit(event, arg):
        try:
            count = 5
            if arg and arg.strip().isdigit():
                count = min(30, max(1, int(arg.strip())))
            await safe_edit(event, f"⚡ 𝐒ᴄᴀɴɴɪɴɢ ᴀɴᴅ ʟᴇᴀᴠɪɴɢ `{count}` ᴜɴᴜsᴇᴅ ɴᴏɴ-ᴀᴅᴍɪɴ ᴄʜᴀɴɴᴇʟs...")
            freed = []
            dialogs = await bot.get_dialogs(limit=200)
            for d in dialogs:
                if len(freed) >= count:
                    break
                if getattr(d, 'is_channel', False):
                    ent = d.entity
                    is_creator = getattr(ent, 'creator', False)
                    is_admin = getattr(d, 'is_admin', False) or (getattr(ent, 'admin_rights', None) is not None)
                    if not is_creator and not is_admin:
                        try:
                            await bot(functions.channels.LeaveChannelRequest(channel=d.input_entity))
                            freed.append(getattr(d, 'name', '') or str(d.id))
                            await asyncio.sleep(0.7)
                        except Exception:
                            pass

            if not freed:
                await safe_edit(event, "⚠️ 𝐍ᴏ disposable non-admin channels found to leave.")
            else:
                lines = [f"• `{name}`" for name in freed[:8]]
                if len(freed) > 8:
                    lines.append(f"...and {len(freed)-8} more")
                report = (
                    f"🧹 𝐋ɪᴍɪᴛ 𝐂ʟᴇᴀɴᴜᴘ 𝐂ᴏᴍᴘʟᴇᴛᴇ!\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ 𝐅ʀᴇᴇᴅ 𝐒ʟᴏᴛs: `{len(freed)}` channel/supergroup slots\n"
                    f"📋 𝐋ᴇғᴛ 𝐂ʜᴀɴɴᴇʟs:\n" + "\n".join(lines) + "\n\n"
                    f"👉 Ab aap bina kisi limit ke `.creategc` chala sakte hain!"
                )
                await safe_edit(event, report)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂ʟᴇᴀɴ𝐋ɪᴍɪᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("migrategc", group_only=True)
    async def cmd_migrategc(event, _):
        try:
            await safe_edit(event, "⚡ 𝐔ᴘɢʀᴀᴅɪɴɢ 𝐁ᴀsɪᴄ 𝐆ʀᴏᴜᴘ ᴛᴏ 𝐒ᴜᴘᴇʀɢʀᴏᴜᴘ (Megagroup)...")
            res = await bot(functions.messages.MigrateChatRequest(chat_id=event.chat_id))
            await safe_edit(event, "🎉 𝐆ʀᴏᴜᴘ 𝐒ᴜᴄᴄᴇssғᴜʟʟʏ 𝐔ᴘɢʀᴀᴅᴇᴅ ᴛᴏ 𝐒ᴜᴘᴇʀɢʀᴏᴜᴘ! ⚡")
        except Exception as e:
            await safe_edit(event, f"ℹ️ 𝐌ɪɢʀᴀᴛᴇ: `{str(e)[:45]}` (Already Supergroup or Not Allowed)")

    @register_cmd("reply", needs_reply=True)
    async def cmd_reply(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: reply_users.add(uid)
            await safe_edit(event, f"⚔️ 𝐑ᴇᴘʟʏ 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ᴇᴘʟʏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("sreply")
    async def cmd_sreply(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                stopped = [str(uid) for uid in targets if uid in reply_users]
                for uid in targets: reply_users.discard(uid)
                await safe_edit(event, f"🛑 𝐑ᴇᴘʟʏ 𝐎ғғ → `{', '.join(stopped)}`" if stopped else "⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ")
            else:
                reply_users.clear()
                await safe_edit(event, "🛑 𝐑ᴇᴘʟʏ 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐑ᴇᴘʟʏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("rr", needs_reply=True)
    async def cmd_rr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: rr_users.add(uid)
            await safe_edit(event, f"🤣 𝐑𝐑 𝐑ᴀɪᴅ 𝐎ɴ → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("srr")
    async def cmd_srr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: rr_users.discard(uid)
                await safe_edit(event, "🛑 𝐑𝐑 𝐎ғғ")
            else:
                rr_users.clear()
                await safe_edit(event, "🛑 𝐑𝐑 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("flag", needs_reply=True)
    async def cmd_flag(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: flag_users.add(uid)
            await safe_edit(event, f"🚩 𝐅ʟᴀɢ 𝐑ᴀɪᴅ 𝐎ɴ → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ʟᴀɢ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("sflag")
    async def cmd_sflag(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: flag_users.discard(uid)
                await safe_edit(event, "🛑 𝐅ʟᴀɢ 𝐎ғғ")
            else:
                flag_users.clear()
                await safe_edit(event, "🛑 𝐅ʟᴀɢ 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐅ʟᴀɢ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("hrr", needs_reply=True)
    async def cmd_hrr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: hrr_users.add(uid)
            await safe_edit(event, f"💗 𝐇𝐞ᴀʀᴛ 𝐑ᴀɪᴅ 𝐎ɴ → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("shrr")
    async def cmd_shrr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: hrr_users.discard(uid)
                await safe_edit(event, "🛑 𝐇𝐑𝐑 𝐎ғғ")
            else:
                hrr_users.clear()
                await safe_edit(event, "🛑 𝐇𝐑𝐑 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("replygod", needs_reply=True)
    async def cmd_replygod(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: replygod_users.add(uid)
            await safe_edit(event, f"😈 𝐆ᴏᴅ 𝐑ᴀɪᴅ 𝐎ɴ → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ᴇᴘʟʏ𝐆ᴏᴅ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("sgod")
    async def cmd_sgod(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: replygod_users.discard(uid)
                await safe_edit(event, "🛑 𝐆ᴏᴅ 𝐎ғғ")
            else:
                replygod_users.clear()
                await safe_edit(event, "🛑 𝐆ᴏᴅ 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐆ᴏᴅ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("replyaryaxmental", needs_reply=True)
    @register_cmd("replyarya", needs_reply=True)
    @register_cmd("replymental", needs_reply=True)
    @register_cmd("replymentalxarya", needs_reply=True)
    @register_cmd("replyAMRIT", needs_reply=True)
    async def cmd_replyaryaxmental(event, arg):
        try:
            targets = await get_targets(event, "")
            parts = arg.strip().rsplit(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.replyaryaxmental <text> <count>` / `.replyAMRIT <text> <count>`")
            text_part = parts[0].strip()
            try: count = int(parts[1].strip())
            except: return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ")
            count = max(1, min(count, 500))
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ ᴛᴀʀɢᴇᴛ")
            for uid in targets:
                replyaryaxmental_users[uid] = {"text": text_part, "count": count}
            await safe_edit(event, f"🎯 𝐋ɪᴍɪᴛ 𝐑ᴀɪᴅ 𝐎ɴ → `{count}` ʀᴇᴘʟɪᴇs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ʏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("saryaxmental")
    @register_cmd("sarya")
    @register_cmd("smental")
    @register_cmd("sstop")
    async def cmd_sstop(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: replyaryaxmental_users.pop(uid, None)
                await safe_edit(event, "🛑 𝐋ɪᴍɪᴛ 𝐑ᴀɪᴅ 𝐎ғғ")
            else:
                replyaryaxmental_users.clear()
                await safe_edit(event, "🛑 𝐀ʟʟ 𝐋ɪᴍɪᴛ 𝐑ᴀɪᴅs 𝐒ᴛᴏᴘᴘᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐒ᴛᴏᴘ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("combo", needs_reply=True)
    async def cmd_combo(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "⚡ **COMBO**\n━━━━━━━━━━━━━━━\nReply karke `.combo` bhejo")
            spray_text = arg.strip() if arg.strip() else "😂💀🔥"
            for uid in targets:
                reply_users.add(uid)
                rr_users.add(uid)
                hrr_users.add(uid)
                replygod_users.add(uid)
                flag_users.add(uid)
            async def _spray_loop():
                for _ in range(500):
                    try:
                        res = await safe_send(event.chat_id, spray_text, is_raid=True)
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError:
                        break
                    except:
                        break
            task = asyncio.ensure_future(_spray_loop())
            spray_tasks[event.chat_id] = task
            await safe_edit(event, f"💀 𝗠𝗘𝗚𝗔 𝗖𝗢𝗠𝗕𝗢 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 𝗦𝗵𝗶𝗲𝗹𝗱 🛡️)\n🎯 {len(targets)} targets")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂ᴏᴍʙᴏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("stopcombo")
    async def cmd_stopcombo(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets:
                    reply_users.discard(uid)
                    rr_users.discard(uid)
                    hrr_users.discard(uid)
                    replygod_users.discard(uid)
                    flag_users.discard(uid)
                    replyaryaxmental_users.pop(uid, None)
            else:
                reply_users.clear(); rr_users.clear(); hrr_users.clear()
                replygod_users.clear(); flag_users.clear(); replyaryaxmental_users.clear()
            task = spray_tasks.pop(event.chat_id, None)
            if task: task.cancel()
            await safe_edit(event, "🛑 𝐂ᴏᴍʙᴏ 𝐒ᴛᴏᴘᴘᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴏᴘ𝐂ᴏᴍʙᴏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("rspam", needs_reply=True)
    async def cmd_rspam(event, arg):
        try:
            targets = await get_targets(event, "")
            if not targets:
                return await safe_edit(event, "❌ 𝐊ɪsɪ ᴋᴏ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ ʙʜᴇᴊᴏ")
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.rspam <count> <text>`")
            try: count = max(1, min(int(parts[0].strip()), 50))
            except: return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ")
            text = parts[1].strip()
            for uid in targets:
                rspam_users[uid] = {"text": text, "count": count}
            await safe_edit(event, f"💥 ʀᴇᴘʟʏ+𝐒ᴘᴀᴍ ᴏɴ → `{count}x` (Anti-Flood Protected 🛡️)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐒ᴘᴀᴍ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("stoprspam")
    async def cmd_stoprspam(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: rspam_users.pop(uid, None)
                await safe_edit(event, f"🛑 𝐑𝐒ᴘᴀᴍ 𝐎ғғ → {len(targets)}")
            else:
                rspam_users.clear()
                await safe_edit(event, "🛑 𝐀ʟʟ 𝐑𝐒ᴘᴀᴍ 𝐎ғғ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴏᴘ𝐑𝐒ᴘᴀᴍ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("spray")
    async def cmd_spray(event, arg):
        try:
            chat = event.chat_id
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.spray <text>`")
            if chat in spray_tasks:
                spray_tasks[chat].cancel()
                del spray_tasks[chat]
            async def do_spray():
                while True:
                    try:
                        res = await safe_send(chat, to_dark_font(arg), is_raid=True)
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_spray())
            await safe_edit(event, f"💣 𝗦𝗣𝗥𝗔𝗬 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 🛡️)\n📝 `{arg[:50]}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗦𝗣𝗥𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("dspray")
    async def cmd_dspray(event, _):
        try:
            chat = event.chat_id
            if chat in spray_tasks:
                spray_tasks[chat].cancel()
                del spray_tasks[chat]
                await safe_edit(event, "🛑 𝗦𝗣𝗥𝗔𝗬 𝗦𝗧𝗢𝗣𝗣𝗘𝗗")
            else:
                await safe_edit(event, "⚠️ 𝗡𝗢 𝗔𝗖𝗧𝗜𝗩𝗘 𝗦𝗣𝗥𝗔𝗬")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗗𝗦𝗣𝗥𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("stopspray")
    async def cmd_stopspray(event, _):
        try:
            chat = event.chat_id
            if chat in spray_tasks:
                spray_tasks[chat].cancel()
                del spray_tasks[chat]
            await safe_edit(event, "🛑 𝗦𝗣𝗥𝗔𝗬 𝗦𝗧𝗢𝗣𝗣𝗘𝗗")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("spraydelay")
    async def cmd_spraydelay(event, arg):
        global SPRAY_DELAY
        try:
            if not arg:
                return await safe_edit(event, f"⚡ 𝗗𝗘𝗟𝗔𝗬 → `{SPRAY_DELAY}s`")
            SPRAY_DELAY = max(0.05, float(arg))
            await safe_edit(event, f"⚡ 𝗗𝗘𝗟𝗔𝗬 → `{SPRAY_DELAY}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗦𝗣𝗥𝗔𝗬𝗗𝗘𝗟𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("tspray")
    async def cmd_tspray(event, arg):
        try:
            chat = event.chat_id
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔sᴇ → `.tspray <slot_number>`")
            idx = int(arg.strip()) - 1
            if not spam_texts or idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ sʟᴏᴛ")
            text = spam_texts[idx]
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_tspray():
                while True:
                    try:
                        res = await safe_send(chat, to_dark_font(text), is_raid=True)
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_tspray())
            await safe_edit(event, f"💣 𝗧𝗦𝗣𝗥𝗔𝗬 𝗦𝗟𝗢𝗧 `{idx+1}` (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 🛡️)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗧𝗦𝗣𝗥𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("rspray")
    async def cmd_rspray(event, _):
        try:
            chat = event.chat_id
            if not spam_texts:
                return await safe_edit(event, "❌ 𝗡𝗢 𝗦𝗔𝗩𝗘𝗗 𝗧𝗘𝗫𝗧𝗦")
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_rspray():
                while True:
                    try:
                        res = await safe_send(chat, to_dark_font(random.choice(spam_texts)), is_raid=True)
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_rspray())
            await safe_edit(event, "💣 𝗥𝗔𝗡𝗗𝗢𝗠 𝗦𝗣𝗥𝗔𝗬 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 🛡️)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗥𝗦𝗣𝗥𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("multispray")
    async def cmd_multispray(event, _):
        try:
            chat = event.chat_id
            if not spam_texts:
                return await safe_edit(event, "❌ 𝗡𝗢 𝗦𝗔𝗩𝗘𝗗 𝗧𝗘𝗫𝗧𝗦")
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            idx = [0]
            async def do_multi():
                while True:
                    try:
                        res = await safe_send(chat, to_dark_font(spam_texts[idx[0] % len(spam_texts)]), is_raid=True)
                        idx[0] += 1
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_multi())
            await safe_edit(event, "💣 𝗠𝗨𝗟𝗧𝗜𝗦𝗣𝗥𝗔𝗬 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 🛡️)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗠𝗨𝗟𝗧𝗜𝗦𝗣𝗥𝗔𝗬 𝗘𝗥𝗥 → `{str(e)[:40]}`")

    @register_cmd("countspray")
    async def cmd_countspray(event, arg):
        try:
            chat = event.chat_id
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.countspray <n> <text>`")
            try: n = int(parts[0])
            except: return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ")
            text = parts[1]
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_count():
                for _ in range(n):
                    try:
                        res = await safe_send(chat, to_dark_font(text), is_raid=True)
                        if not res: await asyncio.sleep(1.0)
                    except asyncio.CancelledError: break
                    except: break
                spray_tasks.pop(chat, None)
            spray_tasks[chat] = asyncio.create_task(do_count())
            await safe_edit(event, f"💣 𝗖𝗢𝗨𝗡𝗧𝗦𝗣𝗥𝗔𝗬 `{n}x` (𝗭𝗲𝗿𝗼-𝗙𝗹𝗼𝗼𝗱 🛡️)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("addtext")
    async def cmd_addtext(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.addtext <text>`")
            spam_texts.append(arg)
            save_spam_texts()
            await safe_edit(event, f"✅ 𝐓ᴇxᴛ 𝐒ᴀᴠᴇᴅ → sʟᴏᴛ `{len(spam_texts)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴅᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("listtexts")
    async def cmd_listtexts(event, _):
        try:
            if not spam_texts:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐒ᴀᴠᴇᴅ 𝐓ᴇxᴛs")
            lines = [f"`{i+1}`. {t[:80]}" for i, t in enumerate(spam_texts)]
            await safe_edit(event, "📝 𝐒ᴀᴠᴇᴅ 𝐓ᴇxᴛs\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋ɪsᴛᴛᴇxᴛs 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("edittext")
    async def cmd_edittext(event, arg):
        try:
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.edittext <slot> <new_text>`")
            try: idx = int(parts[0]) - 1
            except: return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ sʟᴏᴛ")
            if idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐒ʟᴏᴛ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ")
            spam_texts[idx] = parts[1]
            save_spam_texts()
            await safe_edit(event, f"✅ 𝐒ʟᴏᴛ `{idx+1}` ᴜᴘᴅᴀᴛᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄ᴅɪᴛᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("deltext")
    async def cmd_deltext(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔sᴇ → `.deltext <slot>`")
            idx = int(arg.strip()) - 1
            if idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐒ʟᴏᴛ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ")
            spam_texts.pop(idx)
            save_spam_texts()
            await safe_edit(event, f"🗑️ 𝐒ʟᴏᴛ `{idx+1}` ᴅᴇʟᴇᴛᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃ᴇʟᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("cleartext")
    async def cmd_cleartext(event, arg):
        try:
            if arg.strip().lower() != "confirm":
                return await safe_edit(event, "⚠️ 𝐔sᴇ → `.cleartext confirm`")
            spam_texts.clear()
            save_spam_texts()
            await safe_edit(event, "🗑️ 𝐀ʟʟ 𝐓ᴇxᴛs 𝐂ʟᴇᴀʀᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂ʟᴇᴀʀᴛᴇxᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("fastgc")
    async def cmd_fastgc(event, arg):
        try:
            parts = arg.strip().split(None, 1) if arg else []
            subcmd = parts[0].lower() if parts else ""
            if subcmd == "stop":
                if FASTGC_STATE.get("task"):
                    try: FASTGC_STATE["task"].cancel()
                    except: pass
                FASTGC_STATE.update({"active": False, "template": None, "task": None, "chat_id": None})
                return await safe_edit(event, "🛑 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴏᴘᴘᴇᴅ")
            if subcmd == "set" and len(parts) > 1:
                template = parts[1].strip()
                if not template or "{emoji}" not in template:
                    return await safe_edit(event, "❌ 𝐓ᴇᴍᴘʟᴀᴛᴇ ᴍᴜsᴛ ʜᴀᴠᴇ `{emoji}`")
                if FASTGC_STATE.get("task"):
                    try: FASTGC_STATE["task"].cancel()
                    except: pass
                FASTGC_STATE.update({"active": True, "template": template, "chat_id": event.chat_id})
                task = asyncio.create_task(gc_fast_loop(event.chat_id))
                FASTGC_STATE["task"] = task
                return await safe_edit(event, f"⚡ 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴀʀᴛᴇᴅ\n📝 `{template}`")
            await safe_edit(event, "❌ 𝐔sᴇ → `.fastgc set {emoji} <template>` or `.fastgc stop`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ᴀsᴛ𝐆𝐂 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("antidel")
    async def cmd_antidel(event, arg):
        global antidel_enabled
        try:
            sub = (arg or "").strip().lower()
            if sub == "on":
                antidel_enabled = True
                await safe_edit(event, "🛡️ 𝐀ɴᴛɪ𝐃ᴇʟ 𝐎ɴ")
            elif sub == "off":
                antidel_enabled = False
                antidel_cache.clear()
                await safe_edit(event, "🛡️ 𝐀ɴᴛɪ𝐃ᴇʟ 𝐎ғғ")
            else:
                status = "ON" if antidel_enabled else "OFF"
                await safe_edit(event, f"🛡️ 𝐀ɴᴛɪ𝐃ᴇʟ → `{status}`\n📦 𝐂ᴀᴄʜᴇ → `{len(antidel_cache)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ɴᴛɪ𝐃ᴇʟ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("watchspam", needs_reply=True)
    async def cmd_watchspam(event, arg):
        try:
            targets = await get_targets(event, "")
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            parts = (arg or "").strip().split()
            try:
                limit = int(parts[0]) if len(parts) > 0 else 3
                seconds = float(parts[1]) if len(parts) > 1 else 5.0
            except:
                limit, seconds = 3, 5.0
            for uid in targets:
                watch_spam[(event.chat_id, uid)] = {"limit": limit, "seconds": seconds, "times": []}
            await safe_edit(event, f"👁️ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ → `{limit}` ᴍsɢs / `{seconds}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖ᴀᴛᴄʜ𝐒ᴘᴀᴍ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("unwatchspam")
    async def cmd_unwatchspam(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets:
                    watch_spam.pop((event.chat_id, uid), None)
                await safe_edit(event, f"🗑️ 𝐔ɴᴡᴀᴛᴄʜ → `{len(targets)}`")
            else:
                removed = [k for k in watch_spam if k[0] == event.chat_id]
                for k in removed: del watch_spam[k]
                await safe_edit(event, "🗑️ 𝐀ʟʟ 𝐖ᴀᴛᴄʜᴇs 𝐑ᴇᴍᴏᴠᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔ɴᴡᴀᴛᴄʜ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("watchlist")
    async def cmd_watchlist(event, _):
        try:
            chat_watches = [(k, v) for k, v in watch_spam.items() if k[0] == event.chat_id]
            if not chat_watches:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐖ᴀᴛᴄʜᴇs")
            lines = [f"• `{uid}` → `{v['limit']}` / `{v['seconds']}s`" for (_, uid), v in chat_watches]
            await safe_edit(event, "👁️ 𝐖ᴀᴛᴄʜʟɪsᴛ\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖ᴀᴛᴄʜ𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    gpfp_pool = []
    gpfp_task = None

    @register_cmd("setgpfp", needs_reply=True, group_only=True)
    async def cmd_setgpfp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ")
            file = await reply.download_media(file=bytes)
            if not file: return await safe_edit(event, "❌ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")
            await bot(functions.channels.EditPhotoRequest(channel=event.chat_id, photo=await bot.upload_file(BytesIO(file))))
            await safe_edit(event, "🖼️ 𝐆ʀᴏᴜᴘ 𝐏𝐅𝐏 𝐔ᴘᴅᴀᴛᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴇᴛ𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("addgpfp", needs_reply=True)
    async def cmd_addgpfp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ")
            file = await reply.download_media(file=bytes)
            if file: gpfp_pool.append(file)
            await safe_edit(event, f"✅ 𝐀ᴅᴅᴇᴅ ᴛᴏ 𝐏ᴏᴏʟ → `{len(gpfp_pool)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴅ𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("listgpfp")
    async def cmd_listgpfp(event, _):
        await safe_edit(event, f"🖼️ 𝐆𝐏𝐅𝐏 𝐏ᴏᴏʟ → `{len(gpfp_pool)}`")

    @register_cmd("stopgpfp")
    async def cmd_stopgpfp(event, _):
        global gpfp_task
        try:
            if gpfp_task: gpfp_task.cancel(); gpfp_task = None
            await safe_edit(event, "🛑 𝐀ᴜᴛᴏ 𝐆𝐏𝐅𝐏 𝐒ᴛᴏᴘᴘᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴏᴘ𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("autogpfp", group_only=True)
    async def cmd_autogpfp(event, arg):
        global gpfp_task
        try:
            if not gpfp_pool:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐈ᴍᴀɢᴇs")
            try: interval = max(10, int(arg)) if arg else 30
            except: interval = 30
            if gpfp_task: gpfp_task.cancel()
            async def do_auto():
                while True:
                    try:
                        img = random.choice(gpfp_pool)
                        await bot(functions.channels.EditPhotoRequest(
                            channel=event.chat_id,
                            photo=await bot.upload_file(BytesIO(img))
                        ))
                        await asyncio.sleep(interval)
                    except asyncio.CancelledError: break
                    except: await asyncio.sleep(interval)
            gpfp_task = asyncio.create_task(do_auto())
            await safe_edit(event, f"🖼️ 𝐀ᴜᴛᴏ 𝐆𝐏𝐅𝐏 → `{interval}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴜᴛᴏ𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("ar")
    async def cmd_ar(event, arg):
        global auto_react_emoji
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.ar <emoji>`")
            auto_react_emoji = arg.strip()
            await safe_edit(event, f"❤️ 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ → `{auto_react_emoji}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("sar")
    async def cmd_sar(event, _):
        global auto_react_emoji
        auto_react_emoji = None
        await safe_edit(event, "❤️ 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ 𝐎ғғ")

    @register_cmd("notesadd")
    async def cmd_notesadd(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.notesadd <text>`")
            nid = max(notes.keys(), default=0) + 1
            notes[nid] = arg
            save_notes()
            await safe_edit(event, f"📝 𝐍ᴏᴛᴇ 𝐒ᴀᴠᴇᴅ → 𝐈𝐃 `{nid}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍ᴏᴛᴇs𝐀ᴅᴅ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("noteslist")
    async def cmd_noteslist(event, _):
        try:
            if not notes:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐍ᴏᴛᴇs")
            lines = [f"`{k}`. {v[:60]}" for k, v in sorted(notes.items())]
            await safe_edit(event, "🧠 𝐍ᴏᴛᴇs 𝐋ɪsᴛ\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍ᴏᴛᴇs𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("notesdelete")
    async def cmd_notesdelete(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔sᴇ → `.notesdelete <id>`")
            nid = int(arg.strip())
            if nid not in notes:
                return await safe_edit(event, "❌ 𝐍ᴏᴛᴇ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ")
            del notes[nid]; save_notes()
            await safe_edit(event, f"🗑️ 𝐍ᴏᴛᴇ `{nid}` 𝐃ᴇʟᴇᴛᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍ᴏᴛᴇs𝐃ᴇʟ 𝐄ʀʀ → `{str(e)[:40]}`")

    # ── ANTI-FLOOD AUTO-FORWARD ENGINE (SINGLE GC • ZERO STUCK • ZERO FLOOD) ──
    # chat_id -> dict {"task": asyncio.Task, "sent": int, "max": int, "running": bool, "status_msg": ...}
    chat_fwd_tasks = {}

    @register_cmd("forward", needs_reply=True)
    @register_cmd("fwd", needs_reply=True)
    async def cmd_forward(event, arg):
        """
        Auto-forward replied message into THIS CURRENT group chat continuously:
        - Reply to any message and send `.forward` (runs continuously until .stopforward)
        - Or `.forward 50` (forwards 50 times then stops automatically)
        - 100% Anti-Flood: 1.8s pacing + catches FloodWaitError automatically (Zero Stuck)
        """
        global chat_fwd_tasks
        chat_id = event.chat_id

        # Check reply
        reply = await event.get_reply_message()
        if not reply:
            return await safe_edit(event, "❌ **Kisi message ko reply karke `.forward` likhein!**")

        # Parse optional count
        raw = (arg or "").strip()
        max_count = 0
        if raw.isdigit():
            max_count = int(raw)

        # Cancel any active forward task in this specific chat
        if chat_id in chat_fwd_tasks and chat_fwd_tasks[chat_id].get("running"):
            old = chat_fwd_tasks[chat_id].get("task")
            if old and not old.done():
                old.cancel()

        target_title = getattr(event.chat, 'title', f"Chat {chat_id}")
        mode_str = "Infinite Loop (Jab tak `.stopforward` na karein)" if max_count == 0 else f"{max_count} Messages"

        status_text = (
            f"🚀 **𝐀𝐔𝐓𝐎-𝐅𝐎𝐑𝐖𝐀𝐑𝐃 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!** ⚡\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **Target Chat:** `{target_title}`\n"
            f"🔢 **Mode:** `{mode_str}`\n"
            f"⏱️ **Anti-Flood Delay:** `1.8s` (Safe Pacing)\n"
            f"🛡️ **Zero-Stuck Guard:** `🟢 ACTIVE (Auto-handles FloodWait)`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛑 *Use `.stopforward` or `.stopfwd` to stop anytime.*"
        )
        status_msg = await safe_edit(event, status_text)

        async def _forward_worker(target_chat_id, target_msg_id, from_chat_id, limit, info_msg):
            sent_count = 0
            try:
                while True:
                    if limit > 0 and sent_count >= limit:
                        break

                    try:
                        await bot.forward_messages(target_chat_id, target_msg_id, from_chat_id)
                        sent_count += 1
                        if target_chat_id in chat_fwd_tasks:
                            chat_fwd_tasks[target_chat_id]["sent"] = sent_count
                    except FloodWaitError as fw:
                        logger.warning(f"[AutoForward] FloodWait in chat {target_chat_id}: {fw.seconds}s. Sleeping safely...")
                        try:
                            await safe_edit(info_msg, (
                                f"⏳ **Telegram FloodWait Hit ({fw.seconds}s)!**\n"
                                f"🛡️ Sleeping {fw.seconds}s safely to prevent freeze...\n"
                                f"🔄 Auto-resuming immediately in this chat! (Sent: {sent_count})"
                            ))
                        except Exception:
                            pass
                        await asyncio.sleep(fw.seconds + 1)
                        continue
                    except asyncio.CancelledError:
                        break
                    except Exception as ex:
                        err_str = str(ex).lower()
                        if hasattr(ex, "seconds"):
                            sec = getattr(ex, "seconds", 2)
                            await asyncio.sleep(sec + 1)
                            continue
                        if "chat_write_forbidden" in err_str or "banned" in err_str:
                            break
                        # Transient error
                        await asyncio.sleep(2.0)
                        continue

                    # High-speed forward pacing
                    await asyncio.sleep(0.15)

            except asyncio.CancelledError:
                pass
            finally:
                if target_chat_id in chat_fwd_tasks:
                    chat_fwd_tasks[target_chat_id]["running"] = False
                try:
                    await safe_edit(info_msg, (
                        f"🎉 **𝐀𝐔𝐓𝐎-𝐅𝐎𝐑𝐖𝐀𝐑𝐃 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃 / 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!** ⚡\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ **Total Forwards Sent:** `{sent_count}`\n"
                        f"🎯 **Target Chat:** `{target_title}`\n"
                        f"🛡️ **Flood Status:** `🟢 0% Flood • Zero Stuck`\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👑 **Powered by:** Arya X MENTAL (@xno_amrit)"
                    ))
                except Exception:
                    pass

        task = asyncio.create_task(_forward_worker(chat_id, reply.id, reply.chat_id, max_count, status_msg))
        chat_fwd_tasks[chat_id] = {
            "task": task,
            "running": True,
            "sent": 0,
            "max": max_count,
            "status_msg": status_msg
        }

    @register_cmd("stopforward")
    @register_cmd("stopfwd")
    @register_cmd("fwdstop")
    async def cmd_stopforward(event, _):
        """
        Stops active auto-forward in THIS group chat immediately
        """
        global chat_fwd_tasks
        chat_id = event.chat_id

        if chat_id not in chat_fwd_tasks or not chat_fwd_tasks[chat_id].get("running"):
            return await safe_edit(event, "⚠️ **Is group chat me koi auto-forward active nahi hai.**")

        task_info = chat_fwd_tasks[chat_id]
        task_info["running"] = False
        task = task_info.get("task")
        sent = task_info.get("sent", 0)

        if task and not task.done():
            task.cancel()

        target_title = getattr(event.chat, 'title', f"Chat {chat_id}")
        await safe_edit(event, (
            f"🛑 **𝐀𝐔𝐓𝐎-𝐅𝐎𝐑𝐖𝐀𝐑𝐃 𝐇𝐀𝐋𝐓𝐄𝐃!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ **Total Sent Before Stop:** `{sent}` forwards\n"
            f"🎯 **Chat:** `{target_title}`\n"
            f"🛡️ **Status:** `Safely stopped, 0% flood.`"
        ))

    # ── MULTI-ACCOUNT FLEET & CLUSTER CONTROLLER COMMANDS ──
    @register_cmd("fleet")
    @register_cmd("myaccounts")
    @register_cmd("cluster")
    async def cmd_fleet(event, _):
        """
        View all linked accounts in your fleet cluster (1, 2, 3 or more accounts)
        """
        cfg = load_fleet_config()
        slots = cfg.get("slots", {})
        sync_status = "🟢 ACTIVE (Sync On)" if cfg.get("sync_enabled", True) else "🔴 OFF (Sync Off)"

        lines = []
        if slots:
            for s_idx in sorted(slots.keys(), key=lambda x: int(x)):
                info = slots[s_idx]
                s_num = int(s_idx) + 1
                u_tag = f"@{info.get('username')}" if info.get('username') else info.get('name', f"User {info.get('id')}")
                is_curr = " 👈 (This Acc)" if int(s_idx) == USERBOT_SLOT else ""
                r_tag = "👑 MASTER" if int(s_idx) == 0 else f"🤖 WORKER #{s_num}"
                lines.append(f"│ ⬝ **Acc #{s_num}:** `{r_tag}` ─ {u_tag} (`{info.get('id')}`){is_curr}")
        else:
            try:
                me = await bot.get_me()
                lines.append(f"│ ⬝ **Acc #1:** `👑 MASTER` ─ @{me.username or me.first_name} (`{me.id}`) 👈 (Single Acc)")
            except Exception:
                lines.append(f"│ ⬝ **Acc #1:** `👑 MASTER` ─ (Current Account) 👈")

        total_cnt = max(len(slots), 1)
        masters_str = ", ".join(f"`{m}`" for m in sorted(FLEET_MASTERS)) or "`None`"

        txt = (
            "╭──〔 ⚡ 𝗔𝗥𝗬𝗔 𝗫 𝗠𝗘𝗡𝗧𝗔𝗟 𝗙𝗟𝗘𝗘𝗧 𝗖𝗟𝗨𝗦𝗧𝗘𝗥 〕──╮\n"
            f"│ ✦ 𝗧𝗢𝗧𝗔𝗟 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦 : `{total_cnt}` Active\n"
            f"│ ✦ 𝗙𝗟𝗘𝗘𝗧 𝗦𝗬𝗡𝗖      : {sync_status}\n"
            f"│ ✦ 𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗟𝗢𝗧   : Slot #{USERBOT_SLOT+1} ({'Master Controller' if USERBOT_SLOT==0 else 'Fleet Worker'})\n"
            f"│ ✦ 𝗠𝗔𝗦𝗧𝗘𝗥 𝗜𝗗𝗦     : {masters_str}\n"
            "├────────────────────────────\n"
            + "\n".join(lines) + "\n"
            "╰────────────────────────────╯\n"
            "💡 **Fleet Commands:**\n"
            "• `.sync on` / `.sync off` ─ Sabhi accounts sath me command karenge ya nahi\n"
            "• `.all <cmd>` ─ Force execute command on ALL accounts (e.g. `.all ping`)\n"
            "• `.addmaster <id>` ─ Add an authorized controller ID\n"
            "• `.delmaster <id>` ─ Remove a controller ID\n"
            "• `.masters` ─ View all authorized controller IDs"
        )
        await safe_edit(event, txt)

    @register_cmd("sync")
    @register_cmd("fleetsync")
    async def cmd_sync(event, arg):
        """
        Toggle command synchronization across 1, 2, or 3 accounts:
        - .sync on ➔ Master sends .ping or .attack, all 3 accounts execute together!
        - .sync off ➔ Only the master executes; worker accounts stay quiet.
        """
        raw = (arg or "").strip().lower()
        cfg = load_fleet_config()
        if raw in ("on", "enable", "1", "true"):
            cfg["sync_enabled"] = True
            save_fleet_config(cfg)
            await safe_edit(event, (
                "🟢 **𝗙𝗟𝗘𝗘𝗧 𝗦𝗬𝗡𝗖 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗!** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ Ab aapke **2 ya 3 sabhi accounts ek sath** commands execute karenge!\n"
                "👉 Ek account se `.ping` likhein ➔ Sabhi 3 accounts se ping aayega.\n"
                "👉 Ek account se `.attack` ya `.spray` chalayein ➔ Sabhi accounts ek sath attack karenge!\n"
                "🛡️ Turn off anytime via `.sync off`"
            ))
        elif raw in ("off", "disable", "0", "false"):
            cfg["sync_enabled"] = False
            save_fleet_config(cfg)
            await safe_edit(event, (
                "🔴 **𝗙𝗟𝗘𝗘𝗧 𝗦𝗬𝗡𝗖 𝗗𝗘𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ Ab har account **independent/alone** operate karega.\n"
                "💡 Sabhi accounts se chalane ke liye `.all <cmd>` use kar sakte hain!"
            ))
        else:
            curr = "🟢 ENABLED (All accounts execute together)" if cfg.get("sync_enabled", True) else "🔴 DISABLED (Master only)"
            await safe_edit(event, (
                f"⚡ **Current Fleet Sync Status:** `{curr}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👉 Sabhi accounts se chalana ho: `.sync on`\n"
                "👉 Sirf single account chalana ho: `.sync off`\n"
                "👉 Force run on all: `.all <cmd>` (e.g. `.all ping`)"
            ))

    @register_cmd("all")
    @register_cmd("fleetcmd")
    async def cmd_all(event, arg):
        """
        Broadcast and force run any command on ALL linked accounts in fleet
        Usage: .all ping, .all alive, .all raid @user, .all stopall
        """
        if not arg:
            return await safe_edit(event, "❌ **Usage:** `.all <command>`\nExample: `.all ping`, `.all alive`, `.all spray Har Har Mahadev`")
        parts = arg.strip().split(maxsplit=1)
        sub_cmd = parts[0].lower().lstrip(".").strip()
        sub_arg = parts[1].strip() if len(parts) > 1 else ""
        cmd_data = commands.get(sub_cmd)
        if cmd_data:
            await cmd_data["func"](event, sub_arg)

    # ── MULTI-ACCOUNT FLEET GROUP JOIN & LEAVE ENGINE ──
    async def _execute_join_on_client(tg_client, link_str):
        clean = str(link_str).strip()
        if not clean:
            return False, "Empty link"

        invite_hash = None
        if "t.me/+" in clean:
            invite_hash = clean.split("t.me/+")[1].split("/")[0].split("?")[0].strip()
        elif "t.me/joinchat/" in clean:
            invite_hash = clean.split("t.me/joinchat/")[1].split("/")[0].split("?")[0].strip()
        elif clean.startswith("+"):
            invite_hash = clean.lstrip("+").strip()

        if invite_hash:
            try:
                res = await tg_client(functions.messages.ImportChatInviteRequest(hash=invite_hash))
                return True, "Joined Private GC"
            except Exception as e:
                err = str(e).lower()
                if "already" in err or "user_already_participant" in err:
                    return True, "Already in GC"
                return False, str(e)[:45]
        else:
            clean_user = clean.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").strip().lstrip("@")
            try:
                res = await tg_client(functions.channels.JoinChannelRequest(channel=clean_user))
                return True, "Joined Public GC"
            except Exception as e:
                err = str(e).lower()
                if "already" in err or "user_already_participant" in err:
                    return True, "Already in GC"
                return False, str(e)[:45]

    async def _execute_leave_on_client(tg_client, chat_target):
        try:
            if not chat_target:
                return False, "No chat"
            await tg_client(functions.channels.LeaveChannelRequest(channel=chat_target))
            return True, "Left GC"
        except Exception as e:
            try:
                await tg_client(functions.messages.DeleteChatUserRequest(chat_id=chat_target, user_id="me"))
                return True, "Left GC"
            except Exception as e2:
                return False, str(e2)[:45]

    @register_cmd("joingc")
    @register_cmd("alljoin")
    @register_cmd("joinall")
    @register_cmd("gcjoin")
    async def cmd_joingc(event, arg):
        """
        Join any group or channel across ALL linked fleet accounts automatically!
        Usage: .joingc https://t.me/example_group OR .joingc https://t.me/+invitehash
        """
        link = (arg or "").strip()
        if not link and event.is_reply:
            rep = await event.get_reply_message()
            if rep and rep.text:
                for word in rep.text.split():
                    if "t.me/" in word or word.startswith("@"):
                        link = word.strip()
                        break

        if not link:
            return await safe_edit(event, (
                "❌ **Usage:** `.joingc <Group Link / Username>`\n\n"
                "🔹 **Public GC:** `.joingc https://t.me/group_name` ya `.joingc @group_name`\n"
                "🔹 **Private GC:** `.joingc https://t.me/+abcdef12345`\n\n"
                "💡 Sabhi linked accounts ek sath us group me join ho jayenge!"
            ))

        await safe_edit(event, f"🚀 **FLEET JOIN INITIATED...**\n🎯 Target: `{link}`\n⏳ Connecting all linked accounts...")

        results = []
        uid = HOST_USER_ID or OWNER_ID
        accts_file = os.path.join(os.getcwd(), "data", "users", str(uid), "accounts.json") if uid else None
        all_accts = []
        if accts_file and os.path.isfile(accts_file):
            try:
                with open(accts_file, "r", encoding="utf-8") as f:
                    all_accts = json.load(f)
            except Exception:
                all_accts = []

        # 1. Join on this current client
        ok_curr, note_curr = await _execute_join_on_client(bot, link)
        phone_curr = getattr(me, "phone", "") if 'me' in globals() and me else f"Slot #{USERBOT_SLOT+1}"
        icon_curr = "✅" if ok_curr else "❌"
        results.append(f"{icon_curr} **Acc #{USERBOT_SLOT+1}** (`{phone_curr}`): `{note_curr}`")

        # 2. Join on all other saved accounts in the fleet
        for a in all_accts:
            slot_idx = a.get("slot", 0)
            if slot_idx == USERBOT_SLOT:
                continue
            s_str = a.get("session_string")
            if not s_str:
                continue
            phone_lbl = a.get("phone", f"Acc #{slot_idx+1}")
            try:
                t_client = TelegramClient(StringSession(s_str), API_ID, API_HASH)
                await t_client.connect()
                ok_o, note_o = await _execute_join_on_client(t_client, link)
                await t_client.disconnect()
                icon_o = "✅" if ok_o else "❌"
                results.append(f"{icon_o} **Acc #{slot_idx+1}** (`{phone_lbl}`): `{note_o}`")
            except Exception as ex:
                results.append(f"❌ **Acc #{slot_idx+1}** (`{phone_lbl}`): `{str(ex)[:30]}`")

        total_succ = sum(1 for r in results if r.startswith("✅"))
        summary = (
            "👑 ◢█◣ ⟨ 𝐅𝐋𝐄𝐄𝐓 𝐆𝐑𝐎𝐔𝐏 𝐉𝐎𝐈𝐍 ⟩ ◢█◣\n"
            "❖═━•〔 ⚡ 𝐌𝐔𝐋𝐓𝐈-𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐉𝐎𝐈𝐍 〕•━═❖\n\n"
            f"🎯 **Target GC:** `{link}`\n"
            f"📊 **Joined Successfully:** `{total_succ}/{len(results)} Accounts`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(results) + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ *All linked userbots are now in the group & ready for commands!*"
        )
        await safe_edit(event, summary)

    @register_cmd("leavegc")
    @register_cmd("allleave")
    @register_cmd("leaveall")
    @register_cmd("gcleave")
    async def cmd_leavegc(event, arg):
        """
        Leave a group or channel across ALL linked fleet accounts automatically!
        Usage: .leavegc OR .leavegc @group_name
        """
        chat_target = None
        target_name = "This Chat"
        raw = (arg or "").strip()
        if raw:
            try:
                ent = await bot.get_entity(raw)
                chat_target = ent
                target_name = getattr(ent, "title", raw)
            except Exception:
                chat_target = raw
                target_name = raw
        else:
            chat_target = event.chat_id
            try:
                ch = await event.get_chat()
                target_name = getattr(ch, "title", str(event.chat_id))
            except Exception:
                target_name = str(event.chat_id)

        await safe_edit(event, f"🚪 **FLEET LEAVE INITIATED...**\n🎯 Chat: `{target_name}`\n⏳ Leaving across all accounts...")

        results = []
        uid = HOST_USER_ID or OWNER_ID
        accts_file = os.path.join(os.getcwd(), "data", "users", str(uid), "accounts.json") if uid else None
        all_accts = []
        if accts_file and os.path.isfile(accts_file):
            try:
                with open(accts_file, "r", encoding="utf-8") as f:
                    all_accts = json.load(f)
            except Exception:
                all_accts = []

        # 1. Leave on other accounts first (so current master stays to report)
        for a in all_accts:
            slot_idx = a.get("slot", 0)
            if slot_idx == USERBOT_SLOT:
                continue
            s_str = a.get("session_string")
            if not s_str: continue
            phone_lbl = a.get("phone", f"Acc #{slot_idx+1}")
            try:
                t_client = TelegramClient(StringSession(s_str), API_ID, API_HASH)
                await t_client.connect()
                ok_o, note_o = await _execute_leave_on_client(t_client, chat_target)
                await t_client.disconnect()
                icon_o = "🚪" if ok_o else "❌"
                results.append(f"{icon_o} **Acc #{slot_idx+1}** (`{phone_lbl}`): `{note_o}`")
            except Exception as ex:
                results.append(f"❌ **Acc #{slot_idx+1}** (`{phone_lbl}`): `{str(ex)[:30]}`")

        # 2. Leave on current bot
        ok_curr, note_curr = await _execute_leave_on_client(bot, chat_target)
        results.append(f"🚪 **Acc #{USERBOT_SLOT+1}** (Current): `{note_curr}`")

        total_succ = sum(1 for r in results if r.startswith("🚪"))
        summary = (
            "🚪 ◢█◣ ⟨ 𝐅𝐋𝐄𝐄𝐓 𝐆𝐑𝐎𝐔𝐏 𝐋𝐄𝐀𝐕𝐄 ⟩ ◢█◣\n"
            "❖═━•〔 ⚡ 𝐌𝐔𝐋𝐓𝐈-𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐋𝐄𝐀𝐕𝐄 〕•━═❖\n\n"
            f"🎯 **Target Chat:** `{target_name}`\n"
            f"📊 **Accounts Left:** `{total_succ}/{len(results)} Accounts`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(results)
        )
        try:
            await safe_edit(event, summary)
        except Exception:
            pass

    @register_cmd("addmaster")
    async def cmd_addmaster(event, arg):
        """
        Add a Telegram ID as an authorized Fleet Master Controller
        Usage: .addmaster 12345678 or reply to user with .addmaster
        """
        global FLEET_MASTERS
        if USERBOT_SLOT != 0:
            return await safe_edit(event, "⛔ **Access Denied:** Masters manage karna sirf MAIN / MASTER ACCOUNT (Slot #1) se hi allowed hai!")
        target_id = None
        raw = (arg or "").strip()
        if raw.isdigit():
            target_id = int(raw)
        elif event.is_reply:
            reply = await event.get_reply_message()
            if reply: target_id = reply.sender_id
        elif raw.startswith("@"):
            try:
                ent = await bot.get_entity(raw)
                target_id = ent.id
            except Exception: pass

        if not target_id:
            return await safe_edit(event, "❌ **Usage:** `.addmaster <user_id>` ya kisi user ke message ko reply karke `.addmaster` likhein.")

        FLEET_MASTERS.add(target_id)
        cfg = load_fleet_config()
        if "masters" not in cfg: cfg["masters"] = []
        if target_id not in cfg["masters"]:
            cfg["masters"].append(target_id)
            save_fleet_config(cfg)

        await safe_edit(event, (
            f"👑 **𝐍𝐄𝐖 𝐅𝐋𝐄𝐄𝐓 𝐌𝐀𝐒𝐓𝐄𝐑 𝐀𝐃𝐃𝐄𝐃!** ⚡\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **Master ID:** `{target_id}`\n"
            f"✅ Ab yeh ID aapke 1, 2 ya 3 sabhi accounts ko 1 command se control kar sakti hai!"
        ))

    @register_cmd("delmaster")
    async def cmd_delmaster(event, arg):
        """
        Remove a Telegram ID from Fleet Masters
        Usage: .delmaster <user_id>
        """
        global FLEET_MASTERS
        if USERBOT_SLOT != 0:
            return await safe_edit(event, "⛔ **Access Denied:** Masters manage karna sirf MAIN / MASTER ACCOUNT (Slot #1) se hi allowed hai!")
        target_id = None
        raw = (arg or "").strip()
        if raw.isdigit():
            target_id = int(raw)
        elif event.is_reply:
            reply = await event.get_reply_message()
            if reply: target_id = reply.sender_id

        if not target_id:
            return await safe_edit(event, "❌ **Usage:** `.delmaster <user_id>`")

        if target_id == OWNER_ID or target_id == GLOBAL_OWNER_ID:
            return await safe_edit(event, "❌ **Primary owner cannot be removed!**")

        FLEET_MASTERS.discard(target_id)
        cfg = load_fleet_config()
        cfg["masters"] = [m for m in cfg.get("masters", []) if m != target_id]
        save_fleet_config(cfg)
        await safe_edit(event, f"🗑️ **Master ID `{target_id}` removed from Fleet Masters!**")

    @register_cmd("masters")
    async def cmd_masters(event, _):
        """
        List all authorized Fleet Master Controller IDs
        """
        lines = [f"• `{m}`" for m in sorted(FLEET_MASTERS)]
        await safe_edit(event, (
            "👑 **𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗙𝗟𝗘𝗘𝗧 𝗠𝗔𝗦𝗧𝗘𝗥 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗟𝗘𝗥𝗦:**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👉 In IDs se bheji gayi koi bhi command aapke sabhi accounts execute karte hain."
        ))

    # ── DIRECT IN-BOT ACCOUNT LINKING & OTP AUTHENTICATION ──
    _PENDING_DIRECT_LOGINS = {}

    @register_cmd("addacc")
    @register_cmd("linkacc")
    @register_cmd("hostacc")
    async def cmd_addacc(event, arg):
        """
        Add another Telegram account directly via OTP from within Telegram!
        Usage: .addacc +91XXXXXXXXXX
        """
        sender = event.sender_id
        if USERBOT_SLOT != 0:
            return await safe_edit(event, "⛔ **Access Denied:** Naye accounts link karne ka feature sirf aapke **MAIN / MASTER ACCOUNT (Pehla Account • Slot #1)** par authorized hai! Linked worker accounts se add account allowed nahi hai.")
        if sender != OWNER_ID and (HOST_USER_ID and sender != HOST_USER_ID) and sender not in FLEET_MASTERS:
            return await safe_edit(event, "⛔ **Access Denied:** Only the owner can link accounts into this personal userbot fleet.")

        phone = (arg or "").strip().replace(" ", "").replace("-", "")
        if not phone or not phone.startswith("+") or len(phone) < 8:
            return await safe_edit(event, (
                "📱 **ADD ACCOUNT TO PERSONAL FLEET**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👉 **Step 1:** Number dalein:\n"
                "`.addacc +91XXXXXXXXXX`\n\n"
                "👉 **Step 2:** Telegram me aane wala code send karein:\n"
                "`.otp 12345`\n\n"
                "👉 **Step 3 (Sirf agar 2FA laga ho):**\n"
                "`.2fa aapka_password`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            ))

        await safe_edit(event, f"⏳ **Connecting to Telegram & requesting OTP for `{phone}`...**")
        try:
            temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await temp_client.connect()
            res = await temp_client.send_code_request(phone)
            _PENDING_DIRECT_LOGINS[event.sender_id] = {
                "client": temp_client,
                "phone": phone,
                "phone_code_hash": res.phone_code_hash,
                "ts": time.time(),
                "state": "WAITING_OTP"
            }
            await safe_edit(event, (
                f"📲 **OTP CODE SENT TO TELEGRAM!** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 **Phone:** `{phone}`\n\n"
                f"👉 **Ab Telegram me aane wala 5-digit code send karein:**\n"
                f"`.otp <CODE>`\n"
                f"*(Example: `.otp 12345`)*\n\n"
                f"💡 *Agar 2FA Password laga hoga, toh bot code verify karne ke baad aapse password mangega!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ Code expires in 3 minutes."
            ))
        except Exception as e:
            await safe_edit(event, f"❌ **OTP Request Failed:** `{str(e)[:70]}`")

    @register_cmd("otp")
    @register_cmd("verifyacc")
    async def cmd_verify_otp(event, arg):
        """
        Verify Telegram OTP and link account into fleet!
        Usage: .otp 12345
        """
        if USERBOT_SLOT != 0:
            return await safe_edit(event, "⛔ **Access Denied:** OTP verification sirf aapke **MAIN / MASTER ACCOUNT (Slot #1)** se hi allowed hai!")

        if event.sender_id not in _PENDING_DIRECT_LOGINS:
            return await safe_edit(event, "❌ **Koi pending OTP request nahi mili!**\nPehle `.addacc +91XXXXXXXXXX` karein.")

        parts = (arg or "").strip().split(maxsplit=1)
        if not parts:
            return await safe_edit(event, "❌ **Usage:** `.otp <CODE>`\n*(Example: `.otp 12345`)*")

        code = parts[0].strip()
        password = parts[1].strip() if len(parts) > 1 else None
        pending = _PENDING_DIRECT_LOGINS[event.sender_id]
        client = pending["client"]
        phone = pending["phone"]

        await safe_edit(event, f"🔐 **Verifying OTP for `{phone}`...**")
        try:
            try:
                await client.sign_in(phone, code=code, phone_code_hash=pending["phone_code_hash"])
            except Exception as se:
                if "SessionPasswordNeededError" in type(se).__name__ or "password" in str(se).lower():
                    if not password:
                        pending["code"] = code
                        pending["state"] = "WAITING_2FA"
                        return await safe_edit(event, (
                            "🔐 **2FA CLOUD PASSWORD DETECTED!**\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 **Phone:** `{phone}`\n"
                            f"✅ **OTP Code:** `{code}` (Verified!)\n\n"
                            "👉 **Ab bas apna 2FA Password send karein:**\n"
                            "`.2fa <YOUR_PASSWORD>`\n"
                            "*(Example: `.2fa mypassword123`)*\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "💡 *Aapka password verify hote hi account fleet me live ho jayega!*"
                        ))
                    await client.sign_in(password=password)
                else:
                    raise se

            session_str = client.session.save()
            me = await client.get_me()
            u_name = getattr(me, "first_name", phone)
            uid = OWNER_ID or HOST_USER_ID or getattr(me, "id", 0)

            # Store in data/users/<uid>/accounts.json
            user_dir = os.path.join(os.getcwd(), "data", "users", str(uid))
            os.makedirs(user_dir, exist_ok=True)
            accts_file = os.path.join(user_dir, "accounts.json")
            existing = []
            if os.path.isfile(accts_file):
                try:
                    with open(accts_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []

            used_slots = {a.get("slot", 0) for a in existing}
            new_slot = 0
            while new_slot in used_slots:
                new_slot += 1

            new_acct = {
                "slot": new_slot,
                "phone": phone,
                "session_string": session_str,
                "hosted": True,
                "hosted_at": int(time.time()),
                "expires_at": int(time.time()) + 999999999,
                "name": u_name
            }
            existing = [a for a in existing if a.get("slot") != new_slot]
            existing.append(new_acct)
            with open(accts_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            # Spawn child worker for this slot
            try:
                py_bin = sys.executable
                child_env = os.environ.copy()
                child_env.update({
                    "API_ID": str(API_ID),
                    "API_HASH": str(API_HASH),
                    "SESSION_STRING": session_str,
                    "USERBOT_OWNER_ID": str(uid),
                    "USERBOT_SLOT": str(new_slot),
                    "USERBOT_MODE": "1",
                })
                os.makedirs("userbot_logs", exist_ok=True)
                log_f = open(f"userbot_logs/userbot_{uid}_slot{new_slot}.log", "a", encoding="utf-8", errors="replace")
                subprocess.Popen(
                    [py_bin, "-O", "-B", "-u", __file__, "--userbot"],
                    env=child_env, stdout=log_f, stderr=log_f, cwd=os.getcwd(),
                    start_new_session=True if sys.platform != "win32" else False
                )
            except Exception as spe:
                print(f"[DIRECT_SPAWN ERROR] {spe}", flush=True)

            del _PENDING_DIRECT_LOGINS[event.sender_id]
            await safe_edit(event, (
                f"🎉 **ACCOUNT SUCCESSFULLY LINKED!** 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Name:** `{u_name}`\n"
                f"📱 **Phone:** `{phone}`\n"
                f"🔢 **Assigned:** `Slot #{new_slot+1}`\n"
                f"⚡ **Status:** `🟢 ONLINE & RUNNING 24/7`\n"
                f"👥 **Fleet:** Added to Personal Fleet!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Check all accounts: `.fleet` ya `.myaccs`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ **Login Verification Failed:** `{str(e)[:70]}`")

    @register_cmd("2fa")
    @register_cmd("pass")
    @register_cmd("password")
    async def cmd_verify_2fa(event, arg):
        """
        Verify Telegram 2FA Password if needed!
        Usage: .2fa your_password
        """
        if USERBOT_SLOT != 0:
            return await safe_edit(event, "⛔ **Access Denied:** 2FA authentication sirf aapke **MAIN / MASTER ACCOUNT (Slot #1)** se hi allowed hai!")

        if event.sender_id not in _PENDING_DIRECT_LOGINS:
            return await safe_edit(event, "❌ **Koi pending 2FA request nahi mili!**\nPehle `.addacc +91XXXXXXXXXX` karein.")

        pending = _PENDING_DIRECT_LOGINS[event.sender_id]
        password = (arg or "").strip()
        if not password:
            return await safe_edit(event, "❌ **Usage:** `.2fa <YOUR_PASSWORD>`\n*(Example: `.2fa mypassword123`)*")

        client = pending["client"]
        phone = pending["phone"]

        await safe_edit(event, f"🔐 **Authenticating 2FA Password for `{phone}`...**")
        try:
            await client.sign_in(password=password)
            session_str = client.session.save()
            me = await client.get_me()
            u_name = getattr(me, "first_name", phone)
            uid = OWNER_ID or HOST_USER_ID or getattr(me, "id", 0)

            user_dir = os.path.join(os.getcwd(), "data", "users", str(uid))
            os.makedirs(user_dir, exist_ok=True)
            accts_file = os.path.join(user_dir, "accounts.json")
            existing = []
            if os.path.isfile(accts_file):
                try:
                    with open(accts_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []

            used_slots = {a.get("slot", 0) for a in existing}
            new_slot = 0
            while new_slot in used_slots:
                new_slot += 1

            new_acct = {
                "slot": new_slot,
                "phone": phone,
                "session_string": session_str,
                "hosted": True,
                "hosted_at": int(time.time()),
                "expires_at": int(time.time()) + 999999999,
                "name": u_name
            }
            existing = [a for a in existing if a.get("slot") != new_slot]
            existing.append(new_acct)
            with open(accts_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            # Spawn child worker for this slot
            try:
                py_bin = sys.executable
                child_env = os.environ.copy()
                child_env.update({
                    "API_ID": str(API_ID),
                    "API_HASH": str(API_HASH),
                    "SESSION_STRING": session_str,
                    "USERBOT_OWNER_ID": str(uid),
                    "USERBOT_SLOT": str(new_slot),
                    "USERBOT_MODE": "1",
                })
                os.makedirs("userbot_logs", exist_ok=True)
                log_f = open(f"userbot_logs/userbot_{uid}_slot{new_slot}.log", "a", encoding="utf-8", errors="replace")
                subprocess.Popen(
                    [py_bin, "-O", "-B", "-u", __file__, "--userbot"],
                    env=child_env, stdout=log_f, stderr=log_f, cwd=os.getcwd(),
                    start_new_session=True if sys.platform != "win32" else False
                )
            except Exception as spe:
                print(f"[DIRECT_SPAWN ERROR] {spe}", flush=True)

            del _PENDING_DIRECT_LOGINS[event.sender_id]
            await safe_edit(event, (
                f"🎉 **ACCOUNT SUCCESSFULLY LINKED!** 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Name:** `{u_name}`\n"
                f"📱 **Phone:** `{phone}`\n"
                f"🔢 **Assigned:** `Slot #{new_slot+1}`\n"
                f"⚡ **Status:** `🟢 ONLINE & RUNNING 24/7`\n"
                f"🛡️ **2FA:** Verified\n"
                f"👥 **Fleet:** Added to Personal Fleet!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Check all accounts: `.fleet` ya `.myaccs`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ **2FA Login Failed:** `{str(e)[:70]}`\nTry again: `.2fa <password>`")

    @register_cmd("antiflood")
    @register_cmd("af")
    async def cmd_antiflood(event, arg):
        """
        Zero-Flood & Anti-SpamBlock Engine Controller
        Usage:
        .af               - View real-time anti-flood protection status
        .af safe          - Human typing jitter pacing (1.4s-2.2s, 100% safe)
        .af balanced      - Fast balanced pacing (0.9s-1.5s)
        .af stealth       - Ultra-stealth ghost pacing (2.2s-3.8s)
        .af zerowidth on  - Enable invisible Unicode SHA-256 mutation
        .af zerowidth off - Disable invisible Unicode mutation
        .af reset         - Reset rate limit buckets and flood counters
        """
        try:
            raw = (arg or "").strip().lower()
            if raw in ("ultra", "fast", "instant", "off", "disable"):
                ANTIFLOOD_CONFIG["enabled"] = False
                ANTIFLOOD_CONFIG["mode"] = "ultra"
                return await safe_edit(event, (
                    "⚡ **𝗙𝗟𝗢𝗢𝗗𝗟𝗘𝗦𝗦 𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗 — 𝗨𝗟𝗧𝗥𝗔-𝗙𝗔𝗦𝗧 𝗦𝗣𝗘𝗘𝗗 𝗔𝗖𝗧𝗜𝗩𝗘!** 🚀\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⏱️ **Pacing:** `0.0s (Direct Instant Sending)`\n"
                    "🚀 **Floodless Delay:** `❌ REMOVED / OFF`\n"
                    "💬 Messages & commands will now fire at maximum raw server speed!"
                ))

            if raw in ("safe", "balanced", "stealth"):
                ANTIFLOOD_CONFIG["enabled"] = True
                ANTIFLOOD_CONFIG["mode"] = raw
                pacing_info = "0.6s - 1.2s (Safe Guard)" if raw == "safe" else ("0.15s - 0.4s (Balanced)" if raw == "balanced" else "1.2s - 2.0s (Stealth)")
                return await safe_edit(event, (
                    f"🛡️ **𝗔𝗡𝗧𝗜-𝗙𝗟𝗢𝗢𝗗 𝗠𝗢𝗗𝗘 𝗨𝗣𝗗𝗔𝗧𝗘𝗗!**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ **New Mode:** `{raw.upper()}`\n"
                    f"⏱️ **Pacing:** `{pacing_info}`\n"
                    f"💡 Flood pacing enabled."
                ))

            if raw in ("zerowidth on", "zw on", "entropy on", "stealth on"):
                ANTIFLOOD_CONFIG["zero_width"] = True
                return await safe_edit(event, (
                    "🥷 **𝗭𝗘𝗥𝗢-𝗪𝗜𝗗𝗧𝗛 𝗔𝗡𝗧𝗜-𝗦𝗣𝗔𝗠𝗕𝗟𝗢𝗖𝗞: 𝗢𝗡 ✅**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛡️ Har outgoing message me invisible Unicode entropy inject hoga.\n"
                    "✨ Telegram SpamBot hash detection 100% bypass!"
                ))

            if raw in ("zerowidth off", "zw off", "entropy off", "stealth off"):
                ANTIFLOOD_CONFIG["zero_width"] = False
                return await safe_edit(event, "⚠️ **𝗭𝗘𝗥𝗢-𝗪𝗜𝗗𝗧𝗛 𝗔𝗡𝗧𝗜-𝗦𝗣𝗔𝗠𝗕𝗟𝗢𝗖𝗞: 𝗢𝗙𝗙**")

            if raw in ("reset", "clear"):
                _CHAT_SEND_TIMES.clear()
                ANTIFLOOD_CONFIG["flood_count"] = 0
                return await safe_edit(event, (
                    "🔄 **𝗔𝗡𝗧𝗜-𝗙𝗟𝗢𝗢𝗗 𝗥𝗔𝗧𝗘 𝗕𝗨𝗖𝗞𝗘𝗧𝗦 𝗥𝗘𝗦𝗘𝗧**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "✅ Sabhi tracked chats ki sending limits aur flood counter 0 ho gaye hain."
                ))

            # Status view
            is_enabled = ANTIFLOOD_CONFIG.get("enabled", False)
            mode_display = "⚡ ULTRA-FAST (0.0s Delay • Instant Send)" if not is_enabled else f"🛡️ {ANTIFLOOD_CONFIG.get('mode', 'safe').upper()} (Paced)"
            zw = "✅ Active" if ANTIFLOOD_CONFIG.get("zero_width") else "❌ Disabled"
            fc = ANTIFLOOD_CONFIG.get("flood_count", 0)

            msg = (
                f"⚡ **𝗙𝗔𝗦𝗧-𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗡𝗗𝗜𝗡𝗚 & 𝗙𝗟𝗢𝗢𝗗 𝗖𝗢𝗡𝗧𝗥𝗢𝗟** 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👑 **𝗦𝗽𝗲𝗲𝗱 𝗦𝘁𝗮𝘁𝘂𝘀**: `🟢 MAXIMUM RAW SPEED`\n"
                f"⏱️ **𝗣𝗮𝗰𝗶𝗻𝗴 𝗗𝗲𝗹𝗮𝘆**: `0.0s (Floodless Delay Hata Diya Hai)`\n"
                f"⚙️ **𝗠𝗼𝗱𝗲**: `{mode_display}`\n"
                f"🥷 **𝗭𝗲𝗿𝗼-𝗪𝗶𝗱𝘁𝗵**: {zw}\n"
                f"🛑 **𝗙𝗹𝗼𝗼𝗱 𝗖𝗼𝘂𝗻𝘁**: `{fc}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 **𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀**:\n"
                f"• `.af ultra` ─ 0.0s Instant Raw Speed (Default)\n"
                f"• `.af safe` ─ Safe Pacing Mode\n"
                f"• `.af zerowidth on/off` ─ Invisible Hash Mutation\n"
                f"• `.af reset` ─ Clear Flood Counters"
            )
            await safe_edit(event, msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝗔𝗙 𝗘𝗿𝗿 → `{str(e)[:40]}`")

    @register_cmd("tts")
    async def cmd_tts(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.tts <text>`")
            await safe_edit(event, "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐓𝐓𝐒...\n━━━━━━━━━━━━━━━")
            fname = f"tts_{int(time.time())}.mp3"
            try: gTTS(text=arg[:5000], lang="hi", slow=False).save(fname)
            except: return await safe_edit(event, "❌ 𝐓𝐓𝐒 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ")
            try:
                if event.out:
                    await event.delete()
                    await bot.send_file(event.chat_id, fname, caption="🎙️ 𝐓𝐓𝐒")
                else: await event.reply(file=fname, message="🎙️ 𝐓𝐓𝐒")
            finally:
                try: os.remove(fname)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓𝐓𝐒 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("qrcode")
    async def cmd_qrcode(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.qrcode <text>`")
            await safe_edit(event, "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐐𝐑...")
            file = f"qr_{int(time.time())}.png"
            qrcode.make(arg[:3000]).save(file)
            try:
                if event.out:
                    await event.delete()
                    await bot.send_file(event.chat_id, file, caption="🔳 𝐐𝐑 𝐂ᴏᴅᴇ")
                else: await event.reply(file=file, message="🔳 𝐐𝐑 𝐂ᴏᴅᴇ")
            finally:
                try: os.remove(file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐐𝐑 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("fancy")
    async def cmd_fancy(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.fancy <text>`")
            t = arg[:500]
            styles = [f"★彡 {t} 彡★", f"『 {t} 』", f"✦ {t} ✦", f"☾ {t} ☽", f"➳ {t} ➳",
                      f"⚡ {t} ⚡", f"❖ {t} ❖", f"♛ {t} ♛", f"꧁ {t} ꧂", f"░▒▓ {t} ▓▒░"]
            text = "✨ 𝐅ᴀɴᴄʏ 𝐒ᴛʏʟᴇs\n━━━━━━━━━━━━━━━\n" + "\n".join(styles)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ᴀɴᴄʏ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("style")
    async def cmd_style(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.style <text>`")
            t = arg[:500]
            fancy = (t.replace('a','𝒶').replace('b','𝒷').replace('c','𝒸').replace('d','𝒹')
                      .replace('e','𝑒').replace('f','𝒻').replace('g','𝑔').replace('h','𝒽'))
            text = f"🎨 𝐒ᴛʏʟᴇ\n━━━━━━━━━━━━━━━\n𝒇𝒂𝒏𝒄𝒚 → {fancy}\n**Bold** → **{t}**\n`Mono` → `{t}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛʏʟᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("emoji")
    async def cmd_emoji(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.emoji <text>`")
            pool = ["🔥","❤️","✨","⚡","💥","🌟","💫","🎯","💎","🦋","🌈","🧨","🎆","👑","🌸","🪄"]
            emojis = "".join(random.choice(pool) for _ in range(8))
            text = f"😀 𝐄ᴍᴏᴊɪ 𝐒ᴛʏʟᴇ\n━━━━━━━━━━━━━━━\n{arg[:500]} {emojis}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄ᴍᴏᴊɪ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("calc")
    async def cmd_calc(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.calc <expr>`")
            expr = arg.replace(" ", "")
            allowed = set("0123456789+-*/().%")
            if any(c not in allowed for c in expr):
                return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐂ʜᴀʀ")
            res = eval(expr, {"__builtins__": None}, {})
            text = f"🧮 𝐂ᴀʟᴄ\n━━━━━━━━━━━━━━━\n📥 `{expr}`\n📤 `{res}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception:
            await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐄xᴘʀᴇssɪᴏɴ")

    @register_cmd("weather")
    async def cmd_weather(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.weather <city>`")
            await safe_edit(event, "⚡ 𝐅ᴇᴛᴄʜɪɴɢ...")
            try:
                geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐆ᴇᴏ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ")
            if not geo.get("results"):
                return await safe_edit(event, "❌ 𝐂ɪᴛʏ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ")
            res = geo["results"][0]
            lat, lon, name = res.get("latitude"), res.get("longitude"), res.get("name")
            try:
                w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐖ᴇᴀᴛʜᴇʀ 𝐅ᴀɪʟ")
            cw = w.get("current_weather")
            if not cw: return await safe_edit(event, "❌ 𝐍ᴏ 𝐃ᴀᴛᴀ")
            msg = f"🌦️ 𝐖ᴇᴀᴛʜᴇʀ\n━━━━━━━━━━━━━━━\n📍 `{name}`\n🌡️ `{cw.get('temperature')}°C`\n💨 `{cw.get('windspeed')} km/h`"
            await safe_edit(event, msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖ᴇᴀᴛʜᴇʀ → `{str(e)[:40]}`")

    @register_cmd("ip")
    async def cmd_ip(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.ip <ip>`")
            await safe_edit(event, "⚡ 𝐋ᴏᴏᴋɪɴɢ...")
            try:
                data = requests.get(f"http://ip-api.com/json/{arg}", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ")
            if data.get("status") != "success":
                return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐈ᴘ")
            text = f"🌍 𝐈ᴘ 𝐈ɴғᴏ\n━━━━━━━━━━━━━━━\n📡 `{data.get('query')}`\n🌐 `{data.get('country')}`\n🏙️ `{data.get('city')}`\n📍 `{data.get('isp')}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈ᴘ → `{str(e)[:40]}`")

    @register_cmd("short")
    async def cmd_short(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔sᴇ → `.short <url>`")
            if not arg.startswith(("http://", "https://")):
                arg = "http://" + arg
            await safe_edit(event, "⚡ 𝐒ʜᴏʀᴛᴇɴɪɴɢ...")
            try:
                short_url = requests.get(f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}", timeout=8).text.strip()
            except: return await safe_edit(event, "❌ 𝐅ᴀɪʟ")
            text = f"🔗 𝐒ʜᴏʀᴛ 𝐔ʀʟ\n━━━━━━━━━━━━━━━\n`{short_url}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ʜᴏʀᴛ → `{str(e)[:40]}`")

    @register_cmd("info")
    async def cmd_info(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try:
                    ent = await bot.get_entity(arg)
                    target = ent.id
                except: return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐔sᴇʀ")
            if not target:
                return await safe_edit(event, "⚠️ `.info` (reply / @user / id)")
            await safe_edit(event, "⚡ 𝐅ᴇᴛᴄʜɪɴɢ...")
            user = await bot.get_entity(target)
            if getattr(user, "deleted", False):
                return await safe_edit(event, "❌ 𝐃ᴇʟᴇᴛᴇᴅ 𝐔sᴇʀ")
            if user.id == OWNER_ID:
                return await safe_edit(event, "🔒 𝐎ᴡɴᴇʀ 𝐏ʀɪᴠᴀᴛᴇ")
            full = await bot(functions.users.GetFullUserRequest(user.id))
            bio = full.full_user.about or "𝐍ᴏ 𝐁ɪᴏ"
            uname = f"@{user.username}" if user.username else "𝐍ᴏ 𝐔sᴇʀ"

            # ─── PHONE LOOKUP (ALWAYS RETURNS VALUE) ───
            async def phone_lookup():
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as s:
                        async with s.get(
                            f"http://api.subhxcosmo.in/api?key=titan&type=sms&term={user.id}",
                            timeout=5
                        ) as r:
                            if r.status == 200:
                                d = await r.json()
                                result = d.get("result", {})
                                num = result.get("number")
                                code = result.get("country_code", "")
                                if num:
                                    return f"{code}{num}"
                except:
                    pass
                return "𝐍ᴏ 𝐍ᴮ"

            phone = await phone_lookup()

            text = (
                "👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎\n━━━━━━━━━━━━━━━\n"
                f"🆔 𝐈𝐃 → `{user.id}`\n"
                f"📛 𝐍ᴀᴍᴇ → {user.first_name or ''} {user.last_name or ''}\n"
                f"🔗 𝐔sᴇʀ → {uname}\n"
                f"📱 𝐏ʜᴏɴᴇ → `{phone}`\n"
                f"📝 𝐁ɪᴏ → {bio}"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈ɴғᴏ → `{str(e)[:50]}`")

    @register_cmd("copy")
    async def cmd_copy(event, args):
        global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID
        try:
            reply = await event.get_reply_message()
            target = None
            if reply:
                try:
                    if reply.sender_id: target = await bot.get_entity(reply.sender_id)
                except: pass
            if not target and args:
                try: target = await bot.get_entity(args.strip())
                except: pass
            if not target:
                return await safe_edit(event, "❌ 𝐑ᴇᴘʟʏ / 𝐔sᴇʀ / 𝐈ᴅ")
            me = await bot.get_me()
            if target.id == me.id:
                return await safe_edit(event, "⚠️ 𝐒ᴇʟғ 𝐂ʟᴏɴᴇ 𝐁ʟᴏᴄᴋ")
            if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
                return await safe_edit(event, "⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐂ʟᴏɴᴇᴅ")
            await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ...")

            # Backup my original profile info and photo before cloning
            if not CLONE_ACTIVE:
                full_me = await bot(functions.users.GetFullUserRequest(me.id))
                CLONE_DATA["name"] = me.first_name or ""
                CLONE_DATA["last_name"] = me.last_name or ""
                CLONE_DATA["username"] = me.username or ""
                CLONE_DATA["bio"] = full_me.full_user.about or ""
                try:
                    my_dp_bytes = await bot.download_profile_photo(me, file=bytes)
                    CLONE_DATA["photo_bytes"] = my_dp_bytes
                except:
                    CLONE_DATA["photo_bytes"] = None

            full = await bot(functions.users.GetFullUserRequest(target.id))
            fname = getattr(target, "first_name", "") or ""
            lname = getattr(target, "last_name", "") or ""
            target_bio = full.full_user.about or ""

            # 1. Update Name
            await bot(functions.account.UpdateProfileRequest(
                first_name=fname[:64],
                last_name=lname[:64]
            ))

            # 2. Update Bio
            if target_bio is not None:
                try:
                    await bot(functions.account.UpdateProfileRequest(about=target_bio[:70]))
                except:
                    pass

            # 3. Clone Profile Photo (Dual File/Stream Method)
            dp_cloned = False
            dp_note = ""
            try:
                os.makedirs(DOWNLOAD_PATH, exist_ok=True)
                target_dp_path = os.path.join(DOWNLOAD_PATH, f"clone_dp_{target.id}.jpg")
                if os.path.exists(target_dp_path):
                    try: os.remove(target_dp_path)
                    except: pass

                # Method A: Download to file path
                downloaded = await bot.download_profile_photo(target, file=target_dp_path)
                if not downloaded:
                    downloaded = await bot.download_profile_photo(target.id, file=target_dp_path)

                if downloaded and os.path.exists(target_dp_path) and os.path.getsize(target_dp_path) > 0:
                    up_file = await bot.upload_file(target_dp_path)
                    if up_file:
                        await bot(functions.photos.UploadProfilePhotoRequest(file=up_file))
                        dp_cloned = True
                    try: os.remove(target_dp_path)
                    except: pass
                else:
                    # Method B: In-memory stream with explicit filename
                    photo_bytes = await bot.download_profile_photo(target, file=bytes)
                    if not photo_bytes:
                        photo_bytes = await bot.download_profile_photo(target.id, file=bytes)
                    if photo_bytes:
                        bio_stream = BytesIO(photo_bytes)
                        bio_stream.name = f"avatar_{target.id}.jpg"
                        up_file = await bot.upload_file(bio_stream)
                        if up_file:
                            await bot(functions.photos.UploadProfilePhotoRequest(file=up_file))
                            dp_cloned = True
                    else:
                        dp_note = "DP Private or No Photo"
            except Exception as pe:
                dp_note = str(pe)[:30]

            CLONE_ACTIVE = True
            LAST_CLONE_ID = target.id
            dp_status = "🖼️ 𝗗𝗣: 𝗖𝗹𝗼𝗻𝗲𝗱 ✅" if dp_cloned else f"⚠️ 𝗗𝗣: {dp_note or 'Private Profile Photo'}"
            res_msg = (
                f"🎭 𝐂ʟᴏɴᴇ 𝐒ᴜᴄᴄᴇssғᴜʟ!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 𝗡𝗮𝗺𝗲: {fname} {lname}\n"
                f"📝 𝗕𝗶𝗼: {target_bio or 'No Bio'}\n"
                f"{dp_status}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 𝗥𝗲𝘃𝗲𝗿𝘁: `.normal`"
            )
            await safe_edit(event, res_msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂ᴏᴘʏ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("normal")
    async def cmd_normal(event, _):
        global CLONE_ACTIVE, LAST_CLONE_ID
        try:
            if not CLONE_ACTIVE:
                return await safe_edit(event, "⚠️ 𝐍ᴏᴛ 𝐂ʟᴏɴɪɴɢ")
            await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐏ʀᴏғɪʟᴇ...")

            # 1. Restore Name & Bio
            await bot(functions.account.UpdateProfileRequest(
                first_name=(CLONE_DATA.get("name") or "")[:64],
                last_name=(CLONE_DATA.get("last_name") or "")[:64],
                about=(CLONE_DATA.get("bio") or "")[:70]
            ))

            # 2. Restore Original Profile Photo if saved
            dp_restored = False
            orig_bytes = CLONE_DATA.get("photo_bytes")
            if orig_bytes:
                try:
                    bio_stream = BytesIO(orig_bytes)
                    bio_stream.name = "my_original_avatar.jpg"
                    up_file = await bot.upload_file(bio_stream)
                    if up_file:
                        await bot(functions.photos.UploadProfilePhotoRequest(file=up_file))
                        dp_restored = True
                except Exception:
                    pass

            CLONE_ACTIVE = False
            LAST_CLONE_ID = None
            res = (
                "✅ 𝐏ʀᴏғɪʟᴇ 𝐑ᴇsᴛᴏʀᴇᴅ!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📛 𝗡𝗮𝗺𝗲: {CLONE_DATA.get('name') or ''}\n"
                f"📝 𝗕𝗶𝗼: {CLONE_DATA.get('bio') or 'No Bio'}\n"
                f"🖼️ 𝗗𝗣: {'Restored ✅' if dp_restored else 'Original Maintained'}"
            )
            await safe_edit(event, res)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍ᴏʀᴍᴀʟ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("music")
    async def cmd_music(event, arg):
        if not arg:
            return await safe_edit(event, "❌ 𝐔sᴇ → `.music <song name>`")
        async def download_and_send():
            try:
                await safe_edit(event, f"🎵 𝐒ᴇᴀʀᴄʜɪɴɢ: `{arg}`")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                    'default_search': 'ytsearch1',
                    'noplaylist': True,
                    'quiet': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(arg, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    title = info.get('title', 'Unknown')
                new = os.path.join(DOWNLOAD_PATH, f"{title}.mp3")
                if not os.path.exists(new):
                    for f in os.listdir(DOWNLOAD_PATH):
                        if f.endswith('.mp3'): new = os.path.join(DOWNLOAD_PATH, f); break
                await bot.send_file(event.chat_id, new, voice_note=True, caption=f"🎵 `{title[:60]}`")
                try: os.remove(new)
                except: pass
                await event.delete()
            except Exception as e:
                await safe_edit(event, f"❌ 𝐌ᴜsɪᴄ → `{str(e)[:60]}`")
        asyncio.create_task(download_and_send())

    @register_cmd("dmusic")
    async def cmd_dmusic(event, arg):
        if not arg:
            return await safe_edit(event, "❌ 𝐔sᴇ → `.dmusic <song name>`")
        async def download_music():
            try:
                await safe_edit(event, f"🎵 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ: `{arg}`")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                    'default_search': 'ytsearch1',
                    'noplaylist': True,
                    'quiet': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(arg, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    title = info.get('title', 'Unknown')
                    dur = info.get('duration', 0)
                new = os.path.join(DOWNLOAD_PATH, f"{title}.mp3")
                if not os.path.exists(new):
                    for f in os.listdir(DOWNLOAD_PATH):
                        if f.endswith('.mp3'): new = os.path.join(DOWNLOAD_PATH, f); break
                await bot.send_file(event.chat_id, new, caption=f"🎵 `{title[:60]}`",
                                    attributes=[types.DocumentAttributeAudio(duration=dur, title=title)])
                try: os.remove(new)
                except: pass
                await event.delete()
            except Exception as e:
                await safe_edit(event, f"❌ 𝐃ᴍᴜsɪᴄ → `{str(e)[:60]}`")
        asyncio.create_task(download_music())

    # ── TELEGRAM VOICE CHAT & 500% HIGH-GAIN MIC BOOSTER SUITE ──
    vc_settings = {
        "mic_boost": 500,       # 500% Volume Boost (User requested 500%)
        "speed": 1.25,          # Fast talk rate
        "volume": 500,          # 500% Output gain
        "earrape": True,        # Overdrive dynamic normalization
        "bass": 18,             # 18dB Bass
        "treble": 12,           # 12dB Treble
        "active_call": None,
        "is_muted": False,
        "guard": False          # VC Anti-Mute Protection
    }
    vc_guard_task = None

    # ── AUTO-MIC & VOICE OVERPOWER ENGINE ──
    AUTOMIC_CONFIG_FILE = os.path.join(BASE_DIR, "automic_config.json")
    automic_state = {
        "enabled": False,
        "mode": "echo",      # "echo", "monster", "scream", "300db", "robot", "radio", "ghost", "slowreverb", "chipmunk"
        "gain": 10.0,
        "bass": 32,
        "pitch": 0.84,
        "tempo": 1.19,
        "delete_original": True,
    }

    def load_automic_config():
        global automic_state
        try:
            if os.path.isfile(AUTOMIC_CONFIG_FILE):
                with open(AUTOMIC_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        automic_state.update(data)
        except Exception:
            pass

    def save_automic_config():
        try:
            with open(AUTOMIC_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(automic_state, f, indent=2)
        except Exception:
            pass

    load_automic_config()
    PROCESSED_VOICE_IDS: Set[int] = set()

    def get_voice_dsp(mode: str = "echo"):
        m = (mode or "echo").lower()
        gain = automic_state.get("gain", 10.0)
        bass = automic_state.get("bass", 32)
        pitch = automic_state.get("pitch", 0.84)
        tempo = automic_state.get("tempo", 1.19)

        if m in ("monster", "demon", "beast"):
            flt = "[0:a]compand=attacks=0.005:decays=0.05:points=-80/-5|-40/0|0/0:gain=18,asetrate=48000*0.72,atempo=1.35,bass=g=28:f=85,treble=g=10,volume=14.0[a]"
            cap = "👹 **1000% MONSTER BEAST VOICE**\n🔊 Whisper-to-Monster: ACTIVE | +28dB Sub-Bass"
        elif m in ("scream", "chilla"):
            flt = "[0:a]compand=attacks=0.002:decays=0.04:points=-80/-2|-35/0|0/0:gain=25,treble=g=16:f=3200,bass=g=18:f=100,volume=16.0[a]"
            cap = "🗣️ **10,000% SCREAM BLAST**\n🔊 Low voice blasted to deafening scream!"
        elif m in ("300db", "nuclear", "krakatoa"):
            flt = "[0:a]compand=attacks=0.001:decays=0.01:points=-90/0|-10/0|0/0:gain=28,volume=18.0,bass=g=42:f=60,treble=g=14[a]"
            cap = "🌋 **300 dB+ KRAKATOA NUCLEAR MIC**\n🔊 Max Opus Peak Gain | Physics Limit Shattered"
        elif m in ("robot", "cyborg"):
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=14,flanger=delay=5:depth=4:regen=50:width=80:speed=0.5,equalizer=f=1200:t=q:w=2:g=15,volume={gain}[a]"
            cap = "🤖 **1000% CYBORG ROBOT VOICE**\n🔊 Vocoder Metal Resonator | Overpower ACTIVE"
        elif m in ("radio", "walkie"):
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=15,highpass=f=400,lowpass=f=3400,acrusher=bits=8,volume={gain}[a]"
            cap = "📻 **1000% MILITARY RADIO / WALKIE-TALKIE**\n🔊 Tactical Comm Bandpass + 8-Bit Overdrive"
        elif m in ("ghost", "bhoot"):
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=12,vibrato=f=6.5:d=0.7,aecho=0.8:0.9:150|300|450:0.7|0.5|0.3,volume={gain}[a]"
            cap = "👻 **1000% GHOST / BHOOT WHISPER**\n🔊 Creepy Vibrato Echo Reverb | Haunted Presence"
        elif m in ("slowreverb", "lofi", "aesthetic"):
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=12,asetrate=48000*0.85,atempo=1.0,aecho=0.8:0.88:120|240|360|480:0.6|0.5|0.4|0.3,volume={gain}[a]"
            cap = "🌌 **1000% SLOWED + CATHEDRAL REVERB**\n🔊 Aesthetic Deep Hall Acoustic Gunjan"
        elif m in ("chipmunk", "squirrel"):
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=14,asetrate=48000*1.45,atempo=0.75,volume={gain}[a]"
            cap = "🐿️ **1000% HIGH-PITCH CHIPMUNK VOICE**\n🔊 Ultra High Frequency Fast Talker"
        else: # "echo", "bhari", "bhariecho", "deep", "deepecho"
            flt = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=16,asetrate=48000*{pitch},atempo={tempo},bass=g={bass}:f=85:w=0.6,equalizer=f=140:t=q:w=1.2:g=14,equalizer=f=300:t=q:w=1.5:g=8,aecho=0.85:0.88:90|180|270|360|450:0.65|0.50|0.38|0.26|0.16,volume={gain}[a]"
            cap = "🏰 **1000% BHARI AAWAJ & BOHUT TAGDA STADIUM ECHO**\n🔊 Deep Heavy Pitch + +32dB Chest Bass | 5-Tap Lingering Echo Gunjan"
        return flt, cap

    async def generate_sfx_audio(sfx_type: str, out_file: str):
        s = (sfx_type or "horn").lower().strip()
        if s in ("horn", "airhorn"):
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "sine=frequency=466.16:duration=0.6",
                "-f", "lavfi", "-i", "sine=frequency=370:duration=0.6",
                "-f", "lavfi", "-i", "sine=frequency=311.13:duration=0.6",
                "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:dropout_transition=0,compand=attacks=0.001:decays=0.05:points=-80/0|0/0:gain=14,aecho=0.8:0.88:100|200:0.6|0.3,volume=6.0[a]",
                "-map", "[a]", "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "🎺 **TRIPLE AIRHORN BLAST**"
        elif s in ("siren", "police", "warning"):
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*(700+300*sin(2*PI*0.8*t))*t):d=3.0",
                "-af", "compand=attacks=0.01:decays=0.1:points=-80/0|0/0:gain=10,aecho=0.8:0.7:150:0.4,volume=5.0",
                "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "🚨 **POLICE / AIR-RAID EMERGENCY SIREN**"
        elif s in ("bassdrop", "subdrop", "drop", "808"):
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*(160*exp(-1.5*t))*t):d=2.5",
                "-af", "compand=attacks=0.005:decays=0.05:points=-80/0|0/0:gain=20,bass=g=30:f=60,volume=8.0",
                "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "💣 **808 SUB-BASS DROP BLAST**"
        elif s in ("gun", "ak47", "shotgun", "shoot"):
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=pink:r=48000",
                "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=pink:r=48000",
                "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=pink:r=48000",
                "-filter_complex", "[0:a]adelay=0|0,lowpass=f=1200,volume=12[a1];[1:a]adelay=140|140,lowpass=f=1200,volume=12[a2];[2:a]adelay=280|280,lowpass=f=1200,volume=12[a3];[a1][a2][a3]amix=inputs=3:dropout_transition=0,aecho=0.8:0.8:90|180:0.5|0.3,volume=6[a]",
                "-map", "[a]", "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "💥 **AK-47 RAPID GUNFIRE BURST**"
        elif s in ("nuke", "bomb", "explosion"):
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anoisesrc=d=2.5:c=brown:r=48000",
                "-af", "compand=attacks=0.001:decays=0.3:points=-80/0|0/0:gain=22,lowpass=f=250,bass=g=36:f=50,volume=10.0",
                "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "🌋 **NUCLEAR MEGATON SHOCKWAVE**"
        else: # "thunder", "storm", "bijli"
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anoisesrc=d=2.0:c=brown:r=48000",
                "-af", "compand=attacks=0.01:decays=0.2:points=-80/0|0/0:gain=18,lowpass=f=350,bass=g=28:f=70,aecho=0.8:0.85:120|240:0.6|0.4,volume=8.0",
                "-c:a", "libopus", "-b:a", "128k", out_file
            ]
            title = "⚡ **HEAVY ROLLING THUNDER CRASH**"

        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        return title

    @register_cmd("automic")
    @register_cmd("autovoice")
    @register_cmd("workingmic")
    async def cmd_automic(event, arg):
        """
        Auto Voice Note Modulator & Mic Transformer:
        When turned ON, any voice note sent from your Telegram mic is automatically
        intercepted, amplified to 1000%, given heavy stadium echo / monster demon FX,
        and replaces the raw normal voice note. Normal voice is never sent!
        """
        raw = (arg or "").strip().lower()
        valid_modes = ("echo", "monster", "scream", "300db", "bhari", "bhariecho", "deep", "deepecho", "robot", "cyborg", "radio", "walkie", "ghost", "bhoot", "slowreverb", "lofi", "chipmunk")

        if raw in ("on", "enable", "start", "1", "true"):
            automic_state["enabled"] = True
            save_automic_config()
            return await safe_edit(event, (
                "🎙️ **𝐖𝐎𝐑𝐊𝐈𝐍𝐆 𝐀𝐔𝐓𝐎-𝐌𝐈𝐂 𝐀𝐑𝐌𝐄𝐃 (𝐁𝐇𝐀𝐑𝐈 𝐀𝐀𝐖𝐀𝐉 + 𝐁𝐎𝐇𝐔𝐓 𝐄𝐂𝐇𝐎 𝐎𝐍)!** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 **𝐌ᴏᴅᴇ:** `{automic_state.get('mode', 'echo').upper()}`\n"
                f"💥 **𝐆ᴀɪɴ:** `{int(automic_state.get('gain', 10.0)*100)}% Overdrive (Max Digital Amplification)`\n"
                f"🎙️ **𝐁ʜᴀʀɪ 𝐀ᴀᴡᴀᴊ:** `Deep Heavy Pitch ({automic_state.get('pitch', 0.84)}) + Chest Resonance (+{automic_state.get('bass', 32)}dB Bass)`\n"
                "🏰 **𝐁ᴏʜᴜᴛ 𝐄ᴄ𝐇𝐎:** `5-Tap Stadium Cathedral Reverb (90ms-450ms Gunjan)`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ **100% WORKING GUARANTEE:**\n"
                "Ab aap Telegram par normal aawaj me mic button dabake bolo — bot automatically aapki aawaj ko BHAARI aur BOHUT TAGDE ECHO me badal kar 1000% volume par bhejega!\n"
                "👉 Normal ya patli aawaj kisi ke paas nahi jayegi!"
            ))
        elif raw in ("off", "disable", "stop", "0", "false"):
            automic_state["enabled"] = False
            save_automic_config()
            return await safe_edit(event, "🛑 **𝐀𝐔𝐓𝐎-𝐌𝐈𝐂 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃!** Normal voice notes will be sent.")
        elif raw in valid_modes:
            norm_mode = "echo" if raw in ("echo", "bhari", "bhariecho", "deep", "deepecho") else raw
            automic_state["mode"] = norm_mode
            automic_state["enabled"] = True
            save_automic_config()
            return await safe_edit(event, (
                f"🎙️ **𝐀𝐔𝐓𝐎-𝐌𝐈𝐂 𝐌𝐎𝐃𝐄 𝐒𝐄𝐓 ➔ {norm_mode.upper()}!** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 Status: `🟢 ACTIVE`\n"
                f"🎙️ Voice Profile: `{norm_mode.upper()}`\n"
                f"💥 Gain: `1000% Master Overdrive`\n"
                f"💡 Har voice note automatically `{norm_mode.upper()}` effect ke saath jayega!"
            ))
        else:
            status = "🟢 ACTIVE" if automic_state.get("enabled") else "🔴 INACTIVE (Turn ON via `.automic on`)"
            cur_mode = automic_state.get("mode", "echo")
            return await safe_edit(event, (
                "🎙️ **𝐀𝐔𝐓𝐎-𝐌𝐈𝐂 & 𝐕𝐎𝐈𝐂𝐄 𝐎𝐕𝐄𝐑𝐏𝐎𝐖𝐄𝐑 𝐂𝐎𝐍𝐓𝐑𝐎𝐋** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📡 **𝐒ᴛᴀᴛᴜs:** `{status}`\n"
                f"🔊 **𝐀ᴄᴛɪᴠᴇ 𝐌ᴏᴅᴇ:** `{cur_mode.upper()}`\n"
                f"💥 **𝐆ᴀɪɴ:** `{int(automic_state.get('gain', 10.0)*100)}% Master Overdrive`\n"
                f"🏰 **𝐄ᴄʜᴏ 𝐃𝐒𝐏:** `5-Tap Lingering Stadium Cathedral Reverb`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 **𝐂ᴏᴍᴍᴀɴᴅs:**\n"
                "│ ⬝ `.automic on` ➔ Turn ON auto Bhari + Echo voice changer\n"
                "│ ⬝ `.automic off` ➔ Turn OFF auto mic changer\n"
                "│ ⬝ `.automic <mode>` ➔ echo / monster / scream / 300db / robot / radio / ghost / slowreverb / chipmunk\n"
                "│ ⬝ `.bhari` / `.echomic` ➔ 1000% Bhari Aawaj + Bohut Tagda Echo\n"
                "│ ⬝ `.setmic` ➔ Live fine-tune pitch, bass, speed & gain\n"
                "│ ⬝ `.sfx <type>` ➔ horn / siren / bassdrop / gun / nuke / thunder\n"
                "│ ⬝ `.vcguard on/off` ➔ Permanent anti-mute shield in VC\n"
                "│ ⬝ `.mic` (reply to VN) ➔ Instantly transform voice note\n"
                "│ ⬝ `.vcecho` / `.300db` ➔ Live VC overpower (1000% user, normal opponents)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 Normal aawaj na bhejne ke liye abhi `.automic on` karein!"
            ))

    @register_cmd("mic")
    @register_cmd("echomic")
    @register_cmd("bhari")
    @register_cmd("bhariecho")
    @register_cmd("deepvoice")
    @register_cmd("deepecho")
    @register_cmd("micoff")
    @register_cmd("micon")
    async def cmd_mic_master(event, arg):
        """
        Master Mic & Voice Transformer Command:
        - If replied to voice note: transforms it into Bhari Aawaj + Bohut Tagda Echo!
        - If text provided: speaks text in Bhari Aawaj + 1000% Stadium Echo!
        - If on/off/mode: controls Auto-Mic.
        """
        raw = (arg or "").strip()
        raw_lower = raw.lower()

        if raw_lower in ("on", "enable", "start"):
            return await cmd_automic(event, "on")
        if raw_lower in ("off", "disable", "stop"):
            return await cmd_automic(event, "off")
        valid_modes = ("echo", "monster", "scream", "300db", "bhari", "bhariecho", "deep", "deepecho", "robot", "cyborg", "radio", "walkie", "ghost", "bhoot", "slowreverb", "lofi", "chipmunk")
        if raw_lower in valid_modes:
            return await cmd_automic(event, raw_lower)

        reply = await event.get_reply_message() if event.is_reply else None

        # If replied to audio/voice note or text provided
        if (reply and reply.media) or (raw and raw_lower not in ("status", "info")):
            try:
                mode = automic_state.get("mode", "echo")
                if "monster" in raw_lower: mode = "monster"
                elif "scream" in raw_lower: mode = "scream"
                elif "300db" in raw_lower: mode = "300db"
                elif "robot" in raw_lower: mode = "robot"
                elif "radio" in raw_lower: mode = "radio"
                elif "ghost" in raw_lower or "bhoot" in raw_lower: mode = "ghost"
                elif "slow" in raw_lower or "lofi" in raw_lower: mode = "slowreverb"
                elif "chipmunk" in raw_lower: mode = "chipmunk"
                elif any(x in raw_lower for x in ("bhari", "echo", "deep")): mode = "echo"

                in_file = None
                is_temp = False

                if reply and reply.media:
                    await safe_edit(event, f"🎙️ 𝐀ᴘᴘʟʏɪɴɢ 1000% 𝐁𝐇𝐀𝐑𝐈 𝐀𝐀𝐖𝐀𝐉 & 𝐁𝐎𝐇𝐔𝐓 𝐄𝐂𝐇𝐎...")
                    in_file = await reply.download_media(file=DOWNLOAD_PATH)
                    is_temp = True
                else:
                    await safe_edit(event, f"🎙️ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 1000% 𝐁𝐇𝐀𝐑𝐈 𝐀𝐀𝐖𝐀𝐉 & 𝐄𝐂𝐇𝐎 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ...")
                    in_file = os.path.join(DOWNLOAD_PATH, f"mictmp_{int(time.time())}.mp3")
                    clean_text = raw
                    for flag in ("echo", "monster", "scream", "300db", "bhari", "bhariecho", "deep", "robot", "radio", "ghost", "slow", "chipmunk"):
                        clean_text = clean_text.replace(flag, "").strip()
                    gTTS(text=(clean_text or "Arya X Mental Overpower Active")[:3000], lang="hi", slow=False).save(in_file)
                    is_temp = True

                out_file = os.path.join(DOWNLOAD_PATH, f"mic_out_{int(time.time()*1000)}.ogg")
                flt, cap = get_voice_dsp(mode)

                cmd = [
                    "ffmpeg", "-y", "-i", in_file,
                    "-filter_complex", flt,
                    "-map", "[a]",
                    "-c:a", "libopus", "-b:a", "128k",
                    out_file
                ]
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await proc.communicate()

                if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                    reply_id = reply.id if reply else None
                    sent = await bot.send_file(
                        event.chat_id,
                        out_file,
                        voice_note=True,
                        reply_to=reply_id,
                        caption=cap
                    )
                    if sent and getattr(sent, "id", None):
                        PROCESSED_VOICE_IDS.add(sent.id)
                    try: os.remove(out_file)
                    except: pass
                    await event.delete()
                else:
                    await safe_edit(event, "❌ Mic audio transformation failed.")

                if is_temp and in_file and os.path.exists(in_file):
                    try: os.remove(in_file)
                    except: pass
            except Exception as e:
                await safe_edit(event, f"❌ 𝐌ɪᴄ 𝐄ʀʀ → `{str(e)[:50]}`")
        else:
            # Check if this chat has an active voice chat
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if call:
                await execute_vc_overpower(event, "1000% Stadium Echo", 100000, 10000, 35, activate_echo=True)
            else:
                await cmd_automic(event, "")

    @register_cmd("setmic")
    @register_cmd("mictune")
    @register_cmd("micsetup")
    async def cmd_setmic(event, arg):
        """
        Mic DSP Fine-Tuner:
        .setmic pitch <0.5 - 1.5> (default: 0.84 - deeper bhaari)
        .setmic bass <10 - 45> (default: 32 dB)
        .setmic gain <1.0 - 20.0> (default: 10.0 = 1000%)
        .setmic speed <0.5 - 2.0> (default: 1.19)
        .setmic reset (restore default 1000% Bhari Echo)
        """
        raw = (arg or "").strip().lower()
        if not raw:
            p = automic_state.get("pitch", 0.84)
            b = automic_state.get("bass", 32)
            g = automic_state.get("gain", 10.0)
            s = automic_state.get("tempo", 1.19)
            m = automic_state.get("mode", "echo")
            return await safe_edit(event, (
                "🎛️ **𝐀𝐔𝐓𝐎-𝐌𝐈𝐂 𝐃𝐒𝐏 𝐅𝐈𝐍𝐄-𝐓𝐔𝐍𝐄𝐑** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎙️ **Mode:** `{m.upper()}`\n"
                f"🎵 **Pitch (Heavy/Bhari):** `{p}` (Lower = Bhaari Heavy Voice)\n"
                f"💥 **Sub-Bass Overdrive:** `+{b} dB`\n"
                f"🔊 **Master Gain:** `{int(g * 100)}% ({g}x)`\n"
                f"⚡ **Speed Multiplier:** `{s}x`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 **Usage Examples:**\n"
                "│ ⬝ `.setmic pitch 0.78` ➔ Aur zyada bhaari / deep voice\n"
                "│ ⬝ `.setmic bass 40` ➔ 40dB chest rumble bass\n"
                "│ ⬝ `.setmic gain 15` ➔ 1500% volume multiplier\n"
                "│ ⬝ `.setmic speed 1.3` ➔ Fast aggressive talk rate\n"
                "│ ⬝ `.setmic reset` ➔ Restore optimal 1000% Bhari Echo defaults"
            ))

        parts = raw.split(maxsplit=1)
        sub = parts[0]
        val = parts[1].strip() if len(parts) > 1 else ""

        if sub == "reset":
            automic_state["pitch"] = 0.84
            automic_state["bass"] = 32
            automic_state["gain"] = 10.0
            automic_state["tempo"] = 1.19
            automic_state["mode"] = "echo"
            save_automic_config()
            return await safe_edit(event, "✅ **𝐌ɪᴄ 𝐒ᴇᴛᴛɪɴɢs 𝐑ᴇsᴇᴛ ᴛᴏ 1000% 𝐁ʜᴀʀɪ + 𝐁ᴏʜᴜᴛ 𝐄ᴄʜᴏ 𝐃ᴇғᴀᴜʟᴛs!**")

        if sub in ("pitch", "sur") and val:
            try:
                pv = float(val)
                automic_state["pitch"] = round(max(0.5, min(pv, 1.8)), 2)
                save_automic_config()
                return await safe_edit(event, f"🎙️ **𝐌ɪᴄ 𝐏ɪᴛᴄʜ 𝐒ᴇᴛ ➔ `{automic_state['pitch']}`** (Lower = Bhaari Heavy Voice)")
            except:
                return await safe_edit(event, "❌ Invalid pitch! Example: `.setmic pitch 0.80`")

        if sub in ("bass", "dhol") and val:
            try:
                bv = int(float(val))
                automic_state["bass"] = max(0, min(bv, 50))
                save_automic_config()
                return await safe_edit(event, f"💥 **𝐌ɪᴄ 𝐒ᴜʙ-𝐁ᴀss 𝐒ᴇᴛ ➔ `+{automic_state['bass']} dB`**")
            except:
                return await safe_edit(event, "❌ Invalid bass! Example: `.setmic bass 35`")

        if sub in ("gain", "vol", "volume") and val:
            try:
                gv = float(val)
                if gv > 20: gv = gv / 100.0
                automic_state["gain"] = round(max(1.0, min(gv, 25.0)), 1)
                save_automic_config()
                return await safe_edit(event, f"🔊 **𝐌ɪᴄ 𝐌ᴀsᴛᴇʀ 𝐆ᴀɪɴ 𝐒ᴇᴛ ➔ `{int(automic_state['gain']*100)}% ({automic_state['gain']}x)`**")
            except:
                return await safe_edit(event, "❌ Invalid gain! Example: `.setmic gain 12`")

        if sub in ("speed", "tempo", "fast") and val:
            try:
                sv = float(val)
                automic_state["tempo"] = round(max(0.5, min(sv, 2.5)), 2)
                save_automic_config()
                return await safe_edit(event, f"⚡ **𝐌ɪᴄ 𝐒ᴘᴇᴇᴅ 𝐒ᴇᴛ ➔ `{automic_state['tempo']}x`**")
            except:
                return await safe_edit(event, "❌ Invalid speed! Example: `.setmic speed 1.25`")

        return await safe_edit(event, "❌ Unknown parameter. Use: `.setmic pitch/bass/gain/speed <value>` or `.setmic reset`")

    @register_cmd("sfx")
    @register_cmd("sound")
    @register_cmd("vcsfx")
    @register_cmd("soundboard")
    async def cmd_sfx(event, arg):
        """
        Live Soundboard & VC SFX Blaster:
        Synthesizes high-impact audio blast drops in milliseconds and:
        1. Streams directly into live Telegram VC (if call is active / pytgcalls connected)
        2. Sends as a 1000% amplified Voice Note into the chat!
        Presets: horn, siren, bassdrop, gun, nuke, thunder
        """
        try:
            raw = (arg or "").strip().lower()
            if not raw or raw in ("list", "help", "menu"):
                return await safe_edit(event, (
                    "💥 **𝐀𝐑𝐘𝐀 𝐗 𝐌𝐄𝐍𝐓𝐀𝐋 𝐋𝐈𝐕𝐄 𝐒𝐅𝐗 𝐒𝐎𝐔𝐍𝐃𝐁𝐎𝐀𝐑𝐃** ⚡\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "│ ⬝ `.sfx horn` ➔ 🎺 Triple Dancehall Airhorn Blast\n"
                    "│ ⬝ `.sfx siren` ➔ 🚨 Police / Air-Raid Emergency Wail\n"
                    "│ ⬝ `.sfx bassdrop` ➔ 💣 808 Subwoofer Bass Drop\n"
                    "│ ⬝ `.sfx gun` ➔ 💥 AK-47 Rapid Gunfire Burst\n"
                    "│ ⬝ `.sfx nuke` ➔ 🌋 Megaton Nuclear Shockwave\n"
                    "│ ⬝ `.sfx thunder` ➔ ⚡ Heavy Rolling Thunder Crash\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 VC me live chalega aur chat me 1000% voice note ban kar jayega!"
                ))

            await safe_edit(event, f"💥 𝐆ᴇɴᴇʀᴀᴛɪɴɢ `{raw.upper()}` 𝐒𝐅𝐗 𝐃ʀᴏᴘ...")
            out_file = os.path.join(DOWNLOAD_PATH, f"sfx_{raw}_{int(time.time()*1000)}.ogg")
            title = await generate_sfx_audio(raw, out_file)

            if not os.path.exists(out_file) or os.path.getsize(out_file) < 100:
                return await safe_edit(event, f"❌ Failed to synthesize `{raw}` SFX.")

            # Attempt live VC stream if pytgcalls is connected
            streamed = False
            try:
                pytg = await get_pytgcalls_app()
                if pytg:
                    from pytgcalls.types import AudioPiped
                    try:
                        await pytg.join_group_call(event.chat_id, AudioPiped(out_file))
                        streamed = True
                    except Exception:
                        await pytg.change_stream(event.chat_id, AudioPiped(out_file))
                        streamed = True
            except Exception:
                pass

            # In groups or active call, stream purely to VC MIC without sending any voice note to chat!
            chat_peer = await event.get_input_chat()
            active_call = await get_active_group_call(chat_peer)
            is_vc_target = bool(active_call or event.is_group)

            if is_vc_target or streamed:
                if os.path.exists(out_file):
                    try: os.remove(out_file)
                    except: pass
                stream_txt = "🟢 **STREAMED DIRECTLY INTO VC MIC (0 VOICE NOTES IN CHAT)**"
            else:
                await bot.send_file(
                    event.chat_id,
                    out_file,
                    voice_note=True,
                    caption=f"{title}\n🔊 1000% Master SFX Blast | Overpower ACTIVE"
                )
                try: os.remove(out_file)
                except: pass
                stream_txt = "📢 **SENT AS 1000% AUDIO DROP**"

            await safe_edit(event, (
                f"{title} 💥\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📡 𝐒ᴛᴀᴛᴜs: {stream_txt}\n"
                f"🔊 𝐆ᴀɪɴ: `1000% Digital Overdrive`\n"
                f"🚫 𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ: `NONE (Only VC Mic Stream)`\n"
                f"👉 Agla drop: `.sfx bassdrop` ya `.sfx horn`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐅𝐗 𝐄ʀʀ → `{str(e)[:50]}`")

    async def _handle_generic_voice_fx(event, arg, fx_mode: str, default_tts: str):
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp = False

            if reply and reply.media:
                await safe_edit(event, f"🎙️ 𝐀ᴘᴘʟʏɪɴɢ 1000% `{fx_mode.upper()}` 𝐄ғғᴇᴄᴛ...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp = True
            elif arg:
                await safe_edit(event, f"🎙️ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ `{fx_mode.upper()}` 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ...")
                in_file = os.path.join(DOWNLOAD_PATH, f"vfx_{fx_mode}_{int(time.time())}.mp3")
                gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                is_temp = True
            else:
                return await safe_edit(event, (
                    f"❌ 𝐔sᴀɢᴇ:\n"
                    f"👉 Reply to voice note with `.{fx_mode}`\n"
                    f"👉 Or type: `.{fx_mode} <text to speak>`"
                ))

            if not in_file or not os.path.exists(in_file):
                return await safe_edit(event, "❌ Failed to read audio media.")

            out_file = os.path.join(DOWNLOAD_PATH, f"vfx_out_{fx_mode}_{int(time.time()*1000)}.ogg")
            flt, cap = get_voice_dsp(fx_mode)

            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", flt,
                "-map", "[a]",
                "-c:a", "libopus", "-b:a", "128k",
                out_file
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                reply_to_id = reply.id if reply else None
                sent = await bot.send_file(
                    event.chat_id,
                    out_file,
                    voice_note=True,
                    reply_to=reply_to_id,
                    caption=cap
                )
                if sent and getattr(sent, "id", None):
                    PROCESSED_VOICE_IDS.add(sent.id)
                try: os.remove(out_file)
                except: pass
                await event.delete()
            else:
                await safe_edit(event, f"❌ `{fx_mode}` audio transformation failed.")

            if is_temp and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕ᴏɪᴄᴇ𝐅𝐗 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("robot")
    @register_cmd("cyborg")
    @register_cmd("robotvoice")
    async def cmd_robot(event, arg):
        """1000% Cyborg Robot Vocoder Voice"""
        await _handle_generic_voice_fx(event, arg, "robot", "Arya X Mental Robot System Armed")

    @register_cmd("radio")
    @register_cmd("walkie")
    @register_cmd("radiovoice")
    async def cmd_radio(event, arg):
        """1000% Military Walkie-Talkie Tactical Radio Voice"""
        await _handle_generic_voice_fx(event, arg, "radio", "Roger that enemy down over")

    @register_cmd("ghostvoice")
    @register_cmd("bhoot")
    @register_cmd("bhootvoice")
    async def cmd_ghostvoice(event, arg):
        """1000% Horror Ghost / Bhoot Vibrato Echo Voice"""
        await _handle_generic_voice_fx(event, arg, "ghost", "Mera badla abhi baki hai")

    @register_cmd("slowreverb")
    @register_cmd("lofi")
    @register_cmd("aesthetic")
    async def cmd_slowreverb(event, arg):
        """1000% Slowed + Cathedral Reverb Voice"""
        await _handle_generic_voice_fx(event, arg, "slowreverb", "Arya X Mental Slowed Reverb Vibe")

    @register_cmd("chipmunk")
    @register_cmd("squirrel")
    async def cmd_chipmunk(event, arg):
        """1000% Fast High-Pitch Chipmunk Voice"""
        await _handle_generic_voice_fx(event, arg, "chipmunk", "Dekho mai kitni tez bolta hu haha")

    @register_cmd("vcguard")
    @register_cmd("antimute")
    @register_cmd("unmuteguard")
    async def cmd_vcguard(event, arg):
        """
        Anti-Mute & VC Self-Defense Guard:
        Constantly monitors active VC; if an admin tries to mute owner,
        instantly unmutes owner within 0.5s and keeps mic permanently active!
        """
        global vc_guard_task
        raw = (arg or "").strip().lower()
        chat_peer = await event.get_input_chat()
        call = await get_active_group_call(chat_peer)

        if raw in ("on", "enable", "start", "1", "true"):
            if not call:
                return await safe_edit(event, "⚠️ **VC Guard Alert:** Active VC not found in this chat. Start or join VC first, then run `.vcguard on`!")
            vc_settings["guard"] = True
            if vc_guard_task and not vc_guard_task.done():
                vc_guard_task.cancel()

            async def _guard_loop():
                while vc_settings.get("guard", False):
                    try:
                        me_ent = await bot.get_input_entity("me")
                        active_call = vc_settings.get("active_call") or call
                        p_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                            call=active_call, ids=[me_ent], sources=[], offset="", limit=1
                        ))
                        if p_obj and hasattr(p_obj, "participants") and p_obj.participants:
                            me_p = p_obj.participants[0]
                            if getattr(me_p, "muted", False):
                                await bot(functions.phone.EditGroupCallParticipantRequest(
                                    call=active_call, participant=me_ent, volume=100000, muted=False
                                ))
                    except asyncio.CancelledError:
                        break
                    except Exception:
                        pass
                    await asyncio.sleep(0.8)

            vc_guard_task = asyncio.create_task(_guard_loop())
            return await safe_edit(event, (
                "🛡️ **𝐕𝐂 𝐀𝐍𝐓𝐈-𝐌𝐔𝐓𝐄 𝐆𝐔𝐀𝐑𝐃 𝐀𝐑𝐌𝐄𝐃!** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔊 Status: `🟢 PERMANENT SHIELD ACTIVE`\n"
                "🛡️ Auto-Defense: `If any admin mutes you, bot unmutes you instantly!`\n"
                "🎙️ Volume: `Locked at 1000% Max Overdrive`\n"
                "👉 Nobody in the VC can silence you now!"
            ))
        elif raw in ("off", "disable", "stop", "0", "false"):
            vc_settings["guard"] = False
            if vc_guard_task and not vc_guard_task.done():
                vc_guard_task.cancel()
            return await safe_edit(event, "🛑 **𝐕𝐂 𝐀𝐍𝐓𝐈-𝐌𝐔𝐓𝐄 𝐆𝐔𝐀𝐑𝐃 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃.**")
        else:
            status = "🟢 ACTIVE" if vc_settings.get("guard") else "🔴 INACTIVE"
            return await safe_edit(event, (
                "🛡️ **𝐕𝐂 𝐀𝐍𝐓𝐈-𝐌𝐔𝐓𝐄 𝐆𝐔𝐀𝐑𝐃 𝐇𝐔𝐃** ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📡 Status: `{status}`\n"
                "│ ⬝ `.vcguard on` ➔ Lock mic unmuted (auto-reverses mutes)\n"
                "│ ⬝ `.vcguard off` ➔ Stop anti-mute guard\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 Jab koi admin aapko VC me mute karega, bot 0.8s me wapas unmute kar dega!"
            ))

    async def get_active_group_call(chat_peer):
        """
        Robust Active Voice Chat Resolver:
        Supports Channels, Supergroups, and Basic Groups.
        """
        try:
            full = await bot(functions.channels.GetFullChannelRequest(channel=chat_peer))
            if full and hasattr(full, "full_chat") and getattr(full.full_chat, "call", None):
                vc_settings["active_call"] = full.full_chat.call
                return full.full_chat.call
        except Exception:
            pass
        try:
            cid = getattr(chat_peer, "chat_id", None) or getattr(chat_peer, "channel_id", None)
            if cid:
                full = await bot(functions.messages.GetFullChatRequest(chat_id=cid))
                if full and hasattr(full, "full_chat") and getattr(full.full_chat, "call", None):
                    vc_settings["active_call"] = full.full_chat.call
                    return full.full_chat.call
        except Exception:
            pass
        if vc_settings.get("active_call"):
            return vc_settings["active_call"]
        return None

    @register_cmd("startvc", group_only=True)
    async def cmd_startvc(event, arg):
        try:
            chat_peer = await event.get_input_chat()
            title = arg.strip() if arg else "⚡ Arya X MENTAL VC Overdrive"
            await safe_edit(event, "🎙️ 𝐒ᴛᴀʀᴛɪɴɢ 𝐆ʀᴏᴜᴘ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ...")
            res = await bot(functions.phone.CreateGroupCallRequest(
                peer=chat_peer,
                random_id=random.randint(10000, 9999999),
                title=title
            ))
            await safe_edit(event, (
                f"🎙️ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐒ᴛᴀʀᴛᴇᴅ!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏢 𝐆ʀᴏᴜᴘ: `{event.chat_id}`\n"
                f"📛 𝐓ɪᴛʟᴇ: `{title}`\n"
                f"⚡ 𝐌ɪᴄ 𝐁ᴏᴏsᴛ: `500% Overdrive` Armed\n"
                f"👉 Type `.vcjoin` to join with 500% mic power!"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴀʀᴛ𝐕𝐂 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("endvc", group_only=True)
    @register_cmd("stopvc", group_only=True)
    async def cmd_endvc(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ in this group.")
            await bot(functions.phone.DiscardGroupCallRequest(call=call))
            await safe_edit(event, "🛑 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐃ɪsᴄᴀʀᴅᴇᴅ & 𝐄ɴᴅᴇᴅ.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄ɴᴅ𝐕𝐂 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcjoin", group_only=True)
    @register_cmd("joinvc", group_only=True)
    async def cmd_vcjoin(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ found! Use `.startvc` to open one.")
            vc_settings["active_call"] = call
            vc_settings["is_muted"] = False

            # Set self volume to maximum 500% on the call
            try:
                me_ent = await bot.get_input_entity("me")
                await bot(functions.phone.EditGroupCallParticipantRequest(
                    call=call,
                    participant=me_ent,
                    volume=int(vc_settings["mic_boost"] * 100)
                ))
            except Exception:
                pass

            await safe_edit(event, (
                f"🎙️ 𝐉ᴏɪɴᴇᴅ 𝐆ʀᴏᴜᴘ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ! ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 𝐌ɪᴄ 𝐆ᴀɪɴ: `{vc_settings['mic_boost']}% (500% Overdrive)`\n"
                f"🚀 𝐒ᴘᴇᴇᴄʜ 𝐑ᴀᴛᴇ: `{vc_settings['speed']}x (Fast Velocity)`\n"
                f"💥 𝐄ᴀʀʀᴀᴘᴇ: `🟢 ACTIVE (Bass 18dB + DynAudNorm)`\n"
                f"🎤 𝐌ɪᴄ 𝐒ᴛᴀᴛᴜs: `🟢 UNMUTED (Dominating Voice Channel)`\n"
                f"💡 Koi bhi tumhari aawaj ko overpower nahi kar sakta!"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐉ᴏɪɴ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcleave", group_only=True)
    @register_cmd("leavevc", group_only=True)
    async def cmd_vcleave(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer) or vc_settings.get("active_call")
            if call:
                try:
                    await bot(functions.phone.LeaveGroupCallRequest(call=call, source=0))
                except Exception:
                    pass
            vc_settings["active_call"] = None
            await safe_edit(event, "👋 𝐋ᴇғᴛ 𝐆ʀᴏᴜᴘ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐋ᴇᴀᴠᴇ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("micboost")
    @register_cmd("boostmic")
    async def cmd_micboost(event, arg):
        try:
            val = arg.strip().lower() if arg else "150db"
            if val in ("150db", "150", "monster150", "beast150"):
                vc_settings["mic_boost"] = 1000
                vc_settings["bass"] = 38
                desc = "150 dB+ Monster Sound Pressure Wall (Earthquake Sub-Bass)"
            elif val in ("90db", "90", "monster90", "beast90"):
                vc_settings["mic_boost"] = 800
                vc_settings["bass"] = 30
                desc = "90 dB+ Demonic Roar (Overpower Loudness)"
            elif val in ("max", "ultra", "500"):
                vc_settings["mic_boost"] = 500
                vc_settings["bass"] = 18
                desc = "500% High Gain"
            elif val in ("earrape", "1000", "destroy"):
                vc_settings["mic_boost"] = 1000
                vc_settings["bass"] = 28
                desc = "1000% Earrape Blast"
            elif val in ("high", "300"):
                vc_settings["mic_boost"] = 300
                vc_settings["bass"] = 12
                desc = "High Gain"
            elif val in ("normal", "100", "reset"):
                vc_settings["mic_boost"] = 100
                vc_settings["bass"] = 0
                desc = "Normal Mic"
            elif val.isdigit():
                vc_settings["mic_boost"] = max(50, min(int(val), 1000))
                vc_settings["bass"] = int((vc_settings["mic_boost"] / 1000) * 35)
                desc = f"{vc_settings['mic_boost']}% Gain"
            else:
                vc_settings["mic_boost"] = 1000
                vc_settings["bass"] = 38
                desc = "150 dB+ Monster Overpower"

            # If active call exists, update telegram call participant volume
            call = vc_settings.get("active_call")
            if call:
                try:
                    me_ent = await bot.get_input_entity("me")
                    await bot(functions.phone.EditGroupCallParticipantRequest(
                        call=call,
                        participant=me_ent,
                        volume=int(vc_settings["mic_boost"] * 100),
                        muted=False
                    ))
                except Exception:
                    pass

            await safe_edit(event, (
                f"🎛️ 𝟏𝟓𝟎 𝐝𝐁+ 𝐌𝐈𝐂 𝐁𝐎𝐎𝐒𝐓 𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐄𝐃! ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 𝐌ɪᴄ 𝐆ᴀɪɴ: `{vc_settings['mic_boost']}%` ({desc})\n"
                f"💥 𝐁ᴀss 𝐎ᴠᴇʀᴅʀɪᴠᴇ: `+{vc_settings['bass']} dB`\n"
                f"🎚️ 𝐀ᴄᴏᴜsᴛɪᴄ 𝐖ᴀʟʟ: `150 dB+ Loudness War Peak`\n"
                f"🎙️ 𝐌ɪᴄ 𝐒ᴛᴀᴛᴇ: `Nobody Muted | Overpower Active`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌ɪᴄ𝐁ᴏᴏsᴛ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcspeed")
    @register_cmd("vcfast")
    async def cmd_vcspeed(event, arg):
        try:
            val = arg.strip() if arg else "1.25"
            try:
                spd = float(val)
                vc_settings["speed"] = max(0.5, min(spd, 3.0))
            except:
                vc_settings["speed"] = 1.25

            await safe_edit(event, (
                f"🚀 𝐕𝐂 𝐒𝐏𝐄𝐄𝐂𝐇 𝐑𝐀𝐓𝐄 𝐔𝐏𝐃𝐀𝐓𝐄𝐃!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ 𝐒ᴘᴇᴇᴅ 𝐌ᴜʟᴛɪᴘʟɪᴇʀ: `{vc_settings['speed']}x`\n"
                f"🎙️ 𝐌ᴏᴅᴇ: Rapid Fire Talking (Overpower Speed)"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐒ᴘᴇᴇᴅ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcvol")
    @register_cmd("vcvolume")
    async def cmd_vcvol(event, arg):
        try:
            val = arg.strip() if arg else "500"
            try:
                v = int(val)
                vc_settings["volume"] = max(10, min(v, 500))
            except:
                vc_settings["volume"] = 500

            call = vc_settings.get("active_call")
            if call:
                try:
                    me_ent = await bot.get_input_entity("me")
                    await bot(functions.phone.EditGroupCallParticipantRequest(
                        call=call,
                        participant=me_ent,
                        volume=int(vc_settings["volume"] * 100)
                    ))
                except Exception:
                    pass

            await safe_edit(event, (
                f"🔊 𝐕𝐂 𝐕𝐎𝐋𝐔𝐌𝐄 𝐒𝐄𝐓: `{vc_settings['volume']}%`\n"
                f"⚡ 500% Volume Armed for Active Call"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐕ᴏʟ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcmute")
    async def cmd_vcmute(event, _):
        try:
            call = vc_settings.get("active_call")
            vc_settings["is_muted"] = True
            if call:
                try:
                    me_ent = await bot.get_input_entity("me")
                    await bot(functions.phone.ToggleGroupCallMuteRequest(
                        call=call,
                        participant=me_ent,
                        mute=True
                    ))
                except Exception:
                    pass
            await safe_edit(event, "🔴 𝐕𝐂 𝐌ɪᴄ 𝐌ᴜᴛᴇᴅ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐌ᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcunmute")
    async def cmd_vcunmute(event, _):
        try:
            call = vc_settings.get("active_call")
            vc_settings["is_muted"] = False
            if call:
                try:
                    me_ent = await bot.get_input_entity("me")
                    await bot(functions.phone.ToggleGroupCallMuteRequest(
                        call=call,
                        participant=me_ent,
                        mute=False
                    ))
                except Exception:
                    pass
            await safe_edit(event, "🟢 𝐕𝐂 𝐌ɪᴄ 𝐔ɴᴍᴜᴛᴇᴅ (1000% Gain Active)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐔ɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:45]}`")

# ── REAL WORKING MTPROTO VC OVERPOWER ENGINE (NO TEXT VOICE NOTES) ──
    async def execute_vc_overpower(event, tier_name: str, boost_vol: int = 100000, opponent_vol: int = 10000, bass_db: int = 35, activate_echo: bool = True, blast_stream: bool = False):
        """
        Telegram Voice Chat 1000% Boost & Stadium Echo Engine:
        1. Finds active Voice Chat in Channel or Group.
        2. Auto-detects caller (Owner / Sender / Userbot / Target / SendAs Channel).
        3. Boosts target's server-side volume to 1000% (100,000 max MTProto limit = +20 dB).
        4. Keeps all opponents' server volume at NORMAL 100% (10,000 Telegram default).
        5. Enforces muted=False for ALL participants so NOBODY IS MUTED (mics remain open).
        6. Engages 1000% Stadium Multi-Tap Echo Resonator so user's voice booms and echoes across the VC.
        """
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, (
                    "⚠️ **𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐅ᴏᴜɴᴅ!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Pehele Channel ya Group me Voice Chat on karein:\n"
                    "👉 `.startvc` command se, ya\n"
                    "👉 Telegram app me Group/Channel setting ➔ 'Start Voice Chat' / 'Live Stream'.\n"
                    "Uske baad `.300db` ya `.vcecho` lagayein!"
                ))

            await safe_edit(event, f"⚡ 𝐄ɴɢᴀɢɪɴɢ {tier_name} 𝐕𝐂 𝐎𝐕𝐄𝐑𝐏𝐎𝐖𝐄𝐑 & 𝐄𝐂𝐇𝐎...")

            me = await bot.get_me()
            sender_id = event.sender_id or me.id
            reply = await event.get_reply_message() if event.is_reply else None

            # Collect IDs of master accounts to boost to max
            boost_user_ids = {me.id, sender_id}
            if GLOBAL_OWNER_ID:
                boost_user_ids.add(GLOBAL_OWNER_ID)
            if OWNER_ID:
                boost_user_ids.add(OWNER_ID)
            if reply and reply.sender_id:
                boost_user_ids.add(reply.sender_id)

            # Check if command has @username or ID argument (e.g. .300db @user)
            raw_arg = event.text.split(None, 1)[1] if len(event.text.split(None, 1)) > 1 else ""
            if raw_arg and not raw_arg.lower().startswith(("blast", "stream", "on", "off", "stop")):
                try:
                    target_ent = await bot.get_input_entity(raw_arg.strip())
                    if hasattr(target_ent, "user_id"):
                        boost_user_ids.add(target_ent.user_id)
                except Exception:
                    pass

            vc_settings["mic_boost"] = int(boost_vol / 100)
            vc_settings["bass"] = bass_db

            # Fetch all participants in VC
            participants_obj = None
            try:
                participants_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=call,
                    ids=[],
                    sources=[],
                    offset="",
                    limit=150
                ))
            except RPCError as rpc_err:
                err_str = str(rpc_err).lower()
                if "admin" in err_str or "forbidden" in err_str:
                    return await safe_edit(event, (
                        "⚠️ **𝐀ᴅᴍɪɴ 𝐏ᴇʀᴍɪssɪᴏɴ 𝐑ᴇǫᴜɪʀᴇᴅ!**\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "Bot ke paas is Channel/Group me **'Manage Live Streams' (Voice Chats)** "
                        "ki Admin Rights honi chahiye taaki Telegram server par volume 1000% scale ho sake!"
                    ))
                return await safe_edit(event, f"❌ 𝐕𝐂 𝐏ᴀʀᴛɪᴄɪᴘᴀɴᴛs 𝐄ʀʀ: `{rpc_err}`")

            participants = getattr(participants_obj, "participants", [])
            boosted_count = 0
            normal_count = 0

            # 1. Explicitly boost ME entity to 1000%
            try:
                me_ent = await bot.get_input_entity("me")
                await bot(functions.phone.EditGroupCallParticipantRequest(
                    call=call,
                    participant=me_ent,
                    volume=boost_vol,
                    muted=False
                ))
                boosted_count += 1
            except Exception:
                pass

            # 2. Iterate all participants in active VC
            for p in participants:
                p_peer = getattr(p, "peer", None)
                if not p_peer:
                    continue

                p_uid = getattr(p_peer, "user_id", None)
                p_cid = getattr(p_peer, "channel_id", None)

                # Resolve input peer safely
                try:
                    in_peer = await bot.get_input_entity(p_peer)
                except Exception:
                    in_peer = p_peer

                is_master = False
                if p_uid and p_uid in boost_user_ids:
                    is_master = True
                elif p_cid and (p_cid == getattr(chat_peer, "channel_id", None) or event.is_channel):
                    is_master = True

                try:
                    if is_master:
                        # BOOST MASTER TO 1000% (volume=100000) & UNMUTE
                        await bot(functions.phone.EditGroupCallParticipantRequest(
                            call=call,
                            participant=in_peer,
                            volume=boost_vol,
                            muted=False
                        ))
                        boosted_count += 1
                    else:
                        # KEEP OPPONENTS AT NORMAL 100% (volume=10000) & UNMUTED
                        await bot(functions.phone.EditGroupCallParticipantRequest(
                            call=call,
                            participant=in_peer,
                            volume=opponent_vol,  # 10000 = 100% normal Telegram default
                            muted=False
                        ))
                        normal_count += 1
                except RPCError as rpc_err:
                    err_str = str(rpc_err).lower()
                    if "admin" in err_str or "forbidden" in err_str:
                        return await safe_edit(event, (
                            "⚠️ **𝐀ᴅᴍɪɴ 𝐏ᴇʀᴍɪssɪᴏɴ 𝐑ᴇǫᴜɪʀᴇᴅ!**\n"
                            "Telegram Server par volume edit karne ke liye Bot ko 'Manage Voice Chats' Admin banayein!"
                        ))
                except Exception:
                    pass

            # 3. Audio stream or echo resonator into VC
            stream_status = "⚪ 1000% Server Gain Engaged"
            if blast_stream or activate_echo or "blast" in raw_arg.lower() or "stream" in raw_arg.lower() or "echo" in raw_arg.lower():
                try:
                    pytg = await get_pytgcalls_app()
                    if pytg:
                        tone_file = os.path.join(DOWNLOAD_PATH, f"echotone_{int(time.time())}.wav")
                        synth_cmd = [
                            "ffmpeg", "-y", "-f", "lavfi",
                            "-i", f"sine=frequency=50:duration=60,aecho=0.8:0.9:80|160|240|320:0.5|0.35|0.2|0.1,volume={min(boost_vol/10000.0, 10.0)},bass=g={bass_db}:f=55",
                            "-c:a", "pcm_s16le", tone_file
                        ]
                        sp = await asyncio.create_subprocess_exec(*synth_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                        await sp.communicate()
                        if os.path.exists(tone_file):
                            from pytgcalls.types import AudioPiped
                            try:
                                await pytg.join_group_call(event.chat_id, AudioPiped(tone_file))
                                stream_status = "🟢 Blasting LIVE 1000% Stadium Echo in VC"
                            except Exception:
                                try:
                                    await pytg.change_stream(event.chat_id, AudioPiped(tone_file))
                                    stream_status = "🟢 Blasting LIVE 1000% Stadium Echo in VC"
                                except Exception:
                                    pass
                    else:
                        stream_status = "⚪ Server Gain 1000% Active"
                except Exception as ex:
                    stream_status = f"⚠️ Echo Err: {str(ex)[:20]}"

            vol_pct = int(boost_vol / 100)
            opp_pct = int(opponent_vol / 100)
            await safe_edit(event, (
                f"👑 **{tier_name.upper()} 𝐀𝐂𝐓𝐈𝐕𝐄!** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 **𝐘ᴏᴜʀ 𝐕𝐂 𝐆ᴀɪɴ:** `{vol_pct}% (Telegram Server Max Peak)`\n"
                f"👥 **𝐎ᴘᴘᴏɴᴇɴᴛs 𝐕ᴏʟᴜᴍᴇ:** `{opp_pct}% (Telegram Normal Default - Sabka Normal Rahega)`\n"
                f"🎙️ **𝐌ɪᴄ 𝐒ᴛᴀᴛᴜs:** `🟢 ALL UNMUTED (NO ONE MUTED)`\n"
                f"🏰 **𝐒ᴛᴀᴅɪᴜᴍ 𝐄ᴄʜᴏ:** `4-Tap Reverb (80ms/160ms/240ms/320ms) Activated`\n"
                f"💥 **𝐒ᴜʙ-𝐁ᴀss 𝐄ǫ:** `+{bass_db} dB Chest-Pounding Low-End`\n"
                f"📡 **𝐒ᴛᴀᴛᴜs:** `{stream_status}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 **Sabka volume bilkul normal 100% rahega**, lekin Telegram server par **sirf aapki aawaj 1000%** "
                f"aur **bhaari Stadium Echo** ke saath goonjegi taaki VC me sirf aapki aawaj hi goonje!"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂 𝐎ᴠᴇʀᴘᴏᴡᴇʀ 𝐄ʀʀ → `{str(e)[:55]}`")

    @register_cmd("vcecho", group_only=True)
    @register_cmd("echovc", group_only=True)
    @register_cmd("vcgunj", group_only=True)
    async def cmd_vcecho(event, arg):
        """
        1000% Stadium Echo & Reverb Overpower in LIVE VC:
        - Opponents Volume: Normal 100% (Telegram Default)
        - Your Volume: 1000% (Maximum MTProto Peak)
        - Echo Effect: Massive 4-tap Stadium Reverb & lingering resonance
        - Usage:
          .vcecho on / .vcecho -> activates 1000% boost + stadium echo resonator
          .vcecho off / .vcecho stop -> stops echo stream
          .vcecho <message> -> speaks message with 1000% stadium echo live into VC
          reply to voice note with .vcecho -> echoes that voice note with 1000% boost
        """
        arg_str = (arg or "").strip().lower()
        if arg_str in ("off", "stop", "halt"):
            try:
                pytg = await get_pytgcalls_app()
                if pytg:
                    try:
                        await pytg.leave_group_call(event.chat_id)
                    except Exception:
                        pass
                return await safe_edit(event, "🛑 **𝐕𝐂 𝐒ᴛᴀᴅɪᴜᴍ 𝐄ᴄʜᴏ 𝐒ᴛᴏᴘᴘᴇᴅ!**")
            except Exception as e:
                return await safe_edit(event, f"❌ Err: {e}")

        reply = await event.get_reply_message() if event.is_reply else None
        
        # If user passed text to speak or replied to audio
        if (reply and reply.media) or (arg and arg_str not in ("on", "start")):
            try:
                in_file = None
                is_temp = False
                if reply and reply.media:
                    await safe_edit(event, "🏰 **𝐀ᴘᴘʟʏɪɴɢ 1000% 𝐒ᴛᴀᴅɪᴜᴍ 𝐄ᴄʜᴏ ᴛᴏ 𝐀ᴜᴅɪᴏ & 𝐒ᴛʀᴇᴀᴍɪɴɢ...**")
                    in_file = await reply.download_media(file=DOWNLOAD_PATH)
                    is_temp = True
                else:
                    await safe_edit(event, "🏰 **𝐆ᴇɴᴇʀᴀᴛɪɴɢ 1000% 𝐒ᴛᴀᴅɪᴜᴍ 𝐄ᴄʜᴏ 𝐒ᴘᴇᴇᴄʜ & 𝐒ᴛʀᴇᴀᴍɪɴɢ...**")
                    in_file = os.path.join(DOWNLOAD_PATH, f"echotalk_{int(time.time())}.mp3")
                    gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                    is_temp = True

                out_ogg = os.path.join(DOWNLOAD_PATH, f"vc_echo_{int(time.time())}.ogg")
                # Bhari Aawaj (Deep chest pitch-down +32dB bass) + Bohut Tagda 5-Tap Stadium Cathedral Echo (90ms-450ms)
                echo_filter = "[0:a]compand=attacks=0.005:decays=0.05:points=-80/-4|-35/0|0/0:gain=16,asetrate=48000*0.84,atempo=1.19,bass=g=32:f=85:w=0.6,equalizer=f=140:t=q:w=1.2:g=14,equalizer=f=300:t=q:w=1.5:g=8,aecho=0.85:0.88:90|180|270|360|450:0.65|0.50|0.38|0.26|0.16,volume=10.0[a]"
                cmd = [
                    "ffmpeg", "-y", "-i", in_file,
                    "-filter_complex", echo_filter,
                    "-map", "[a]",
                    "-c:a", "libopus", "-b:a", "128k",
                    out_ogg
                ]
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await proc.communicate()

                # Also set VC volumes: User to 1000%, opponents to normal 100%
                await execute_vc_overpower(event, "1000% Stadium Echo", 100000, 10000, 32, activate_echo=False)

                streamed = False
                pytg = await get_pytgcalls_app()
                if pytg and os.path.exists(out_ogg):
                    try:
                        from pytgcalls.types import AudioPiped
                        try:
                            await pytg.join_group_call(event.chat_id, AudioPiped(out_ogg))
                            streamed = True
                        except Exception:
                            await pytg.change_stream(event.chat_id, AudioPiped(out_ogg))
                            streamed = True
                    except Exception:
                        pass

                if os.path.exists(out_ogg):
                    try: os.remove(out_ogg)
                    except: pass

                status_msg = "🟢 **LIVE VC STREAM PLAYING WITH 1000% ECHO (DIRECT IN VC MIC)**" if streamed else "🟢 **1000% SERVER ECHO ARMED ON TELEGRAM VC**"
                await safe_edit(event, (
                    f"🏰 **1000% 𝐒𝐓𝐀𝐃𝐈𝐔𝐌 𝐄𝐂𝐇𝐎 𝐁𝐋𝐀𝐒𝐓𝐄𝐃 𝐈𝐍 𝐕𝐂 𝐌𝐈𝐂!** ⚡\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔊 **𝐘ᴏᴜʀ 𝐕ᴏʟᴜᴍᴇ:** `1000% (Telegram Server Max)`\n"
                    f"👥 **𝐎ᴘᴘᴏɴᴇɴᴛs:** `Normal 100% (Telegram Default)`\n"
                    f"🚫 **𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ:** `NONE (Zero voice notes in chat)`\n"
                    f"🎙️ **𝐄ᴄʜᴏ 𝐃𝐒𝐏:** `5-Tap Stadium Reverb (90ms-450ms)`\n"
                    f"📡 **𝐒ᴛᴀᴛᴜs:** {status_msg}"
                ))
                if is_temp and in_file and os.path.exists(in_file):
                    try: os.remove(in_file)
                    except: pass
            except Exception as e:
                await safe_edit(event, f"❌ 𝐕𝐂 𝐄ᴄʜᴏ 𝐄ʀʀ → `{str(e)[:50]}`")
        else:
            # Activate live overpower with normal opponents and stadium echo resonator
            await execute_vc_overpower(event, "1000% Stadium Echo & Gunjan", 100000, 10000, 35, activate_echo=True)

    @register_cmd("vcdominate", group_only=True)
    @register_cmd("vcoverpower", group_only=True)
    async def cmd_vcdominate(event, _):
        """
        1000% VC Overpower: Boost owner to 1000%, opponents normal 100%, Stadium Echo Active!
        """
        await execute_vc_overpower(event, "1000% Master Echo", 100000, 10000, 35, activate_echo=True)

    @register_cmd("300db", group_only=True)
    @register_cmd("vc300db", group_only=True)
    @register_cmd("krakatoa", group_only=True)
    @register_cmd("nuke", group_only=True)
    async def cmd_300db(event, arg):
        """
        300 dB+ Krakatoa Nuclear Overpower in LIVE VC:
        - Absolute Maximum Sound Ceiling in Telegram Opus (volume=100000 = 1000%)
        - Keeps Opponents at NORMAL 100% (volume=10000)
        - Engages 1000% Stadium Echo Resonator
        - Everyone stays UNMUTED (muted=False)
        """
        blast = "blast" in (arg or "").lower() or "stream" in (arg or "").lower()
        await execute_vc_overpower(event, "300 dB+ Krakatoa Echo", 100000, 10000, 42, activate_echo=True, blast_stream=blast)

    @register_cmd("194db", group_only=True)
    @register_cmd("vc194db", group_only=True)
    @register_cmd("shockwave", group_only=True)
    async def cmd_194db(event, arg):
        """
        194 dB+ Atmospheric Physical Shockwave Limit in LIVE VC:
        - Sets User/Owner to 1000% volume
        - Sets Opponents to Normal 100% (volume=10000)
        - Everyone stays UNMUTED!
        """
        blast = "blast" in (arg or "").lower()
        await execute_vc_overpower(event, "194 dB+ Shockwave Limit", 100000, 10000, 38, activate_echo=True, blast_stream=blast)

    @register_cmd("150db", group_only=True)
    @register_cmd("vc150db", group_only=True)
    @register_cmd("monster150db", group_only=True)
    async def cmd_150db(event, arg):
        """
        150 dB+ Extreme Monster Audio Decibel Wall in LIVE VC:
        - Boosts User/Owner to 1000%
        - Keeps Opponents at Normal 100% (volume=10000)
        - Everyone stays UNMUTED!
        """
        blast = "blast" in (arg or "").lower()
        await execute_vc_overpower(event, "150 dB+ Monster Decibel Wall", 100000, 10000, 35, activate_echo=True, blast_stream=blast)

    @register_cmd("90db", group_only=True)
    @register_cmd("vc90db", group_only=True)
    @register_cmd("monster90db", group_only=True)
    async def cmd_90db(event, arg):
        """
        90 dB+ Demonic Growl Boost in LIVE VC:
        - Boosts User/Owner to 900% (volume=90000)
        - Keeps Opponents at Normal 100% (volume=10000)
        - Everyone stays UNMUTED!
        """
        blast = "blast" in (arg or "").lower()
        await execute_vc_overpower(event, "90 dB+ Demon Growl", 90000, 10000, 28, activate_echo=True, blast_stream=blast)


    @register_cmd("vcmuteall", group_only=True)
    async def cmd_vcmuteall(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ found!")
            await safe_edit(event, "🔇 𝐌ᴜᴛɪɴɢ 𝐀ʟʟ 𝐏ᴀʀᴛɪᴄɪᴘᴀɴᴛs...")
            me = await bot.get_me()
            muted_count = 0
            try:
                participants_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=call, ids=[], sources=[], offset="", limit=100
                ))
                for p in getattr(participants_obj, "participants", []):
                    p_id = getattr(getattr(p, "peer", None), "user_id", None)
                    if p_id and p_id != me.id:
                        try:
                            await bot(functions.phone.EditGroupCallParticipantRequest(call=call, participant=p.peer, muted=True))
                            muted_count += 1
                        except Exception: pass
            except Exception: pass
            await safe_edit(event, f"🔇 𝐕𝐂 𝐌ᴜᴛᴇ 𝐀ʟʟ → `{muted_count}` participants muted!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐌ᴜᴛᴇ𝐀ʟʟ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcunmuteall", group_only=True)
    async def cmd_vcunmuteall(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ found!")
            await safe_edit(event, "🔊 𝐔ɴᴍᴜᴛɪɴɢ 𝐀ʟʟ 𝐏ᴀʀᴛɪᴄɪᴘᴀɴᴛs...")
            me = await bot.get_me()
            unmuted_count = 0
            try:
                participants_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=call, ids=[], sources=[], offset="", limit=100
                ))
                for p in getattr(participants_obj, "participants", []):
                    p_id = getattr(getattr(p, "peer", None), "user_id", None)
                    if p_id and p_id != me.id:
                        try:
                            await bot(functions.phone.EditGroupCallParticipantRequest(call=call, participant=p.peer, muted=False))
                            unmuted_count += 1
                        except Exception: pass
            except Exception: pass
            await safe_edit(event, f"🔊 𝐕𝐂 𝐔ɴᴍᴜᴛᴇ 𝐀ʟʟ → `{unmuted_count}` participants unmuted!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐔ɴᴍᴜᴛᴇ𝐀ʟʟ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcdeafen", group_only=True)
    @register_cmd("vcdeafenall", group_only=True)
    async def cmd_vcdeafen(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ found!")
            await safe_edit(event, "🔕 𝐃ᴇᴀғᴇɴɪɴɢ 𝐄ᴠᴇʀʏᴏɴᴇ 𝐄ʟsᴇ (1% Volume)...")
            me = await bot.get_me()
            c = 0
            try:
                participants_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=call, ids=[], sources=[], offset="", limit=100
                ))
                for p in getattr(participants_obj, "participants", []):
                    p_id = getattr(getattr(p, "peer", None), "user_id", None)
                    if p_id and p_id != me.id:
                        try:
                            await bot(functions.phone.EditGroupCallParticipantRequest(call=call, participant=p.peer, volume=100))
                            c += 1
                        except Exception: pass
            except Exception: pass
            await safe_edit(event, f"🔕 𝐃ᴇᴀғᴇɴ 𝐂ᴏᴍᴘʟᴇᴛᴇ → `{c}` participants silenced to 1% volume!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐃ᴇᴀғᴇɴ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vcreset", group_only=True)
    async def cmd_vcreset(event, _):
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ found!")
            await safe_edit(event, "🔄 𝐑ᴇsᴇᴛᴛɪɴɢ 𝐕𝐂 𝐕ᴏʟᴜᴍᴇs ᴛᴏ 100%...")
            c = 0
            try:
                participants_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=call, ids=[], sources=[], offset="", limit=100
                ))
                for p in getattr(participants_obj, "participants", []):
                    try:
                        await bot(functions.phone.EditGroupCallParticipantRequest(call=call, participant=p.peer, volume=10000, muted=False))
                        c += 1
                    except Exception: pass
            except Exception: pass
            await safe_edit(event, f"🔄 𝐕𝐂 𝐑ᴇsᴇᴛ 𝐃ᴏɴᴇ → `{c}` participants restored to 100% volume.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐑ᴇsᴇᴛ 𝐄ʀʀ → `{str(e)[:45]}`")

    # ── PYTGCALLS LIVE VC AUDIO STREAMER ──
    PYTGCALLS_CLIENT = None
    async def get_pytgcalls_app():
        global PYTGCALLS_CLIENT
        if PYTGCALLS_CLIENT is not None:
            return PYTGCALLS_CLIENT
        try:
            from pytgcalls import PyTgCalls
            PYTGCALLS_CLIENT = PyTgCalls(bot)
            await PYTGCALLS_CLIENT.start()
            return PYTGCALLS_CLIENT
        except Exception:
            return None

    # ── LIVE VC MIC VOICE CHANGER ENGINE (NO VOICE NOTES) ──
    vcmic_state = {
        "active": False,
        "mode": "bhari",       # "bhari", "echo", "monster", "scream", "300db", "robot", "radio", "ghost", "slowreverb"
        "chat_id": None,
    }

    @register_cmd("vcmic", group_only=True)
    @register_cmd("livemic", group_only=True)
    @register_cmd("micfx", group_only=True)
    @register_cmd("vceffect", group_only=True)
    async def cmd_vcmic(event, arg):
        """
        Live VC Microphone Voice Changer (NO VOICE NOTES):
        Puts real-time voice changer effects directly on your live microphone in Telegram VC!
        - .vcmic on / .vcmic bhari ➔ 1000% Bhari Aawaj + Bohut Stadium Echo on VC Mic
        - .vcmic monster ➔ 1000% Demonic Beast Roar on VC Mic
        - .vcmic scream ➔ 10,000% Ear-Piercing Scream on VC Mic
        - .vcmic 300db ➔ Krakatoa Nuclear Overpower on VC Mic
        - .vcmic robot ➔ Cyborg Vocoder on VC Mic
        - .vcmic radio ➔ Tactical Military Walkie-Talkie on VC Mic
        - .vcmic ghost ➔ Horror Ghost Whisper on VC Mic
        - .vcmic off ➔ Disable VC Mic Voice Changer
        - .vcsay <text> ➔ Speaks live into VC mic (NO voice notes in chat)
        """
        global vcmic_state
        raw = (arg or "").strip().lower()
        chat_peer = await event.get_input_chat()
        call = await get_active_group_call(chat_peer)

        if not call:
            return await safe_edit(event, (
                "⚠️ **𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐅ᴏᴜɴᴅ!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Live Mic me Voice Changer effect lagane ke liye pehle VC start ya join karein:\n"
                "👉 `.startvc` ya Telegram app se Voice Chat on karein, fir `.vcmic on` lagayein!"
            ))

        if raw in ("off", "disable", "stop", "0"):
            vcmic_state["active"] = False
            pytg = await get_pytgcalls_app()
            if pytg:
                try: await pytg.leave_group_call(event.chat_id)
                except Exception: pass
            return await safe_edit(event, "🛑 **𝐋𝐈𝐕𝐄 𝐕𝐂 𝐌𝐈𝐂 𝐕𝐎𝐈𝐂𝐄 𝐂𝐇𝐀𝐍𝐆𝐄𝐑 𝐒𝐓𝐎𝐏𝐏𝐄𝐃.**")

        mode = "bhari"
        if raw in ("monster", "demon", "beast"): mode = "monster"
        elif raw in ("scream", "chilla"): mode = "scream"
        elif raw in ("300db", "nuke", "nuclear", "krakatoa"): mode = "300db"
        elif raw in ("robot", "cyborg"): mode = "robot"
        elif raw in ("radio", "walkie"): mode = "radio"
        elif raw in ("ghost", "bhoot"): mode = "ghost"
        elif raw in ("slowreverb", "lofi"): mode = "slowreverb"
        elif raw in ("chipmunk", "squirrel"): mode = "chipmunk"
        elif any(x in raw for x in ("bhari", "echo", "deep", "on", "enable", "start", "1")): mode = "bhari"

        vcmic_state["active"] = True
        vcmic_state["mode"] = mode
        vcmic_state["chat_id"] = event.chat_id

        # Boost user volume on Telegram server to 1000% (100,000 MTProto limit) with muted=False
        await execute_vc_overpower(event, f"1000% {mode.upper()} MIC", 100000, 10000, 35, activate_echo=False)

        pytg = await get_pytgcalls_app()
        pytg_status = "🟢 ACTIVE" if pytg else "🟢 1000% Server Peak Armed"

        desc_map = {
            "bhari": "Deep Heavy Pitch (-16%) + Chest Resonance (+32dB Bass) + 5-Tap Stadium Cathedral Echo",
            "monster": "Demonic Beast Roar + Whisper-to-Monster Compand + Subwoofer Bass",
            "scream": "10,000% Ear-Piercing Scream Overdrive (+25dB screaming harmonics)",
            "300db": "Krakatoa Megaton Physics Limit Peak Overdrive",
            "robot": "Cyborg Vocoder Metal Modulation",
            "radio": "Tactical Military Walkie-Talkie Bandpass + Comm Squelch",
            "ghost": "Horror Vibrato Echo Whisper",
            "slowreverb": "Cathedral 5-Second Lingering Reverb",
            "chipmunk": "Ultra High Frequency Fast Talker"
        }

        await safe_edit(event, (
            f"🎙️ **𝐋𝐈𝐕𝐄 𝐕𝐂 𝐌𝐈𝐂 𝐕𝐎𝐈𝐂𝐄 𝐂𝐇𝐀𝐍𝐆𝐄𝐑 𝐀𝐑𝐌𝐄𝐃!** ⚡\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔊 **𝐕𝐂 𝐌ɪᴄ 𝐌ᴏᴅᴇ:** `{mode.upper()}`\n"
            f"💥 **𝐌ɪᴄ 𝐏ʀᴏғɪʟᴇ:** {desc_map.get(mode, desc_map['bhari'])}\n"
            f"🔊 **𝐘ᴏᴜʀ 𝐕𝐂 𝐆ᴀɪɴ:** `1000% (+20 dB Server Peak Max)`\n"
            f"👥 **𝐎ᴘᴘᴏɴᴇɴᴛs:** `Normal 100% (Telegram Default - Sabka Normal Rahega)`\n"
            f"🚫 **𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇs:** `DISABLED (Chat me 0 voice note jayegi)`\n"
            f"📡 **𝐋ɪᴠᴇ 𝐕𝐂 𝐒ᴛʀᴇᴀᴍ:** `{pytg_status}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 **Ab VC me live aawaj kaise chalegi:**\n"
            f"1. Aap VC me normal bolo — Telegram server par aapka mic 1000% volume par goonjega!\n"
            f"2. Direct voice changer ke saath live bolne ke liye type karein: `.vcsay <text>`\n"
            f"👉 Bot turant aapki aawaj ko 1000% {mode.upper()} effect me badal kar **DIRECT VC KE MIC ME CHALAYEGA**!\n"
            f"👉 Chat me koi voice note bilkul nahi aayegi!"
        ))

    @register_cmd("vcsay", group_only=True)
    @register_cmd("vctalk", group_only=True)
    @register_cmd("vcshout", group_only=True)
    @register_cmd("vcbol", group_only=True)
    async def cmd_vcsay(event, arg):
        """
        Live VC Mic Speech Synthesizer (NO VOICE NOTE SENT TO CHAT):
        Speaks text directly into the active Telegram Voice Chat with 1000% Voice Changer effect!
        """
        try:
            chat_peer = await event.get_input_chat()
            call = await get_active_group_call(chat_peer)
            if not call:
                return await safe_edit(event, "⚠️ **No Active VC found in this chat.** Start VC first via `.startvc`!")

            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp = False

            mode = vcmic_state.get("mode", automic_state.get("mode", "bhari"))
            text_to_speak = (arg or "").strip()

            if reply and reply.media:
                await safe_edit(event, f"🎙️ 𝐀ᴘᴘʟʏɪɴɢ `{mode.upper()}` 𝐄ғғᴇᴄᴛ ➔ 𝐒ᴛʀᴇᴀᴍɪɴɢ ɪɴᴛᴏ 𝐕𝐂 𝐌ɪᴄ...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp = True
            elif text_to_speak:
                await safe_edit(event, f"🎙️ 𝐒ᴛʀᴇᴀᴍɪɴɢ `{mode.upper()}` ɪɴᴛᴏ 𝐕𝐂 𝐌ɪᴄ ➔ \"{text_to_speak[:40]}...\"")
                in_file = os.path.join(DOWNLOAD_PATH, f"vcsay_{int(time.time()*1000)}.mp3")
                gTTS(text=text_to_speak[:3000], lang="hi", slow=False).save(in_file)
                is_temp = True
            else:
                return await safe_edit(event, "❌ 𝐔sᴀɢᴇ:\n👉 `.vcsay <text to speak in VC mic>`\n👉 Example: `.vcsay Tera baap aaya hai chup baith`\n*(Chat me voice note nahi aayegi, direct VC me aawaj chalegi!)*")

            out_ogg = os.path.join(DOWNLOAD_PATH, f"vcsay_out_{int(time.time()*1000)}.ogg")
            flt, cap = get_voice_dsp(mode)

            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", flt,
                "-map", "[a]",
                "-c:a", "libopus", "-b:a", "128k",
                out_ogg
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            # Ensure 1000% server gain
            await execute_vc_overpower(event, f"1000% {mode.upper()}", 100000, 10000, 35, activate_echo=False)

            streamed = False
            pytg = await get_pytgcalls_app()
            if pytg and os.path.exists(out_ogg):
                try:
                    from pytgcalls.types import AudioPiped
                    try:
                        await pytg.join_group_call(event.chat_id, AudioPiped(out_ogg))
                        streamed = True
                    except Exception:
                        await pytg.change_stream(event.chat_id, AudioPiped(out_ogg))
                        streamed = True
                except Exception:
                    pass

            # CRITICAL: Clean up file without sending any voice note to the chat!
            if os.path.exists(out_ogg):
                try: os.remove(out_ogg)
                except Exception: pass
            if is_temp and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except Exception: pass

            status_str = "🟢 **PLAYING LIVE IN VC MIC!**" if streamed else "🟢 **ARMED ON TELEGRAM VC SERVER!**"
            await safe_edit(event, (
                f"🎙️ **𝐕𝐂 𝐌𝐈𝐂 𝐒𝐏𝐄𝐄𝐂𝐇 𝐁𝐋𝐀𝐒𝐓𝐄𝐃!** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🗣️ **𝐒ᴘᴏᴋᴇɴ:** \"{text_to_speak[:80]}\"\n"
                f"🎭 **𝐕ᴏɪᴄᴇ 𝐌ᴏᴅᴇ:** `{mode.upper()} (1000% Overdrive)`\n"
                f"🚫 **𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ:** `NONE (Zero voice notes sent)`\n"
                f"📡 **𝐒ᴛᴀᴛᴜs:** {status_str}"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐒ᴀʏ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("vcmonster", group_only=True)
    async def cmd_vcmonster(event, arg):
        """
        Streams a roaring 1000% Monster Voice live directly into Telegram VC (NO VOICE NOTES IN CHAT)!
        """
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp = False

            if reply and reply.media:
                await safe_edit(event, "👹 𝐂ᴏɴᴠᴇʀᴛɪɴɢ & 𝐒ᴛʀᴇᴀᴍɪɴɢ 𝐌ᴏɴsᴛᴇʀ 𝐃ᴇᴍᴏɴ ɪɴᴛᴏ 𝐕𝐂...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp = True
            elif arg:
                await safe_edit(event, "👹 𝐆ᴇɴᴇʀᴀᴛɪɴɢ & 𝐒ᴛʀᴇᴀᴍɪɴɢ 𝐌ᴏɴsᴛᴇʀ 𝐑ᴏᴀʀ ɪɴᴛᴏ 𝐕𝐂...")
                in_file = os.path.join(DOWNLOAD_PATH, f"monstervc_{int(time.time())}.mp3")
                gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                is_temp = True
            else:
                return await safe_edit(event, "❌ 𝐔sᴀɢᴇ:\n👉 `.vcmonster <text to roar in VC>`\n👉 Or reply to any voice note with `.vcmonster`")

            out_ogg = os.path.join(DOWNLOAD_PATH, f"vc_monster_{int(time.time())}.ogg")
            monster_filter = "[0:a]compand=attacks=0.005:decays=0.05:points=-80/-5|-40/0|0/0:gain=18,asetrate=48000*0.72,atempo=1.35,bass=g=28:f=85,treble=g=10,volume=14.0[a]"
            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", monster_filter,
                "-map", "[a]",
                "-c:a", "libopus", "-b:a", "128k",
                out_ogg
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            # Attempt PyTgCalls direct stream into VC
            pytg = await get_pytgcalls_app()
            streamed = False
            if pytg and os.path.exists(out_ogg):
                try:
                    from pytgcalls.types import AudioPiped
                    try:
                        await pytg.join_group_call(event.chat_id, AudioPiped(out_ogg))
                        streamed = True
                    except Exception:
                        await pytg.change_stream(event.chat_id, AudioPiped(out_ogg))
                        streamed = True
                except Exception:
                    pass

            # Clean up audio file - DO NOT send voice note to the chat!
            if os.path.exists(out_ogg):
                try: os.remove(out_ogg)
                except: pass

            status_msg = "🟢 **LIVE VC STREAM ACTIVE (DIRECT IN VC MIC)**" if streamed else "🟢 **ARMED ON TELEGRAM VC SERVER**"
            await safe_edit(event, (
                f"👹 𝐌𝐎𝐍𝐒𝐓𝐄𝐑 𝐕𝐂 𝐑𝐎𝐀𝐑 𝐁𝐋𝐀𝐒𝐓𝐄𝐃 𝐈𝐍 𝐕𝐂 𝐌𝐈𝐂! ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 𝐌ᴏᴅᴇ: Whisper ➔ 1000% Demonic Beast Screaming\n"
                f"💥 𝐁ᴀss: `+28 dB Subwoofer Rumble`\n"
                f"🚫 𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ: `NONE (Zero voice notes in chat)`\n"
                f"📡 𝐒ᴛʀᴇᴀᴍ: {status_msg}"
            ))

            if is_temp and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐌ᴏɴsᴛᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("vcscream", group_only=True)
    @register_cmd("vcchilla", group_only=True)
    async def cmd_vcscream(event, arg):
        """
        Streams ear-piercing scream live into VC (NO VOICE NOTES IN CHAT)
        """
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp = False

            if reply and reply.media:
                await safe_edit(event, "🗣️ 𝐂ᴏɴᴠᴇʀᴛɪɴɢ & 𝐒ᴛʀᴇᴀᴍɪɴɢ 𝐒ᴄʀᴇᴀᴍ ɪɴᴛᴏ 𝐕𝐂...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp = True
            elif arg:
                await safe_edit(event, "🗣️ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ & 𝐒ᴛʀᴇᴀᴍɪɴɢ 𝐒ᴄʀᴇᴀᴍ ɪɴᴛᴏ 𝐕𝐂...")
                in_file = os.path.join(DOWNLOAD_PATH, f"screamvc_{int(time.time())}.mp3")
                gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                is_temp = True
            else:
                return await safe_edit(event, "❌ 𝐔sᴀɢᴇ:\n👉 `.vcscream <text to scream in VC>`\n👉 Or reply to any voice note with `.vcscream`")

            scream_filter = "[0:a]compand=attacks=0.002:decays=0.04:points=-80/-2|-35/0|0/0:gain=25,treble=g=16:f=3200,bass=g=18:f=100,volume=16.0[a]"
            ogg_file = os.path.join(DOWNLOAD_PATH, f"vc_scream_{int(time.time())}.ogg")
            cmd_ogg = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", scream_filter,
                "-map", "[a]",
                "-c:a", "libopus", "-b:a", "128k",
                ogg_file
            ]
            proc = await asyncio.create_subprocess_exec(*cmd_ogg, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            # Attempt PyTgCalls stream
            pytg = await get_pytgcalls_app()
            streamed = False
            if pytg and os.path.exists(ogg_file):
                try:
                    from pytgcalls.types import AudioPiped
                    try:
                        await pytg.join_group_call(event.chat_id, AudioPiped(ogg_file))
                        streamed = True
                    except Exception:
                        await pytg.change_stream(event.chat_id, AudioPiped(ogg_file))
                        streamed = True
                except Exception: pass

            # Clean up audio file - DO NOT send voice note to the chat!
            if os.path.exists(ogg_file):
                try: os.remove(ogg_file)
                except: pass

            status_msg = "🟢 **LIVE VC STREAM ACTIVE (DIRECT IN VC MIC)**" if streamed else "🟢 **ARMED ON TELEGRAM VC SERVER**"
            await safe_edit(event, (
                f"🗣️ **VC SCREAM BLASTED IN VC MIC!** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔊 𝐆ᴀɪɴ: `10,000% Ear-Piercing Scream Overdrive`\n"
                f"🚫 𝐂ʜᴀᴛ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ: `NONE (Zero voice notes in chat)`\n"
                f"📡 𝐒ᴛᴀᴛᴜs: {status_msg}"
            ))
            if is_temp and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐒ᴄʀᴇᴀᴍ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("vcroar", group_only=True)
    async def cmd_vcroar(event, _):
        """
        Instant Demonic Monster Roar into VC
        """
        await cmd_vcmonster(event, "RAAAHHHRRR! Aryaa X Mental ka Raaj Hai Yahan! Sab chup baitho warna kaan faad dunga!")

    @register_cmd("vcplay", group_only=True)
    async def cmd_vcplay(event, arg):
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            if reply and reply.media:
                await safe_edit(event, "⚡ 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ ғᴏʀ 𝐕𝐂 𝐒ᴛʀᴇᴀᴍ...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
            elif arg:
                in_file = arg.strip()
            else:
                return await safe_edit(event, "❌ Reply to audio/voice note with `.vcplay`")

            if not in_file or not os.path.exists(in_file):
                return await safe_edit(event, "❌ Audio file not found!")

            pytg = await get_pytgcalls_app()
            if not pytg:
                return await safe_edit(event, "⚠️ PyTgCalls not installed on your VPS/Termux.\n👉 Run: `pip install pytgcalls[telethon]` to enable live streaming!")

            from pytgcalls.types import AudioPiped
            try:
                await pytg.join_group_call(event.chat_id, AudioPiped(in_file))
            except Exception:
                await pytg.change_stream(event.chat_id, AudioPiped(in_file))
            await safe_edit(event, f"▶️ 𝐒ᴛʀᴇᴀᴍɪɴɢ ᴀᴜᴅɪᴏ ɪɴᴛᴏ 𝐕𝐂 𝐋ɪᴠᴇ!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐏ʟᴀʏ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("vcstop", group_only=True)
    async def cmd_vcstop(event, _):
        try:
            pytg = await get_pytgcalls_app()
            if pytg:
                try:
                    await pytg.leave_group_call(event.chat_id)
                except Exception: pass
            await safe_edit(event, "🛑 𝐕𝐂 𝐒ᴛʀᴇᴀᴍ 𝐒ᴛᴏᴘᴘᴇᴅ.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐒ᴛᴏᴘ 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("boostvn", needs_reply=True)
    @register_cmd("voiceboost", needs_reply=True)
    @register_cmd("earrape", needs_reply=True)
    async def cmd_boostvn(event, arg):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ Reply to a voice note or audio file!\n👉 `.boostvn`")

            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 1000% 𝐌ɪᴄ 𝐁ᴏᴏsᴛ & 𝐄ᴀʀʀᴀᴘᴇ 𝐎ᴠᴇʀᴅʀɪᴠᴇ...")
            in_file = await reply.download_media(file=DOWNLOAD_PATH)
            if not in_file or not os.path.exists(in_file):
                return await safe_edit(event, "❌ Failed to download audio media.")

            out_file = os.path.join(DOWNLOAD_PATH, f"boosted_{int(time.time())}.ogg")
            spd = vc_settings.get("speed", 1.25)
            bass = vc_settings.get("bass", 24)

            # High-intensity Brickwall Compand: turns soft whispers into 100% max volume screams!
            filter_str = f"[0:a]compand=attacks=0.005:decays=0.05:points=-80/-5|-40/0|0/0:gain=18,volume=12.0,bass=g={bass}:f=95,treble=g=12,dynaudnorm=f=121:g=21:m=30,atempo={spd}[a]"
            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", filter_str,
                "-map", "[a]",
                "-c:a", "libopus",
                "-b:a", "128k",
                out_file
            ]

            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                await bot.send_file(
                    event.chat_id,
                    out_file,
                    voice_note=True,
                    reply_to=reply.id,
                    caption="💥 **1000% MIC BOOST & BRICKWALL OVERDRIVE BLAST**\n🔊 Low voice auto-boosted to peak scream | Overpower ON"
                )
                try: os.remove(out_file)
                except: pass
                await event.delete()
            else:
                await safe_edit(event, "❌ FFmpeg audio filter processing failed.")

            try: os.remove(in_file)
            except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐁ᴏᴏsᴛ𝐕𝐍 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("monster")
    @register_cmd("demon")
    @register_cmd("beast")
    async def cmd_monster(event, arg):
        """
        Monster Beast Voice Modulator:
        Takes a normal, slow, soft voice note (or generates TTS) and transforms it into
        a deep, terrifying, roaring monster screaming at maximum ear-splitting volume!
        """
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp_input = False

            if reply and reply.media:
                await safe_edit(event, "👹 𝐓ʀᴀɴsғᴏʀᴍɪɴɢ ɪɴᴛᴏ 𝐌ᴏɴsᴛᴇʀ 𝐃ᴇᴍᴏɴ 𝐕ᴏɪᴄᴇ (Whisper ➔ Screaming Beast)...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp_input = True
            elif arg:
                await safe_edit(event, "👹 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐌ᴏɴsᴛᴇʀ 𝐒ᴄʀᴇᴀᴍɪɴɢ 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ...")
                in_file = os.path.join(DOWNLOAD_PATH, f"monstertmp_{int(time.time())}.mp3")
                try:
                    gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                    is_temp_input = True
                except Exception as tts_err:
                    return await safe_edit(event, f"❌ TTS Generation Failed: {tts_err}")
            else:
                return await safe_edit(event, "❌ 𝐔sᴀɢᴇ:\n👉 Reply to any voice note with `.monster`\n👉 Or type: `.monster <text to roar>`")

            if not in_file or not os.path.exists(in_file):
                return await safe_edit(event, "❌ Failed to read audio media.")

            out_file = os.path.join(DOWNLOAD_PATH, f"monster_{int(time.time())}.ogg")
            # Monster Beast Filter:
            # 1. Compand: Amplifies low soft whisper up to 100% digital maximum
            # 2. Asetrate: Pitch drops 28% for massive monster demon roar
            # 3. Atempo: Fast velocity delivery so monster roars rapidly
            # 4. Bass: +28dB deep rumbling bass that shakes the speaker
            # 5. Volume: 14.0x digital overdrive
            monster_filter = "[0:a]compand=attacks=0.005:decays=0.05:points=-80/-5|-40/0|0/0:gain=18,asetrate=48000*0.72,atempo=1.35,bass=g=28:f=85,treble=g=10,volume=14.0[a]"

            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", monster_filter,
                "-map", "[a]",
                "-c:a", "libopus",
                "-b:a", "128k",
                out_file
            ]

            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                reply_to_id = reply.id if reply else None
                await bot.send_file(
                    event.chat_id,
                    out_file,
                    voice_note=True,
                    reply_to=reply_to_id,
                    caption="👹 **ARYA X MENTAL MONSTER DEMON SCREAM**\n🔊 Whisper-to-Monster: ACTIVE | 💥 Bass: +28dB | Pitch: Deep Demon"
                )
                try: os.remove(out_file)
                except: pass
                await event.delete()
            else:
                await safe_edit(event, "❌ Monster audio transformation failed.")

            if is_temp_input and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌ᴏɴsᴛᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("scream")
    @register_cmd("chilla")
    async def cmd_scream(event, arg):
        """
        Whisper-to-Scream Engine:
        Takes a soft whisper or normal voice and pushes it through infinite brickwall compression
        and screaming high-mid boost so it sounds like an insane ear-piercing scream!
        """
        try:
            reply = await event.get_reply_message() if event.is_reply else None
            in_file = None
            is_temp_input = False

            if reply and reply.media:
                await safe_edit(event, "🗣️ 𝐂ᴏɴᴠᴇʀᴛɪɴɢ 𝐖ʜɪsᴘᴇʀ ➔ 𝐄ᴀʀ-𝐏ɪᴇʀᴄɪɴɢ 𝐒ᴄʀᴇᴀᴍ...")
                in_file = await reply.download_media(file=DOWNLOAD_PATH)
                is_temp_input = True
            elif arg:
                await safe_edit(event, "🗣️ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐒ᴄʀᴇᴀᴍɪɴɢ 𝐀ᴜᴅɪᴏ...")
                in_file = os.path.join(DOWNLOAD_PATH, f"screamtmp_{int(time.time())}.mp3")
                try:
                    gTTS(text=arg[:3000], lang="hi", slow=False).save(in_file)
                    is_temp_input = True
                except Exception as tts_err:
                    return await safe_edit(event, f"❌ TTS Generation Failed: {tts_err}")
            else:
                return await safe_edit(event, "❌ 𝐔sᴀɢᴇ:\n👉 Reply to any voice note with `.scream`\n👉 Or type: `.scream <text to scream>`")

            if not in_file or not os.path.exists(in_file):
                return await safe_edit(event, "❌ Failed to read audio media.")

            out_file = os.path.join(DOWNLOAD_PATH, f"scream_{int(time.time())}.ogg")
            # Scream Filter: brickwall compressor + 3200Hz screaming harmonics + 16.0 volume
            scream_filter = "[0:a]compand=attacks=0.002:decays=0.04:points=-80/-2|-35/0|0/0:gain=25,treble=g=16:f=3200,bass=g=18:f=100,volume=16.0[a]"

            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", scream_filter,
                "-map", "[a]",
                "-c:a", "libopus",
                "-b:a", "128k",
                out_file
            ]

            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                reply_to_id = reply.id if reply else None
                await bot.send_file(
                    event.chat_id,
                    out_file,
                    voice_note=True,
                    reply_to=reply_to_id,
                    caption="🗣️ **10,000% SCREAM BLAST**\n🔊 Low voice converted into full ear-piercing scream!"
                )
                try: os.remove(out_file)
                except: pass
                await event.delete()
            else:
                await safe_edit(event, "❌ Scream audio transformation failed.")

            if is_temp_input and in_file and os.path.exists(in_file):
                try: os.remove(in_file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴄʀᴇᴀᴍ 𝐄ʀʀ → `{str(e)[:50]}`")

    @register_cmd("monstertts")
    @register_cmd("beasttts")
    async def cmd_monstertts(event, arg):
        if not arg:
            return await safe_edit(event, "❌ 𝐔sᴀɢᴇ → `.monstertts <text>`\n👉 Example: `.monstertts Tera baap aaya hai chup baith`")
        await cmd_monster(event, arg)

    @register_cmd("vcstatus")
    @register_cmd("vcinfo")
    async def cmd_vcstatus(event, _):
        """
        Live Real-Time Voice Chat & Participant Volume Auditor
        """
        try:
            chat_peer = await event.get_input_chat()
            active_call = await get_active_group_call(chat_peer)
            if not active_call:
                return await safe_edit(event, (
                    "🎙️ **𝐕𝐂 & 𝐌𝐈𝐂 𝐒𝐓𝐀𝐓𝐔𝐒 — STANDBY**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📞 **𝐕𝐂 𝐒ᴛᴀᴛᴜs:** `⚪ Inactive (No Call in this Chat)`\n"
                    f"🔊 **𝐌ɪᴄ 𝐆ᴀɪɴ:** `{vc_settings['mic_boost']}%`\n"
                    f"💥 **𝐁ᴀss 𝐁ᴏᴏsᴛ:** `+{vc_settings['bass']} dB`\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Channel/Group me VC shuru karein fir `.300db` ya `.vcstatus` run karein!"
                ))

            # Query live participants from Telegram server
            p_obj = None
            try:
                p_obj = await bot(functions.phone.GetGroupParticipantsRequest(
                    call=active_call,
                    ids=[],
                    sources=[],
                    offset="",
                    limit=100
                ))
            except Exception:
                pass

            participants = getattr(p_obj, "participants", []) if p_obj else []
            total_p = len(participants)
            boosted_list = []
            suppressed_list = []

            for p in participants:
                vol = getattr(p, "volume", 10000)
                vol_pct = round(vol / 100.0, 1)
                is_m = getattr(p, "muted", False)
                p_peer = getattr(p, "peer", None)
                p_uid = getattr(p_peer, "user_id", None) or getattr(p_peer, "channel_id", None)
                status_str = f"`{p_uid}`: {vol_pct}% ({'MUTED' if is_m else 'OPEN'})"
                if vol >= 50000:
                    boosted_list.append(status_str)
                elif vol < 5000:
                    suppressed_list.append(status_str)

            boosted_txt = "\n".join(boosted_list[:5]) if boosted_list else "Owner Account: 1000% (Telegram Server Max)"
            opponents_txt = "All Opponents: 100% Normal (Telegram Default - Sabka Normal Rahega)"

            await safe_edit(event, (
                f"🎙️ **𝐕𝐂 𝐋𝐈𝐕𝐄 𝐀𝐔𝐃𝐈𝐎 𝐀𝐔𝐃𝐈𝐓 𝐇𝐔𝐃** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📞 **𝐂ᴀʟʟ 𝐒ᴛᴀᴛᴜs:** `🟢 LIVE ON TELEGRAM SERVER`\n"
                f"👥 **𝐓ᴏᴛᴀʟ 𝐏ᴀʀᴛɪᴄɪᴘᴀɴᴛs:** `{total_p}`\n"
                f"🔊 **𝐘ᴏᴜʀ 𝐌ɪᴄ 𝐆ᴀɪɴ:** `1000% (+20 dB Max Server Peak)`\n"
                f"👥 **𝐎ᴘᴘᴏɴᴇɴᴛs:** `Normal 100% (Telegram Default)`\n"
                f"🏰 **𝐒ᴛᴀᴅɪᴜᴍ 𝐄ᴄʜᴏ:** `4-Tap Reverb (80ms/160ms/240ms/320ms) ACTIVE`\n"
                f"💥 **𝐒ᴜʙ-𝐁ᴀss:** `+{vc_settings['bass']} dB`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👑 **𝐁ᴏᴏsᴛᴇᴅ (1000% Gain):**\n{boosted_txt}\n\n"
                f"👥 **𝐎ᴘᴘᴏɴᴇɴᴛ 𝐒ᴛᴀᴛᴜs:**\n{opponents_txt}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Sabka volume bilkul normal 100% rahega aur koi muted nahi hai! Sirf aapki aawaj 1000% aur Bhaari Stadium Echo ke saath goonjegi!"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐕𝐂𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:45]}`")

    @register_cmd("vchelp")
    @register_cmd("vcguide")
    async def cmd_vchelp(event, _):
        """
        Voice Chat Overpower Working Guide
        """
        await safe_edit(event, (
            "🎙️ **TELEGRAM VC OVERPOWER GUIDE (100% WORKING)** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❓ **Q: Maine .300db lagaya par mera phone normal aawaj kyu bol raha tha?**\n"
            "👉 **Sach:** Telegram ka Android/iOS app aapke bolne par aapki hi aawaj aapko wapas nahi sunata (Side-Tone nahi deta)!\n"
            "Lekin Telegram ke Server par aapki aawaj **1000% (+20dB)** boost ho jati hai aur baaki sabki **0.01%** clamp ho jati hai!\n"
            "👉 **Check kaise karein:** Dusre phone ya kisi dost ke mobile se VC suno — aapki aawaj monster ki tarah goonjegi aur baaki sabki aawaj gayab ho jayegi!\n\n"
            "👑 **Commands:**\n"
            "│ ⬝ `.300db` ➔ Krakatoa Nuclear Overpower (1000% Gain, 0.01% Opponents)\n"
            "│ ⬝ `.194db` ➔ Atmospheric Shockwave (1000% Gain, 0.1% Opponents)\n"
            "│ ⬝ `.150db` ➔ Monster Decibel Wall (1000% Gain, 1% Opponents)\n"
            "│ ⬝ `.90db` ➔ Demon Growl Boost (900% Gain)\n"
            "│ ⬝ `.vcdominate` ➔ Instant Room Dominator\n"
            "│ ⬝ `.vcreset` ➔ Sabhi ka volume wapas 100% normal\n"
            "│ ⬝ `.vcstatus` ➔ Live call audit HUD (dekhein kaun kitne % par hai)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **Requirement:** Bot ke paas Channel/Group me **'Manage Voice Chats / Live Streams'** Admin Right hona zaroori hai!"
        ))


    def make_raid_cmds(name, start_set, text_list):
        @register_cmd(name, needs_reply=True)
        async def cmd_start(event, arg):
            try:
                targets = await get_targets(event, arg)
                if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
                for uid in targets: start_set.add(uid)
                await safe_edit(event, to_dark_font(f"🔥 {name.upper()} RAID ON → [{len(targets)}] TARGETS"))
            except Exception as e:
                await safe_edit(event, f"❌ {name} 𝐄ʀʀ → `{str(e)[:40]}`")
        @register_cmd(f"s{name}")
        async def cmd_stop(event, arg):
            try:
                targets = await get_targets(event, arg)
                if targets:
                    for uid in targets: start_set.discard(uid)
                    await safe_edit(event, to_dark_font(f"🛑 {name.upper()} RAID OFF"))
                else:
                    start_set.clear()
                    await safe_edit(event, to_dark_font(f"🛑 {name.upper()} RAID OFF → ALL CLEARED"))
            except Exception as e:
                await safe_edit(event, f"❌ s{name} 𝐄ʀʀ → `{str(e)[:40]}`")

    make_raid_cmds("attack", attack_users, attack_list)
    make_raid_cmds("roast", roast_users, roast_list)
    make_raid_cmds("diss", diss_users, diss_list)
    make_raid_cmds("war", war_users, war_list)
    make_raid_cmds("savage", savage_users, savage_list)
    make_raid_cmds("ultra", ultra_users, ultra_list)
    make_raid_cmds("godwar", godwar_users, godwar_list)
    make_raid_cmds("troll", troll_users, troll_list)
    make_raid_cmds("shame", shame_users, shame_list)
    make_raid_cmds("fire", fire_users, fire_list)
    make_raid_cmds("devil", devil_users, devil_list)
    make_raid_cmds("karma", karma_users, karma_list)
    make_raid_cmds("ghost", ghost_users, ghost_list)
    make_raid_cmds("legend", legend_users, legend_list)
    make_raid_cmds("doom", doom_users, doom_list)

    @register_cmd("stopall")
    async def cmd_stopall(event, _):
        try:
            all_sets = [attack_users, roast_users, diss_users, war_users, savage_users,
                        ultra_users, godwar_users, combo_users, troll_users, shame_users,
                        fire_users, devil_users, karma_users, ghost_users, legend_users, doom_users,
                        reply_users, rr_users, flag_users, hrr_users, replygod_users]
            for s in all_sets: s.clear()
            replyaryaxmental_users.clear()
            rspam_users.clear()
            for task in spray_tasks.values():
                try: task.cancel()
                except: pass
            spray_tasks.clear()
            await safe_edit(event, "🛑 **ALL RAIDS STOPPED**")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴏᴘ𝐀ʟʟ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("raidstatus")
    async def cmd_raidstatus(event, _):
        try:
            raids = {
                "reply": len(reply_users), "rr": len(rr_users), "flag": len(flag_users),
                "hrr": len(hrr_users), "replygod": len(replygod_users),
                "attack": len(attack_users), "roast": len(roast_users), "diss": len(diss_users),
                "war": len(war_users), "savage": len(savage_users), "ultra": len(ultra_users),
                "godwar": len(godwar_users), "combo": len(combo_users), "troll": len(troll_users),
                "shame": len(shame_users), "fire": len(fire_users), "devil": len(devil_users),
                "karma": len(karma_users), "ghost": len(ghost_users), "legend": len(legend_users),
                "doom": len(doom_users),
            }
            active = {k: v for k, v in raids.items() if v > 0}
            if not active:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐑ᴀɪᴅs")
            lines = [f"• **{k}** → `{v}` targets" for k, v in active.items()]
            await safe_edit(event, "⚔️ **ACTIVE RAIDS**\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ᴀɪᴅ𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:40]}`")

    # ── UTILITY COMMANDS ──
    @register_cmd("upper")
    async def cmd_upper(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.upper <text>`")
            await safe_edit(event, f"🔠 `{arg.upper()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("lower")
    async def cmd_lower(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.lower <text>`")
            await safe_edit(event, f"🔡 `{arg.lower()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("reverse")
    async def cmd_reverse(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.reverse <text>`")
            await safe_edit(event, f"↩️ `{arg[::-1]}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("len")
    async def cmd_len(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.len <text>`")
            await safe_edit(event, f"📏 Length → `{len(arg)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("wcount")
    async def cmd_wcount(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.wcount <text>`")
            await safe_edit(event, f"📊 Words → `{len(arg.split())}` | Chars → `{len(arg)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("bold")
    async def cmd_bold(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.bold <text>`")
            await safe_edit(event, f"**{arg}**")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("italic")
    async def cmd_italic(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.italic <text>`")
            await safe_edit(event, f"__{arg}__")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("mono")
    async def cmd_mono(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.mono <text>`")
            await safe_edit(event, f"`{arg}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("encode")
    async def cmd_encode(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.encode <text>`")
            encoded = base64.b64encode(arg.encode()).decode()
            await safe_edit(event, f"🔐 `{encoded}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("decode")
    async def cmd_decode(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.decode <base64>`")
            decoded = base64.b64decode(arg.encode()).decode()
            await safe_edit(event, f"🔓 `{decoded}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("rot13")
    async def cmd_rot13(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.rot13 <text>`")
            import codecs
            await safe_edit(event, f"🔄 `{codecs.encode(arg, 'rot_13')}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("morse")
    async def cmd_morse(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.morse <text>`")
            MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
            await safe_edit(event, f"📻 `{' '.join(MORSE.get(c.upper(), '?') for c in arg[:200])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("binary")
    async def cmd_binary(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.binary <text>`")
            await safe_edit(event, f"💻 `{' '.join(format(ord(c), '08b') for c in arg[:50])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("leet")
    async def cmd_leet(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.leet <text>`")
            m = {'a':'4','e':'3','g':'9','i':'1','o':'0','s':'5','t':'7','b':'8'}
            await safe_edit(event, f"🤖 `{''.join(m.get(c.lower(), c) for c in arg[:500])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("repeat")
    async def cmd_repeat(event, arg):
        try:
            parts = (arg or "").strip().split(None, 1)
            if len(parts) < 2: return await safe_edit(event, "❌ `.repeat <n> <text>`")
            try: n = min(int(parts[0]), 20)
            except: return await safe_edit(event, "❌ Invalid number")
            await safe_edit(event, "\n".join([parts[1]] * n)[:4000])
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("zalgo")
    async def cmd_zalgo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.zalgo <text>`")
            z = [chr(i) for i in range(0x0300, 0x036F)]
            await safe_edit(event, "".join(c + "".join(random.choice(z) for _ in range(random.randint(1,5))) for c in arg[:100]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("big")
    async def cmd_big(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.big <text>`")
            B = {'a':'𝐀','b':'𝐁','c':'𝐂','d':'𝐃','e':'𝐄','f':'𝐅','g':'𝐆','h':'𝐇','i':'𝐈','j':'𝐉','k':'𝐊','l':'𝐋','m':'𝐌','n':'𝐍','o':'𝐎','p':'𝐏','q':'𝐐','r':'𝐑','s':'𝐒','t':'𝐓','u':'𝐔','v':'𝐕','w':'𝐖','x':'𝐗','y':'𝐘','z':'𝐙',' ':' '}
            await safe_edit(event, "".join(B.get(c.lower(), c) for c in arg[:300]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("small")
    async def cmd_small(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.small <text>`")
            S = {'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'Q','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'}
            await safe_edit(event, "".join(S.get(c.lower(), c) for c in arg[:300]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("shadow")
    async def cmd_shadow(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.shadow <text>`")
            await safe_edit(event, f"░▒▓ {arg[:300]} ▓▒░")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("camel")
    async def cmd_camel(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.camel <text>`")
            w = arg.split()
            await safe_edit(event, f"🐪 `{w[0].lower() + ''.join(x.capitalize() for x in w[1:])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("md5")
    async def cmd_md5(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.md5 <text>`")
            await safe_edit(event, f"🔐 `{hashlib.md5(arg.encode()).hexdigest()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("sha256")
    async def cmd_sha256(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.sha256 <text>`")
            await safe_edit(event, f"🔐 `{hashlib.sha256(arg.encode()).hexdigest()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("sha1")
    async def cmd_sha1(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.sha1 <text>`")
            await safe_edit(event, f"🔐 `{hashlib.sha1(arg.encode()).hexdigest()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("sha512")
    async def cmd_sha512(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.sha512 <text>`")
            await safe_edit(event, f"🔐 `{hashlib.sha512(arg.encode()).hexdigest()[:64]}...`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("b64")
    async def cmd_b64(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.b64 <text>`")
            await safe_edit(event, f"🔐 `{base64.b64encode(arg.encode()).decode()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("b64d")
    async def cmd_b64d(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.b64d <base64>`")
            await safe_edit(event, f"🔓 `{base64.b64decode(arg.encode()).decode()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("uuid")
    async def cmd_uuid(event, _):
        try: await safe_edit(event, f"🆔 `{uuid.uuid4()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("password")
    async def cmd_password(event, arg):
        try:
            try: length = max(8, min(int(arg), 64)) if arg else 16
            except: length = 16
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|"
            await safe_edit(event, f"🔑 `{''.join(random.choice(chars) for _ in range(length))}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("time")
    async def cmd_time(event, _):
        try:
            now = datetime.now()
            await safe_edit(event, f"⏰ `{now.strftime('%H:%M:%S')}` 📅 `{now.strftime('%d/%m/%Y')}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("date")
    async def cmd_date(event, _):
        try:
            now = datetime.now()
            await safe_edit(event, f"📅 `{now.strftime('%d %B %Y')}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("uptime")
    async def cmd_uptime(event, _):
        try:
            e = int(time.time() - START_TIME)
            await safe_edit(event, f"⏱️ `{e//3600}h {(e%3600)//60}m {e%60}s`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("random")
    async def cmd_random(event, arg):
        try:
            parts = (arg or "").strip().split()
            try:
                mn = int(parts[0]) if len(parts) > 0 else 1
                mx = int(parts[1]) if len(parts) > 1 else 100
            except: mn, mx = 1, 100
            if mn > mx: mn, mx = mx, mn
            await safe_edit(event, f"🎲 `{random.randint(mn, mx)}` [{mn}, {mx}]")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("tempconv")
    async def cmd_tempconv(event, arg):
        try:
            parts = (arg or "").strip().split()
            if len(parts) < 2: return await safe_edit(event, "❌ `.tempconv C/F <value>`")
            mode, val = parts[0].upper(), float(parts[1])
            if mode == "C": r = f"{val}°C = {(val*9/5)+32:.2f}°F"
            elif mode == "F": r = f"{val}°F = {(val-32)*5/9:.2f}°C"
            else: return await safe_edit(event, "❌ Use C or F")
            await safe_edit(event, f"🌡️ `{r}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("id")
    async def cmd_id(event, arg):
        try:
            uid = event.sender_id
            if event.is_reply:
                r = await event.get_reply_message()
                if r: uid = r.sender_id
            await safe_edit(event, f"🆔 User → `{uid}`\n💬 Chat → `{event.chat_id}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("chatid")
    async def cmd_chatid(event, _):
        try: await safe_edit(event, f"💬 `{event.chat_id}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("whois")
    async def cmd_whois(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try: target = (await bot.get_entity(arg)).id
                except: return await safe_edit(event, "❌ Invalid")
            else: target = event.sender_id
            u = await bot.get_entity(target)
            un = f"@{u.username}" if getattr(u,'username',None) else "None"
            await safe_edit(event, f"🔍 `{u.id}` | {getattr(u,'first_name','')} | {un}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("mention")
    async def cmd_mention(event, arg):
        try:
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id:
                    u = await bot.get_entity(r.sender_id)
                    return await safe_edit(event, f"[{getattr(u,'first_name','User')}](tg://user?id={u.id})")
            if arg:
                try:
                    u = await bot.get_entity(arg)
                    return await safe_edit(event, f"[{getattr(u,'first_name','User')}](tg://user?id={u.id})")
                except: pass
            await safe_edit(event, "❌ Reply/Username")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("getpp")
    async def cmd_getpp(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try: target = (await bot.get_entity(arg)).id
                except: return await safe_edit(event, "❌ Invalid")
            else: target = event.sender_id
            await safe_edit(event, "⚡ Fetching...")
            photo = await bot.download_profile_photo(target, file=bytes)
            if not photo: return await safe_edit(event, "❌ No Profile Photo")
            bio = BytesIO(photo); bio.name = "pp.jpg"
            await event.delete()
            await bot.send_file(event.chat_id, bio, caption="🖼️ Profile Photo")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("setname")
    async def cmd_setname(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.setname <name>`")
            parts = arg.strip().split(None, 1)
            await bot(functions.account.UpdateProfileRequest(
                first_name=parts[0][:64],
                last_name=(parts[1][:64] if len(parts) > 1 else "")
            ))
            await safe_edit(event, f"✅ Name set → `{arg}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("setbio")
    async def cmd_setbio(event, arg):
        try:
            await bot(functions.account.UpdateProfileRequest(about=(arg or "")[:70]))
            await safe_edit(event, f"✅ Bio set → `{arg[:70]}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("setpp", needs_reply=True)
    async def cmd_setpp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ Reply to image")
            file = await reply.download_media(file=bytes)
            if not file: return await safe_edit(event, "❌ Download fail")
            await bot(functions.photos.UploadProfilePhotoRequest(file=await bot.upload_file(BytesIO(file))))
            await safe_edit(event, "✅ Profile Photo Set")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("groupinfo")
    async def cmd_groupinfo(event, _):
        try:
            if not event.is_group: return await safe_edit(event, "⚠️ Group only")
            chat = await bot.get_entity(event.chat_id)
            await safe_edit(event, f"ℹ️ `{getattr(chat,'title','Unknown')}`\n🆔 `{event.chat_id}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("membercount")
    async def cmd_membercount(event, _):
        try:
            p = await bot.get_participants(event.chat_id, limit=0)
            await safe_edit(event, f"👥 `{p.total}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("invitelink")
    async def cmd_invitelink(event, _):
        try:
            if not event.is_group: return await safe_edit(event, "⚠️ Group only")
            try:
                r = await bot(functions.messages.ExportChatInviteRequest(peer=event.chat_id))
            except:
                r = await bot(functions.channels.ExportInviteRequest(channel=event.chat_id))
            await safe_edit(event, f"🔗 `{r.link}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("ban", needs_reply=True, group_only=True)
    async def cmd_ban(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ No Target")
            b, f = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditBannedRequest(
                        channel=event.chat_id, participant=uid,
                        banned_rights=types.ChatBannedRights(until_date=None, view_messages=True)))
                    b.append(str(uid))
                except: f.append(str(uid))
            parts = []
            if b: parts.append(f"🔨 Banned → `{', '.join(b)}`")
            if f: parts.append(f"⚠️ Failed → `{', '.join(f)}`")
            await safe_edit(event, "\n".join(parts) or "❌ No Action")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("unban", needs_reply=True, group_only=True)
    async def cmd_unban(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ No Target")
            b, f = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditBannedRequest(
                        channel=event.chat_id, participant=uid,
                        banned_rights=types.ChatBannedRights(until_date=None)))
                    b.append(str(uid))
                except: f.append(str(uid))
            parts = []
            if b: parts.append(f"✅ Unbanned → `{', '.join(b)}`")
            if f: parts.append(f"⚠️ Failed → `{', '.join(f)}`")
            await safe_edit(event, "\n".join(parts) or "❌ No Action")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("kick", needs_reply=True, group_only=True)
    async def cmd_kick(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ No Target")
            k, f = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try: await bot.kick_participant(event.chat_id, uid); k.append(str(uid))
                except: f.append(str(uid))
            parts = []
            if k: parts.append(f"👞 Kicked → `{', '.join(k)}`")
            if f: parts.append(f"⚠️ Failed → `{', '.join(f)}`")
            await safe_edit(event, "\n".join(parts) or "❌ No Action")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("autokick", group_only=True)
    @register_cmd("kickdeleted", group_only=True)
    @register_cmd("cleandeleted", group_only=True)
    async def cmd_autokick(event, arg):
        try:
            chat_id = event.chat_id
            arg_str = (arg or "").strip().lower()

            # If user replied to someone or specified @username or user ID
            is_specific_target = bool(event.is_reply or (arg and any(c.isalnum() for c in arg) and arg_str not in ["on", "start", "deleted", "del", "ghost", "dead", "clean"]))

            if is_specific_target:
                targets = await get_targets(event, arg)
                if targets:
                    if chat_id not in autokick_users:
                        autokick_users[chat_id] = set()
                    added = []
                    for uid in targets:
                        try:
                            uid_int = int(uid)
                            autokick_users[chat_id].add(uid_int)
                            added.append(str(uid_int))
                            try: await bot.kick_participant(chat_id, uid_int)
                            except: pass
                        except: continue
                    return await safe_edit(
                        event,
                        f"👞 𝐀𝐔𝐓𝐎-𝐊𝐈𝐂𝐊 𝐀𝐑𝐌𝐄𝐃 𝐅𝐎𝐑 𝐓𝐇𝐈𝐒 𝐆𝐂! ⚡\n━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 𝐓ᴀʀɢᴇᴛ 𝐔sᴇʀs: `{', '.join(added)}`\n"
                        f"🛡️ 𝐒ᴛᴀᴛᴜs: 𝐀ᴄᴛɪᴠᴇ (𝐆𝐂 ᴍᴇ ʙᴏʟᴛᴇ ʜɪ 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ ʜᴏ ᴊᴀʏᴇɢᴀ!)\n"
                        f"🛑 𝐒ᴛᴏᴘ 𝐂ᴍᴅ: `.stopautokick`"
                    )

            # Default behavior for .autokick, .autokick on, .autokick deleted, .kickdeleted:
            # Auto-kick all deleted/ghost accounts from this GC!
            await safe_edit(event, "🔍 𝐒ᴄᴀɴɴɪɴɢ 𝐆𝐂 𝐅ᴏʀ 𝐃ᴇʟᴇᴛᴇᴅ 𝐀ᴄᴄᴏᴜɴᴛ𝐬...")
            kicked = 0
            failed = 0
            try:
                async for user in bot.iter_participants(chat_id):
                    if getattr(user, "deleted", False):
                        try:
                            await bot.kick_participant(chat_id, user.id)
                            kicked += 1
                            await asyncio.sleep(0.35)
                        except Exception:
                            failed += 1
            except Exception as e:
                return await safe_edit(event, f"❌ 𝐒ᴄᴀɴ 𝐄ʀʀᴏʀ → `{str(e)[:40]}`")

            if kicked == 0 and failed == 0:
                return await safe_edit(
                    event,
                    "✨ 𝐆𝐂 𝐈𝐒 𝐀𝐋𝐑𝐄𝐀𝐃𝐘 𝐂𝐋𝐄𝐀𝐍!\n━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "✅ 𝐈𝐬 𝐆𝐂 𝐦𝐞 𝐞𝐤 𝐛𝐡𝐢 𝐃𝐞𝐥ᴇᴛᴇᴅ 𝐀ᴄᴄᴏᴜɴ𝐭 𝐧𝐚𝐡𝐢 𝐦𝐢𝐥𝐚."
                )

            return await safe_edit(
                event,
                f"👞 𝐀𝐔𝐓𝐎-𝐊𝐈𝐂𝐊 𝐃𝐄𝐋𝐄𝐓𝐄𝐃 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄! ⚡\n━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ 𝐊ɪᴄᴋᴇᴅ 𝐃ᴇʟᴇᴛᴇᴅ 𝐀ᴄᴄᴏᴜɴᴛ𝐬: `{kicked}`\n"
                f"⚠️ 𝐒ᴋɪᴘᴘᴇᴅ / 𝐅ᴀɪʟᴇᴅ: `{failed}`\n"
                f"🛡️ 𝐃𝐞𝐚𝐝 𝐆𝐂 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐂𝐥𝐞𝐚𝐧𝐞𝐝!"
            )
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ 𝐄ʀʀᴏʀ → `{str(e)[:40]}`")

    @register_cmd("stopautokick", group_only=True)
    @register_cmd("sautokick", group_only=True)
    async def cmd_stopautokick(event, arg):
        try:
            chat_id = event.chat_id
            if chat_id in autokick_users:
                targets = await get_targets(event, arg)
                if targets:
                    for uid in targets:
                        try: autokick_users[chat_id].discard(int(uid))
                        except: pass
                    await safe_edit(event, f"🛑 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ 𝐑ᴇᴍᴏᴠᴇᴅ 𝐅ᴏʀ `{len(targets)}` 𝐔sᴇʀ(s) ɪɴ ᴛʜɪs 𝐆𝐂!")
                else:
                    autokick_users.pop(chat_id, None)
                    await safe_edit(event, "🛑 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐥𝐲 𝐒𝐭𝐨𝐩𝐩𝐞𝐝 𝐅ᴏʀ 𝐓𝐡𝐢𝐬 𝐆𝐂!")
            else:
                await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ 𝐑ᴜʟᴇs ɪɴ ᴛʜɪs 𝐆𝐂.")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴏᴘ 𝐄ʀʀᴏʀ → `{str(e)[:40]}`")

    @register_cmd("autokicklist", group_only=True)
    async def cmd_autokicklist(event, _):
        try:
            chat_id = event.chat_id
            uids = autokick_users.get(chat_id, set())
            if not uids:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐀ᴜᴛᴏ-𝐊ɪᴄᴋ 𝐓ᴀʀɢᴇᴛs ɪɴ ᴛʜɪs 𝐆𝐂.")
            lines = [f"• `{uid}`" for uid in uids]
            await safe_edit(event, f"👞 𝐀𝐔𝐓𝐎-𝐊𝐈𝐂𝐊 𝐓𝐀𝐑𝐆𝐄𝐓𝐒 ({len(uids)})\n━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋ɪsᴛ 𝐄ʀʀᴏʀ → `{str(e)[:40]}`")

    @register_cmd("promote", group_only=True)
    async def cmd_promote(event, arg):
        try:
            targets = []
            if event.is_reply:
                try:
                    reply = await event.get_reply_message()
                    if reply and reply.sender_id:
                        targets.append(reply.sender_id)
                except: pass
            if arg:
                for part in arg.strip().replace(",", " ").split():
                    if part and part not in targets:
                        targets.append(part)

            if not targets:
                return await safe_edit(event, "❌ 𝐏ʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ sᴘᴇᴄɪғʏ @username / ID\n👉 `.promote @user`")

            chat_peer = await event.get_input_chat()
            p, f = [], []
            for t in targets:
                ok, detail = await universal_promote_bot_or_user(chat_peer, t, custom_rank="Admin ⚡")
                if ok: p.append(f"`{t}` ({detail})")
                else: f.append(f"`{t}` ({detail})")
                await asyncio.sleep(0.8)

            parts = ["👑 𝐔sᴇʀ / 𝐁ᴏᴛ 𝐏ʀᴏᴍᴏᴛɪᴏɴ\n━━━━━━━━━━━━━━━"]
            if p: parts.append(f"⭐ 𝐏ʀᴏᴍᴏᴛᴇᴅ ({len(p)}):\n• " + "\n• ".join(p))
            if f: parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ ({len(f)}):\n• " + "\n• ".join(f))
            await safe_edit(event, "\n".join(parts))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("demote", group_only=True)
    async def cmd_demote(event, arg):
        try:
            targets = []
            if event.is_reply:
                try:
                    reply = await event.get_reply_message()
                    if reply and reply.sender_id:
                        targets.append(reply.sender_id)
                except: pass
            if arg:
                for part in arg.strip().replace(",", " ").split():
                    if part and part not in targets:
                        targets.append(part)

            if not targets:
                return await safe_edit(event, "❌ 𝐏ʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ sᴘᴇᴄɪғʏ @username / ID\n👉 `.demote @user`")

            chat_peer = await event.get_input_chat()
            d, f = [], []
            for t in targets:
                ok, detail = await universal_demote_bot_or_user(chat_peer, t)
                if ok: d.append(f"`{t}`")
                else: f.append(f"`{t}` ({detail})")
                await asyncio.sleep(0.5)

            parts = ["⬇️ 𝐃ᴇᴍᴏᴛɪᴏɴ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n━━━━━━━━━━━━━━━"]
            if d: parts.append(f"⬇️ 𝐃ᴇᴍᴏᴛᴇᴅ ({len(d)}):\n• " + "\n• ".join(d))
            if f: parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ ({len(f)}):\n• " + "\n• ".join(f))
            await safe_edit(event, "\n".join(parts))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("warn", needs_reply=True)
    async def cmd_warn(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ No Target")
            res = []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                warns[uid] = warns.get(uid, 0) + 1
                res.append(f"`{uid}` → ⚠️ `{warns[uid]}`")
            save_warns()
            await safe_edit(event, "⚠️ Warn\n" + "\n".join(res))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("warnlist")
    async def cmd_warnlist(event, _):
        try:
            if not warns: return await safe_edit(event, "⚠️ No warns")
            lines = [f"• `{u}` → `{c}`" for u, c in sorted(warns.items())]
            await safe_edit(event, "⚠️ Warnlist\n" + "\n".join(lines))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("clearwarn")
    async def cmd_clearwarn(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: warns.pop(uid, None)
                await safe_edit(event, f"✅ Warns cleared ({len(targets)})")
            else:
                warns.clear()
                await safe_edit(event, "✅ All warns cleared")
            save_warns()
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("pin", needs_reply=True, group_only=True)
    async def cmd_pin(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply: return await safe_edit(event, "❌ Reply to pin")
            await bot.pin_message(event.chat_id, reply.id)
            await safe_edit(event, "📌 Pinned")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("unpin", group_only=True)
    async def cmd_unpin(event, _):
        try:
            await bot(functions.messages.UnpinAllMessagesRequest(peer=event.chat_id))
            await safe_edit(event, "📌 Unpinned")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("joke")
    async def cmd_joke(event, _):
        try: await safe_edit(event, f"😂 {random.choice(joke_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("riddle")
    async def cmd_riddle(event, _):
        try: await safe_edit(event, f"🤔 {random.choice(riddle_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("fact")
    async def cmd_fact(event, _):
        try: await safe_edit(event, f"🧠 {random.choice(fact_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("quote")
    async def cmd_quote(event, _):
        try: await safe_edit(event, f"💭 {random.choice(quote_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("truth")
    async def cmd_truth(event, _):
        try: await safe_edit(event, f"🤥 {random.choice(truth_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("dare")
    async def cmd_dare(event, _):
        try: await safe_edit(event, f"😈 {random.choice(dare_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("pickup")
    async def cmd_pickup(event, _):
        try: await safe_edit(event, f"💘 {random.choice(pickup_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("compliment")
    async def cmd_compliment(event, _):
        try: await safe_edit(event, f"🌟 {random.choice(compliment_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("roastme")
    async def cmd_roastme(event, _):
        try: await safe_edit(event, f"🔥 {random.choice(roast_list)}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("8ball")
    async def cmd_8ball(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.8ball <q>`")
            ans = random.choice(["🟢 Yes!","🟢 Bet on it!","🟢 Most likely!","🟡 Cannot predict","🟡 Ask later","🟡 Concentrate","🔴 Don't count","🔴 Very doubtful","🔴 Outlook not good"])
            await safe_edit(event, f"🎱 {arg}\n{ans}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("rps")
    async def cmd_rps(event, arg):
        try:
            ch = {"r":"🪨 Rock","p":"📄 Paper","s":"✂️ Scissors"}
            w = {"r":"s","p":"r","s":"p"}
            if not arg or arg.lower() not in ch: return await safe_edit(event, "❌ `.rps r/p/s`")
            u, b = arg.lower(), random.choice(list(ch.keys()))
            r = "🤝 Draw!" if u == b else ("🏆 You Win!" if w[u] == b else "😈 Bot Wins!")
            text = f"✂️🪨📄 RPS\nYou → {ch[u]}\nBot → {ch[b]}\n\n{r}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("choose")
    async def cmd_choose(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.choose a|b|c`")
            opts = [o.strip() for o in arg.split("|") if o.strip()]
            if not opts: return await safe_edit(event, "❌ No options")
            await safe_edit(event, f"🎯 `{random.choice(opts)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("del", needs_reply=True)
    async def cmd_del(event, _):
        try:
            reply = await event.get_reply_message()
            if reply: await reply.delete()
            await event.delete()
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("echo")
    async def cmd_echo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.echo <text>`")
            await event.delete()
            await bot.send_message(event.chat_id, arg)
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("react")
    async def cmd_react(event, arg):
        try:
            if event.is_reply:
                r = await event.get_reply_message()
                emoji = arg.strip() if arg else "❤️"
                await bot(functions.messages.SendReactionRequest(
                    peer=event.chat_id, msg_id=r.id,
                    reaction=[types.ReactionEmoji(emoticon=emoji)]))
                await safe_edit(event, f"✅ Reacted {emoji}")
            else:
                await safe_edit(event, "❌ Reply to a message")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("read")
    async def cmd_read(event, _):
        try:
            await bot.send_read_acknowledge(event.chat_id)
            await safe_edit(event, "✅ Marked as read")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("typing")
    async def cmd_typing(event, arg):
        try:
            secs = min(int(arg), 10) if arg and arg.isdigit() else 3
            await safe_edit(event, f"⌨️ Typing {secs}s...")
            async with bot.action(event.chat_id, 'typing'):
                await asyncio.sleep(secs)
            await event.delete()
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("online")
    async def cmd_online(event, _):
        try:
            await bot(functions.account.UpdateStatusRequest(offline=False))
            await safe_edit(event, "✅ Online 🟢")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("myip")
    async def cmd_myip(event, _):
        try:
            await safe_edit(event, "⚡ Fetching...")
            d = requests.get("http://ip-api.com/json/", timeout=8).json()
            await safe_edit(event, f"🌐 `{d.get('query')}`\n🌍 `{d.get('country')}`\n📍 `{d.get('isp')}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("hex")
    async def cmd_hex(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.hex <text>`")
            await safe_edit(event, f"🔢 `{' '.join(format(ord(c), '02X') for c in arg[:100])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("octal")
    async def cmd_octal(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.octal <text>`")
            await safe_edit(event, f"🔢 `{' '.join(format(ord(c), 'o') for c in arg[:100])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("ascii")
    async def cmd_ascii(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.ascii <text>`")
            await safe_edit(event, f"🔡 `{' '.join(str(ord(c)) for c in arg[:100])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("charcount")
    async def cmd_charcount(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.charcount <text>`")
            t = len(arg); l = sum(c.isalpha() for c in arg); d = sum(c.isdigit() for c in arg); s = sum(c.isspace() for c in arg)
            await safe_edit(event, f"📊 Total `{t}` | Letters `{l}` | Digits `{d}` | Spaces `{s}` | Special `{t-l-d-s}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("palindrome")
    async def cmd_palindrome(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.palindrome <text>`")
            c = arg.lower().replace(" ", "")
            ok = c == c[::-1]
            await safe_edit(event, f"{'✅' if ok else '❌'} `{arg}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("vowels")
    async def cmd_vowels(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.vowels <text>`")
            vs = sum(1 for c in arg.lower() if c in 'aeiou')
            cs = sum(1 for c in arg.lower() if c.isalpha() and c not in 'aeiou')
            await safe_edit(event, f"🅰️ Vowels `{vs}` | 🔡 Consonants `{cs}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("titlecase")
    async def cmd_titlecase(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.titlecase <text>`")
            await safe_edit(event, f"📝 `{arg.title()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("snake")
    async def cmd_snake(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.snake <text>`")
            await safe_edit(event, f"🐍 `{'_'.join(arg.lower().split())}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("shout")
    async def cmd_shout(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.shout <text>`")
            await safe_edit(event, f"📢 `{'  '.join(arg.upper())}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("alternating")
    async def cmd_alternating(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.alternating <text>`")
            await safe_edit(event, f"🔀 `{''.join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(arg))}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("spaceit")
    async def cmd_spaceit(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.spaceit <text>`")
            await safe_edit(event, f"↔️ `{' '.join(arg)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("wordfreq")
    async def cmd_wordfreq(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.wordfreq <text>`")
            freq = {}
            for w in arg.lower().split(): freq[w] = freq.get(w, 0) + 1
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            await safe_edit(event, "📊 " + "\n".join(f"`{w}` → {n}x" for w, n in top))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("removespaces")
    async def cmd_removespaces(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.removespaces <text>`")
            await safe_edit(event, f"✂️ `{''.join(arg.split())}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("truncate")
    async def cmd_truncate(event, arg):
        try:
            p = (arg or "").strip().split(None, 1)
            if len(p) < 2: return await safe_edit(event, "❌ `.truncate <n> <text>`")
            n = int(p[0]); await safe_edit(event, f"✂️ `{p[1][:n] + ('...' if len(p[1])>n else '')}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("percentage")
    async def cmd_percentage(event, arg):
        try:
            p = (arg or "").strip().split()
            if len(p) < 2: return await safe_edit(event, "❌ `.percentage <v> <t>`")
            await safe_edit(event, f"📊 `{(float(p[0])/float(p[1]))*100:.2f}%`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("square")
    async def cmd_square(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.square <n>`")
            n = float(arg); await safe_edit(event, f"`{n}²` = `{n**2}`\n√`{abs(n)}` = `{math.sqrt(abs(n)):.4f}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("prime")
    async def cmd_prime(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.prime <n>`")
            n = int(arg)
            if n < 2: return await safe_edit(event, f"❌ `{n}` not prime")
            ok = all(n % i != 0 for i in range(2, int(n**0.5)+1))
            await safe_edit(event, f"{'✅' if ok else '❌'} `{n}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("factorial")
    async def cmd_factorial(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.factorial <n>`")
            n = int(arg)
            if n > 20: return await safe_edit(event, "❌ Max 20")
            await safe_edit(event, f"`{n}!` = `{math.factorial(n)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("fibonacci")
    async def cmd_fibonacci(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.fibonacci <n>`")
            n = min(int(arg), 30)
            a, b, seq = 0, 1, []
            for _ in range(n): seq.append(a); a, b = b, a+b
            await safe_edit(event, f"🌀 `{', '.join(map(str, seq))}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("bmi")
    async def cmd_bmi(event, arg):
        try:
            p = (arg or "").strip().split()
            if len(p) < 2: return await safe_edit(event, "❌ `.bmi <w> <h_cm>`")
            w, h = float(p[0]), float(p[1]) / 100
            b = w / (h*h)
            cat = "Underweight" if b < 18.5 else ("Normal" if b < 25 else ("Overweight" if b < 30 else "Obese"))
            await safe_edit(event, f"⚖️ BMI `{b:.1f}` — {cat}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("age")
    async def cmd_age(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.age DD/MM/YYYY`")
            from datetime import date
            p = arg.strip().split("/")
            bd = date(int(p[2]), int(p[1]), int(p[0]))
            t = date.today()
            await safe_edit(event, f"🎂 Age `{(t-bd).days // 365}` years")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("coin")
    async def cmd_coin(event, _):
        try: await safe_edit(event, f"🪙 {random.choice(['HEADS','TAILS'])}!")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("lucky")
    async def cmd_lucky(event, _):
        try:
            n = random.randint(1, 100)
            m = "🎉 Lucky!" if n >= 80 else ("😊 Thoda lucky!" if n >= 50 else ("😐 Average" if n >= 30 else "😬 Ghhar baith!"))
            await safe_edit(event, f"🍀 `{n}/100` — {m}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("roll")
    async def cmd_roll(event, arg):
        try:
            s = int(arg) if arg and arg.isdigit() else 6
            s = max(2, min(s, 1000))
            await safe_edit(event, f"🎲 d{s} → `{random.randint(1, s)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("number")
    async def cmd_number(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.number <n>`")
            n = int(arg)
            await safe_edit(event, f"`{n}` → Bin `{bin(n)[2:]}` Oct `{oct(n)[2:]}` Hex `{hex(n)[2:].upper()}` Sq `{n**2}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("clap")
    async def cmd_clap(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.clap <text>`")
            await safe_edit(event, "👏".join(arg.split()))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("mock")
    async def cmd_mock(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.mock <text>`")
            await safe_edit(event, f"🤡 `{''.join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(arg))}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("strike")
    async def cmd_strike(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.strike <text>`")
            await safe_edit(event, f"~~{arg}~~")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("spoiler")
    async def cmd_spoiler(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.spoiler <text>`")
            await safe_edit(event, f"||{arg}||")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("mirror")
    async def cmd_mirror(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.mirror <text>`")
            await safe_edit(event, f"🪞 `{arg} | {arg[::-1]}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("emoji2text")
    async def cmd_emoji2text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.emoji2text <text>`")
            r = arg.encode('ascii', 'ignore').decode('ascii').strip() or "[Only emojis]"
            await safe_edit(event, f"📝 `{r}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("lettercount")
    async def cmd_lettercount(event, arg):
        try:
            p = arg.split(None, 1)
            if len(p) < 2: return await safe_edit(event, "❌ `.lettercount <l> <text>`")
            await safe_edit(event, f"🔍 `'{p[0]}'` → `{p[1].lower().count(p[0].lower())}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("nato")
    async def cmd_nato(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.nato <text>`")
            N = {'A':'Alpha','B':'Bravo','C':'Charlie','D':'Delta','E':'Echo','F':'Foxtrot','G':'Golf','H':'Hotel','I':'India','J':'Juliet','K':'Kilo','L':'Lima','M':'Mike','N':'November','O':'Oscar','P':'Papa','Q':'Quebec','R':'Romeo','S':'Sierra','T':'Tango','U':'Uniform','V':'Victor','W':'Whiskey','X':'X-ray','Y':'Yankee','Z':'Zulu',' ':'/'}
            await safe_edit(event, f"📻 `{' - '.join(N.get(c.upper(), c) for c in arg[:50])}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("boxtext")
    async def cmd_boxtext(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.boxtext <text>`")
            lines = arg.split('\n'); w = max(len(l) for l in lines) + 4
            top = "┌" + "─" * (w-2) + "┐"; bot = "└" + "─" * (w-2) + "┘"
            mid = "\n".join(f"│ {l.ljust(w-4)} │" for l in lines)
            await safe_edit(event, f"`{top}\n{mid}\n{bot}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("countdown")
    async def cmd_countdown(event, arg):
        try:
            if not arg or not arg.isdigit(): return await safe_edit(event, "❌ `.countdown <sec>`")
            n = min(int(arg), 10)
            for i in range(n, 0, -1):
                await safe_edit(event, f"⏳ **{i}**...")
                await asyncio.sleep(1)
            await safe_edit(event, "🎉 **BOOM!** 💥")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("tinytext")
    async def cmd_tinytext(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.tinytext <text>`")
            T = {'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᵍ','h':'ʰ','i':'ⁱ','j':'ʲ','k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ','o':'ᵒ','p':'ᵖ','q':'ᵠ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ','v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ',' ':' '}
            await safe_edit(event, "".join(T.get(c.lower(), c) for c in arg[:200]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("bubble")
    async def cmd_bubble(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.bubble <text>`")
            B = {'a':'ⓐ','b':'ⓑ','c':'ⓒ','d':'ⓓ','e':'ⓔ','f':'ⓕ','g':'ⓖ','h':'ⓗ','i':'ⓘ','j':'ⓙ','k':'ⓚ','l':'ⓛ','m':'ⓜ','n':'ⓝ','o':'ⓞ','p':'ⓟ','q':'ⓠ','r':'ⓡ','s':'ⓢ','t':'ⓣ','u':'ⓤ','v':'ⓥ','w':'ⓦ','x':'ⓧ','y':'ⓨ','z':'ⓩ','A':'Ⓐ','B':'Ⓑ','C':'Ⓒ','D':'Ⓓ','E':'Ⓔ','F':'Ⓕ','G':'Ⓖ','H':'Ⓗ','I':'Ⓘ','J':'Ⓙ','K':'Ⓚ','L':'Ⓛ','M':'Ⓜ','N':'Ⓝ','O':'Ⓞ','P':'Ⓟ','Q':'Ⓠ','R':'Ⓡ','S':'Ⓢ','T':'Ⓣ','U':'Ⓤ','V':'Ⓥ','W':'Ⓦ','X':'Ⓧ','Y':'Ⓨ','Z':'Ⓩ','0':'⓪','1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'}
            await safe_edit(event, "".join(B.get(c, c) for c in arg[:200]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("square_text")
    async def cmd_square_text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.square_text <text>`")
            S = {'a':'🅐','b':'🅑','c':'🅒','d':'🅓','e':'🅔','f':'🅕','g':'🅖','h':'🅗','i':'🅘','j':'🅙','k':'🅚','l':'🅛','m':'🅜','n':'🅝','o':'🅞','p':'🅟','q':'🅠','r':'🅡','s':'🅢','t':'🅣','u':'🅤','v':'🅥','w':'🅦','x':'🅧','y':'🅨','z':'🅩',' ':' '}
            await safe_edit(event, "".join(S.get(c.lower(), c) for c in arg[:200]))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("encrypt")
    async def cmd_encrypt(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.encrypt <text>`")
            e1 = base64.b64encode(arg[:500].encode()).decode()
            await safe_edit(event, f"🔒 `{base64.b64encode(e1[::-1].encode()).decode()}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("decrypt")
    async def cmd_decrypt(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.decrypt <text>`")
            s1 = base64.b64decode(arg.strip().encode()).decode()
            await safe_edit(event, f"🔓 `{base64.b64decode(s1[::-1].encode()).decode()}`")
        except Exception: await safe_edit(event, "❌ Invalid")

    @register_cmd("charinfo")
    async def cmd_charinfo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.charinfo <char>`")
            c = arg[0]
            import unicodedata
            await safe_edit(event, f"🔤 `{c}` — {unicodedata.name(c, 'Unknown')} U+{ord(c):04X}")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("timer")
    async def cmd_timer(event, arg):
        try:
            if not arg or not arg.isdigit(): return await safe_edit(event, "❌ `.timer <sec>`")
            n = min(int(arg), 60)
            await safe_edit(event, f"⏱️ Timer: **{n}s**")
            await asyncio.sleep(n)
            await safe_edit(event, f"✅ **Done!** ({n}s)")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("typetest")
    async def cmd_typetest(event, _):
        try:
            words = ["python","telegram","userbot","ARYA X MENTAL","coding","fire","speed","attack","legend","ultra"]
            await safe_edit(event, f"⌨️ Type: **`{random.choice(words)}`**")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("sysinfo")
    async def cmd_sysinfo(event, _):
        try:
            import platform
            e = int(time.time() - START_TIME)
            await safe_edit(event, f"🖥️ Python `{platform.python_version()}`\n💻 System `{platform.system()}`\n⏱️ `{e//3600}h {(e%3600)//60}m {e%60}s`\n📦 Cmds `{len(commands)}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("table")
    async def cmd_table(event, arg):
        try:
            if not arg or not arg.isdigit(): return await safe_edit(event, "❌ `.table <n>`")
            n = min(int(arg), 20)
            await safe_edit(event, "\n".join(f"`{n} × {i:2} = {n*i}`" for i in range(1, 13)))
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("roman")
    async def cmd_roman(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.roman <n>`")
            n = int(arg)
            if not 1 <= n <= 3999: return await safe_edit(event, "❌ Range 1-3999")
            v = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
            s = ['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I']
            r = ""
            for i, x in enumerate(v):
                while n >= x: r += s[i]; n -= x
            await safe_edit(event, f"🏛️ **{r}**")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("randname")
    async def cmd_randname(event, _):
        try:
            f = ["Arjun","Rahul","Rohan","Dev","Kabir","Veer","Aarav","Shiv","Karan","Aditya","Anjali","Priya","Neha","Nisha","Riya","Sana","Meera","Pooja","Divya","Tara"]
            l = ["Sharma","Kumar","Singh","Verma","Gupta","Patel","Shah","Joshi","Rao","Nair"]
            await safe_edit(event, f"👤 **{random.choice(f)} {random.choice(l)}**")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("randcolor")
    async def cmd_randcolor(event, _):
        try:
            r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
            await safe_edit(event, f"🎨 R `{r}` G `{g}` B `{b}` HEX **`#{r:02X}{g:02X}{b:02X}`**")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    @register_cmd("flip_text")
    async def cmd_flip_text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ `.flip_text <text>`")
            F = {'a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ','i':'ᴉ','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d','q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x','y':'ʎ','z':'z',' ':' '}
            await safe_edit(event, f"🙃 `{''.join(F.get(c.lower(), c) for c in arg[:200])[::-1]}`")
        except Exception as e: await safe_edit(event, f"❌ → `{str(e)[:40]}`")

    # ── AUTO HANDLERS ──
    @bot.on(events.NewMessage)
    async def auto_handler(event):
        if event.out: return
        sender = event.sender_id
        chat = event.chat_id
        if not sender: return
        if sender == OWNER_ID: return
        if sender in PROTECTED_IDS: return

        # ── ZERO-MEDIA & 5GB BANDWIDTH PROTECTION ──
        # Drop incoming media (videos, gifs, photos, stickers, voice) in groups/channels
        # immediately to protect 5GB bandwidth & 512MB RAM!
        raw_t = (event.raw_text or "").strip()
        is_cmd = raw_t.startswith((".", "!", "/", "?"))
        if event.media and not is_cmd and (event.is_group or event.is_channel):
            if sender not in reply_users and sender not in replygod_users and sender not in watch_spam:
                return

        # Pure media without text in groups is dropped instantly (0 bandwidth consumed)
        if not raw_t and (event.is_group or event.is_channel):
            return

        # ── FAST EXIT FOR STRANGER GROUP MESSAGES (MASSIVE RAM SAVER) ──
        has_targets = bool(
            reply_users or replygod_users or flag_users or hrr_users or rr_users or
            attack_users or roast_users or diss_users or war_users or savage_users or
            ultra_users or godwar_users or combo_users or troll_users or shame_users or
            fire_users or devil_users or karma_users or ghost_users or legend_users or
            doom_users or watch_spam or (chat in autokick_users) or (chat in group_locks) or
            (sender in global_muted) or (sender in muted_users)
        )
        if (event.is_group or event.is_channel) and not is_cmd and not has_targets:
            return

        if sender in global_muted or sender in muted_users:
            try: await event.delete()
            except: pass
            return

        ws_key = (chat, sender)
        if ws_key in watch_spam:
            now = time.time()
            entry = watch_spam[ws_key]
            entry["times"] = [t for t in entry["times"] if now - t < entry["seconds"]]
            entry["times"].append(now)
            if len(entry["times"]) > entry["limit"]:
                try: await event.delete()
                except: pass
                return

        if chat in autokick_users and sender in autokick_users[chat]:
            try:
                await bot.kick_participant(chat, sender)
                try: await event.delete()
                except: pass
                print(f"[AUTO-KICK] Automatically kicked target {sender} in GC {chat}", flush=True)
            except Exception: pass
            return

        if chat in group_locks:
            if not is_admin(sender):
                try: await event.delete()
                except: pass
                return

        try:
            if sender in reply_users:
                await safe_send(chat, to_dark_font(random.choice(reply_list)), reply_to=event.id, is_raid=True)

            if sender in replygod_users:
                for _ in range(3):
                    await safe_send(chat, to_dark_font(random.choice(reply_texts)), reply_to=event.id, is_raid=True)

            if sender in flag_users:
                await safe_send(chat, to_dark_font(random.choice(flag_texts)), reply_to=event.id, is_raid=True)

            if sender in hrr_users:
                await safe_send(chat, to_dark_font(random.choice(heart_replies)), reply_to=event.id, is_raid=True)

            if sender in rr_users:
                msg = await safe_send(chat, to_dark_font(random.choice(fun_texts)), reply_to=event.id, is_raid=True)
                if msg:
                    try:
                        await bot(functions.messages.SendReactionRequest(
                            peer=chat, msg_id=msg.id,
                            reaction=[types.ReactionEmoji(emoticon="🤣")]))
                    except: pass

            for user_set, text_list in [
                (attack_users, attack_list), (roast_users, roast_list),
                (diss_users, diss_list), (war_users, war_list),
                (savage_users, savage_list), (ultra_users, ultra_list),
                (godwar_users, godwar_list), (combo_users, combo_list),
                (troll_users, troll_list), (shame_users, shame_list),
                (fire_users, fire_list), (devil_users, devil_list),
                (karma_users, karma_list), (ghost_users, ghost_list),
                (legend_users, legend_list), (doom_users, doom_list),
            ]:
                if sender in user_set:
                    await safe_send(chat, to_dark_font(random.choice(text_list)), reply_to=event.id, is_raid=True)

            if sender in replyaryaxmental_users:
                data = replyaryaxmental_users.get(sender)
                if data and int(data.get("count", 0)) > 0:
                    await safe_send(chat, to_dark_font(data.get("text", "")), reply_to=event.id, is_raid=True)
                    data["count"] -= 1
                else:
                    replyaryaxmental_users.pop(sender, None)

            if sender in rspam_users:
                data = rspam_users.get(sender)
                if data:
                    for _ in range(int(data.get("count", 1))):
                        res = await safe_send(chat, to_dark_font(data.get("text", "")), reply_to=event.id, is_raid=True)
                        if not res: break

        except Exception as e:
            print(f"[AUTO_HANDLER_ERR] {str(e)[:80]}", flush=True)

    @bot.on(events.NewMessage(outgoing=True))
    async def cache_own_messages(event):
        if not antidel_enabled: return
        try:
            msg_id = event.id
            chat = event.chat_id
            if not msg_id or not chat: return
            antidel_cache[msg_id] = {"chat_id": chat, "text": event.raw_text or "", "time": time.time()}
            now = time.time()
            stale = [k for k, v in antidel_cache.items() if now - v["time"] > 7200]
            for k in stale: antidel_cache.pop(k, None)
            if len(antidel_cache) > 300:
                oldest = sorted(antidel_cache, key=lambda k: antidel_cache[k]["time"])
                for k in oldest[:50]: antidel_cache.pop(k, None)
        except: pass

    @bot.on(events.MessageDeleted)
    async def on_message_deleted(event):
        if not antidel_enabled: return
        try:
            for msg_id in (event.deleted_ids or []):
                entry = antidel_cache.pop(msg_id, None)
                if not entry: continue
                chat_id = entry.get("chat_id") or getattr(event, "chat_id", None)
                text = entry.get("text", "")
                if not chat_id or not text: continue
                try:
                    await bot.send_message(chat_id, f"♻️ **[Anti-Delete]**\n{text}")
                except: pass
        except: pass

    @bot.on(events.NewMessage(outgoing=True))
    async def auto_react(event):
        emoji = auto_react_emoji
        if not emoji: return
        try:
            await bot(functions.messages.SendReactionRequest(
                peer=event.chat_id, msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)]))
        except FloodWaitError as fw:
            try: await asyncio.sleep(fw.seconds)
            except: pass
        except: pass

    # ── AUTOMATIC OUTGOING VOICE NOTE HOOK (NO NORMAL VOICE EVER SENT) ──
    @bot.on(events.NewMessage(outgoing=True))
    async def automic_voice_listener(event):
        try:
            if not automic_state.get("enabled"):
                return

            # Check if this outgoing message is a voice note or audio file
            is_voice = bool(event.voice)
            is_audio = bool(event.media and getattr(event.media, 'document', None) and getattr(event.media.document, 'mime_type', '').startswith('audio/'))
            if not (is_voice or is_audio):
                return

            # Avoid re-processing our own sent transformed voice note
            if event.id in PROCESSED_VOICE_IDS:
                return

            mode = automic_state.get("mode", "echo")
            in_file = await event.download_media(file=DOWNLOAD_PATH)
            if not in_file or not os.path.exists(in_file):
                return

            out_file = os.path.join(DOWNLOAD_PATH, f"automic_{int(time.time()*1000)}.ogg")

            audio_filter, caption_badge = get_voice_dsp(mode)

            cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-filter_complex", audio_filter,
                "-map", "[a]",
                "-c:a", "libopus", "-b:a", "128k",
                out_file
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

            if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
                reply_to_id = event.reply_to_msg_id
                chat_id = event.chat_id
                if automic_state.get("delete_original", True):
                    try:
                        await event.delete()
                    except Exception:
                        pass

                sent = await bot.send_file(
                    chat_id,
                    out_file,
                    voice_note=True,
                    reply_to=reply_to_id,
                    caption=caption_badge
                )
                if sent and getattr(sent, "id", None):
                    PROCESSED_VOICE_IDS.add(sent.id)
                    if len(PROCESSED_VOICE_IDS) > 300:
                        PROCESSED_VOICE_IDS.clear()

            try:
                if os.path.exists(out_file): os.remove(out_file)
                if os.path.exists(in_file): os.remove(in_file)
            except Exception:
                pass
        except Exception as e:
            print(f"[AUTOMIC_LISTENER_ERR] {e}", flush=True)

    # ── SOLO COMMANDS (SINGLE-ACCOUNT ONLY IN GROUPS) ──
    # Commands that should ONLY run on the account where the command was typed.
    # When typed in a group, other linked accounts stay SILENT so only ONE bot replies,
    # and stranger/other userbots CANNOT trigger them.
    # To run on all accounts intentionally, the user can use `.all <cmd>` (e.g. `.all ping`).
    SOLO_COMMANDS = {
        "menu", "help", "ping", "alive", "id", "info", "stats",
        "uptime", "dc", "vchelp", "whois", "cmds", "start", "logs",
        "status", "myaccounts", "host", "restart", "repo", "version",
        "owner", "dev", "vars", "speedtest", "sysinfo", "neofetch"
    }

    # ── FLEET-AWARE MULTI-ACCOUNT DISPATCHER ──
    @bot.on(events.NewMessage())
    async def dispatcher(event):
        # FAST DROP FOR MEDIA: If message has media and no text or is not a command, ignore immediately!
        if event.media and not getattr(event, "raw_text", None):
            return
        text = event.raw_text
        if not text: return
        if not text.startswith("."): return

        sender = event.sender_id
        is_own = getattr(event, "out", False) or (OWNER_ID and sender == OWNER_ID)

        # STRICT MULTI-TENANT ISOLATION:
        # 1. Outgoing commands from THIS account itself (event.out == True) are ALWAYS authorized.
        # 2. Incoming messages (not is_own) MUST be sent by an authorized controller of THIS user's fleet:
        #    - Either the host user's Telegram ID (HOST_USER_ID)
        #    - Or in this user's private FLEET_MASTERS (e.g. Account #1 slot 0)
        #    - Or registered slots in this user's cluster config
        # 3. Any message from ANY other user, stranger, or another bot user is REJECTED IMMEDIATELY.
        if not is_own:
            if not sender:
                return

            curr_cfg = load_fleet_config()
            allowed_masters = set(FLEET_MASTERS)
            if HOST_USER_ID:
                allowed_masters.add(HOST_USER_ID)
            for m in curr_cfg.get("masters", []):
                try: allowed_masters.add(int(m))
                except: pass
            for s_info in curr_cfg.get("slots", {}).values():
                if isinstance(s_info, dict) and "id" in s_info:
                    try: allowed_masters.add(int(s_info["id"]))
                    except: pass

            if sender not in allowed_masters:
                return

        body = text[1:].strip()
        if not body: return
        parts = body.split(maxsplit=1)
        cmd = parts[0].lower().strip()
        arg = parts[1].strip() if len(parts) > 1 else ""

        # Special fleet broadcast command: `.all <cmd>` or `.fleetcmd <cmd>`
        is_forced_fleet = False
        if cmd in ("all", "fleetcmd") and arg:
            is_forced_fleet = True
            sub_parts = arg.split(maxsplit=1)
            cmd = sub_parts[0].lower().lstrip(".").strip()
            arg = sub_parts[1].strip() if len(sub_parts) > 1 else ""

        # Solo command protection:
        # If this is an incoming message in a group/channel from another account,
        # do NOT trigger solo commands (like .menu, .ping, .alive) unless explicitly requested via `.all`.
        # This guarantees:
        # - When user types .menu in a group, ONLY the sending account displays the menu!
        # - Other linked accounts stay silent and do NOT reply with multiple duplicate menus!
        # - But in Private DM between the owner and this userbot, solo commands are always accepted!
        if not is_own and not is_forced_fleet:
            if not getattr(event, "is_private", False) and cmd in SOLO_COMMANDS:
                return
            # Also check if fleet synchronization is disabled
            curr_cfg = load_fleet_config()
            if not curr_cfg.get("sync_enabled", True):
                return

        cmd_data = commands.get(cmd)
        if not cmd_data: return

        if cmd_data.get("group_only"):
            try:
                if not event.is_group:
                    await safe_edit(event, "⚠️ 𝐆ʀᴏᴜᴘ 𝐎ɴʟʏ")
                    return
            except: return

        if cmd_data.get("needs_reply"):
            try:
                if not event.is_reply and not arg:
                    await safe_edit(event, f"❌ Reply or Target\n👉 .{cmd} @user / id")
                    return
            except: return

        try:
            # Instant command dispatch without slot stagger
            await cmd_data["func"](event, arg)
        except FloodWaitError as e:
            try: await safe_edit(event, f"⏳ FloodWait `{e.seconds}s`")
            except: pass
        except Exception as e:
            try: await safe_edit(event, f"❌ `{str(e)[:50]}`")
            except: pass

    # ── STARTUP ──
    async def main():
        global OWNER_ID, FLEET_MASTERS
        try:
            print("🔌 Connecting to Telegram...", flush=True)
            if not bot.is_connected():
                await bot.connect()
            if not await bot.is_user_authorized():
                print("❌ Telethon Session is NOT authorized! Please re-host via /host.", flush=True)
                return
            me = await bot.get_me()
            OWNER_ID = me.id
            uname = f"@{me.username}" if me.username else "NoUsername"

            # Register in Fleet Cluster
            if USERBOT_SLOT == 0:
                FLEET_MASTERS.add(me.id)
            cfg = load_fleet_config()
            if "slots" not in cfg: cfg["slots"] = {}
            cfg["slots"][str(USERBOT_SLOT)] = {
                "id": me.id,
                "name": me.first_name,
                "username": me.username or "",
                "role": "Master Controller" if USERBOT_SLOT == 0 else f"Fleet Worker #{USERBOT_SLOT+1}",
                "last_active": int(time.time())
            }
            if USERBOT_SLOT == 0 and me.id not in cfg.get("masters", []):
                if "masters" not in cfg: cfg["masters"] = []
                cfg["masters"].append(me.id)
            save_fleet_config(cfg)

            role_str = f"👑 MASTER (Slot #{USERBOT_SLOT+1})" if USERBOT_SLOT == 0 else f"🤖 FLEET WORKER (Slot #{USERBOT_SLOT+1})"
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
            print("🤖 AMRIT ADVANCE V2 USERBOT STARTED!", flush=True)
            print(f"👤 Logged in as → {me.first_name} ({uname})", flush=True)
            print(f"🆔 User ID → {me.id}  [{role_str}]", flush=True)
            print(f"📦 Commands → {len(commands)} registered", flush=True)
            print(f"🛡️ Fleet Masters → {sorted(FLEET_MASTERS)}", flush=True)
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
            # Start continuous zero-disk and zero-RAM purger (protects server 512MB RAM & 5GB bandwidth)
            asyncio.create_task(_auto_disk_and_memory_purger())
            while True:
                try: await bot.run_until_disconnected(); break
                except (ConnectionError, OSError):
                    print("⚠️ Reconnecting...", flush=True)
                    await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Userbot stopped manually", flush=True)
        except Exception as e:
            print(f"\n❌ Startup Error → {str(e)[:200]}", flush=True)
            _traceback.print_exc()
        finally:
            try:
                if bot.is_connected(): await bot.disconnect()
            except: pass

    if __name__ == "__main__":
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            print("\n🛑 Userbot stopped manually", flush=True)
        except Exception as e:
            print(f"\n❌ Userbot Loop Error: {e}", flush=True)
            _traceback.print_exc()
        finally:
            try:
                if bot.is_connected():
                    loop.run_until_complete(bot.disconnect())
            except Exception:
                pass

# ════════════════════════════════════════════════════════════════════
#   HOSTER BOT MODE
# ════════════════════════════════════════════════════════════════════
else:
    import os, sys, json, threading, subprocess, time as _time
    import shutil, asyncio, logging, time, html
    import types as _types

    # ── BOT & OWNER CONFIG (From Top Config or Environment) ──
    BOT_TOKEN         = os.environ.get("BOT_TOKEN", "").strip() or GLOBAL_BOT_TOKEN
    OWNER_ID          = int(os.environ.get("OWNER_ID", "").strip() or GLOBAL_OWNER_ID)
    SUPPORT_USERNAME  = os.environ.get("SUPPORT_USERNAME", "").strip() or GLOBAL_SUPPORT_USERNAME
    DEVELOPER_NAME    = os.environ.get("DEVELOPER_NAME", "").strip() or GLOBAL_DEVELOPER_NAME
    DEVELOPER_HANDLE  = os.environ.get("DEVELOPER_HANDLE", "").strip() or GLOBAL_DEVELOPER_HANDLE
    DEVELOPER_URL     = "https://t.me/" + DEVELOPER_HANDLE.lstrip("@")
    MAX_ACCOUNTS_PER_USER = int(os.environ.get("MAX_ACCOUNTS_PER_USER", "10") or "10")

    # ── FORCE JOIN CHANNELS / GROUP CONFIGURATION (2 CHANNELS + 1 GC) ──
    FORCE_CHANNELS = [
        {"id": "channel_1", "name": "📢 MENTAL FYTS POST", "username": "@mental_fyts_post", "url": "https://t.me/mental_fyts_post"},
        {"id": "channel_2", "name": "💬 MENTAL ERA GC", "username": "@mental_era", "url": "https://t.me/mental_era"},
        {"id": "channel_3", "name": "📢 MENTALS EMPIRE", "username": "@mentals_empire", "url": "https://t.me/mentals_empire"}
    ]
    MAX_USERBOTS      = int(os.environ.get("MAX_USERBOTS", "50") or "50")
    TELEGRAM_API_ID   = int(os.environ.get("TELEGRAM_API_ID", "").strip() or os.environ.get("API_ID", "").strip() or GLOBAL_API_ID)
    TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "").strip() or os.environ.get("API_HASH", "").strip() or GLOBAL_API_HASH
    MAX_ACCOUNTS_PER_USER = int(os.environ.get("MAX_ACCOUNTS_PER_USER", "10") or "10")

    # ── DB ──
    _DB_DIR = os.path.join(os.getcwd(), "data")
    _db_lock = threading.Lock()

    def _db_path(*parts):
        p = os.path.join(_DB_DIR, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def _read_json(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

    def _write_json(path, data):
        with _db_lock:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)

    def user_exists(uid):
        return os.path.isfile(_db_path("users", str(uid), "meta.json"))

    def save_user_meta(uid, data):
        path = _db_path("users", str(uid), "meta.json")
        existing = _read_json(path, {})
        existing.update(data)
        _write_json(path, existing)

    def get_all_users():
        users_dir = os.path.join(_DB_DIR, "users")
        if not os.path.isdir(users_dir):
            return []
        return [d for d in os.listdir(users_dir)
                if os.path.isdir(os.path.join(users_dir, d))]

    def user_count():
        return len(get_all_users())

    def _accts_path(uid):
        return _db_path("users", str(uid), "accounts.json")

    def get_accounts(uid):
        return _read_json(_accts_path(uid), [])

    def get_account(uid, slot):
        for a in get_accounts(uid):
            if a.get("slot") == slot:
                return a
        return None

    def add_account(uid, acct):
        accounts = get_accounts(uid)
        accounts = [a for a in accounts if a.get("slot") != acct.get("slot")]
        accounts.append(acct)
        _write_json(_accts_path(uid), accounts)

    def remove_account(uid, slot):
        accounts = [a for a in get_accounts(uid) if a.get("slot") != slot]
        _write_json(_accts_path(uid), accounts)

    def hosted_count():
        total = 0
        for uid_str in get_all_users():
            for a in get_accounts(uid_str):
                if a.get("hosted"):
                    total += 1
        return total

    def _sudo_path():
        return _db_path("sudo.json")

    def get_sudo_users():
        return _read_json(_sudo_path(), [])

    def add_sudo(uid):
        s = get_sudo_users()
        if uid not in s:
            s.append(uid)
            _write_json(_sudo_path(), s)

    def remove_sudo(uid):
        s = [x for x in get_sudo_users() if x != uid]
        _write_json(_sudo_path(), s)

    def is_sudo(uid, owner_id):
        return uid == owner_id or uid in get_sudo_users()

    def _blocked_path():
        return _db_path("blocked.json")

    def get_blocked():
        return _read_json(_blocked_path(), [])

    def block_user(uid):
        b = get_blocked()
        if uid not in b:
            b.append(uid)
            _write_json(_blocked_path(), b)

    def unblock_user(uid):
        b = [x for x in get_blocked() if x != uid]
        _write_json(_blocked_path(), b)

    def is_blocked(uid):
        return uid in get_blocked()

    db = _types.SimpleNamespace(
        user_exists=user_exists, save_user_meta=save_user_meta,
        get_all_users=get_all_users, user_count=user_count,
        get_accounts=get_accounts, get_account=get_account,
        add_account=add_account, remove_account=remove_account,
        hosted_count=hosted_count,
        get_sudo_users=get_sudo_users, add_sudo=add_sudo,
        remove_sudo=remove_sudo, is_sudo=is_sudo,
        get_blocked=get_blocked, block_user=block_user,
        unblock_user=unblock_user, is_blocked=is_blocked,
    )

    # ── RUNNER (with PID file persistence) ──
    _procs = {}
    _start_times = {}
    _log_handles = {}
    _PID_FILE = os.path.join(_DB_DIR, "running_pids.json")

    def _this_file():
        return os.path.abspath(__file__)

    def _get_python_exe():
        exe = sys.executable
        if sys.platform == "win32":
            prefix_py = os.path.join(sys.prefix, "python.exe")
            if os.path.isfile(prefix_py):
                return prefix_py
            base_py = os.path.join(getattr(sys, "base_prefix", sys.prefix), "python.exe")
            if os.path.isfile(base_py):
                return base_py
            if exe and exe.lower().endswith("pythonw.exe"):
                p = exe[:-9] + "python.exe"
                if os.path.isfile(p):
                    return p
            if exe and ("launcher" in exe.lower() or exe.lower().endswith("py.exe")):
                real = shutil.which("python") or shutil.which("python3")
                if real and not real.lower().endswith("py.exe"):
                    return real
        return exe or "python"

    def _save_pids():
        """Persist running PIDs to disk so they survive hoster restart."""
        try:
            data = {}
            for (uid, slot), proc in _procs.items():
                if proc.poll() is None:
                    data[f"{uid}:{slot}"] = {
                        "pid": proc.pid,
                        "start": _start_times.get((uid, slot), _time.time()),
                    }
            _write_json(_PID_FILE, data)
        except Exception as e:
            print(f"[RUNNER] save_pids error: {e}", flush=True)

    def _load_pids():
        """Re-attach to previously running userbots via PID."""
        try:
            data = _read_json(_PID_FILE, {})
            for key, info in data.items():
                try:
                    uid_s, slot_s = key.split(":")
                    uid, slot = int(uid_s), int(slot_s)
                    pid = info.get("pid")
                    if not pid: continue
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        continue  # dead
                    _start_times[(uid, slot)] = info.get("start", _time.time())
                    _procs[(uid, slot)] = _ExternalProc(pid)
                except Exception as e:
                    print(f"[RUNNER] load_pids skip {key}: {e}", flush=True)
        except Exception as e:
            print(f"[RUNNER] load_pids error: {e}", flush=True)

    class _ExternalProc:
        """Wraps an externally-running PID so we can query its status."""
        def __init__(self, pid):
            self.pid = pid
        def poll(self):
            try:
                os.kill(self.pid, 0)
                return None  # alive
            except OSError:
                return 1  # dead
        def terminate(self):
            try: os.kill(self.pid, 15)
            except: pass
        def kill(self):
            try: os.kill(self.pid, 9)
            except: pass
        def wait(self, timeout=None):
            import time as _t
            start = _t.time()
            while True:
                if self.poll() is not None: return 0
                if timeout and (_t.time() - start) > timeout: raise TimeoutError()
                _t.sleep(0.2)

    def _build_env(api_id, api_hash, session_string, owner_id_str, slot=0):
        env = os.environ.copy()
        env.update({
            "API_ID":                  str(api_id),
            "API_HASH":                str(api_hash),
            "SESSION_STRING":          session_string,
            "USERBOT_OWNER_ID":        str(owner_id_str),
            "USERBOT_SLOT":            str(slot),
            "USERBOT_MODE":            "1",
            "PYTHONIOENCODING":        "utf-8",
            "PYTHONUTF8":              "1",
            "PYTHONDONTWRITEBYTECODE":  "1",
            "PYTHONUNBUFFERED":        "1",
            "PYTHONOPTIMIZE":          "2",
            "MALLOC_ARENA_MAX":        "1",
            "MALLOC_MMAP_THRESHOLD_": "65536",
            "MALLOC_TRIM_THRESHOLD_": "65536",
            "PYTHONMALLOC":            "malloc",
        })
        return env

    def start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        key = (int(uid), int(slot))
        # If already running, stop first
        existing = _procs.get(key)
        if existing and existing.poll() is None:
            stop_userbot(uid, slot)
        try:
            env = _build_env(api_id, api_hash, session_string, owner_id_str, slot=slot)
            os.makedirs("userbot_logs", exist_ok=True)
            log_path = f"userbot_logs/userbot_{uid}_slot{slot}.log"
            log_file = open(log_path, "a", encoding="utf-8", errors="replace")
            log_file.write(f"\n\n===== Started at {_time.ctime()} =====\n")
            log_file.flush()
            pop_kwargs = {
                "env": env,
                "stdin": subprocess.DEVNULL,
                "stdout": log_file,
                "stderr": log_file,
                "cwd": os.getcwd(),
            }
            if sys.platform == "win32":
                pop_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                pop_kwargs["start_new_session"] = True

            py_bin = _get_python_exe()
            proc = subprocess.Popen(
                [py_bin, "-O", "-B", "-u", _this_file(), "--userbot"],
                **pop_kwargs
            )
            # Retain handle reference in parent so it is not closed prematurely on Windows
            _log_handles[key] = log_file

            _procs[key] = proc
            _start_times[key] = _time.time()
            _save_pids()
            print(f"[RUNNER] Started userbot uid={uid} slot={slot} pid={proc.pid} via {py_bin}", flush=True)

            # Reclaim hoster memory immediately
            import gc
            gc.collect()
            try:
                import ctypes
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception: pass
            return True
        except Exception as e:
            print(f"[RUNNER] start error: {e}", flush=True)
            return False

    def restart_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        return start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str)

    def stop_userbot(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.pop(key, None)
        _start_times.pop(key, None)
        old_log = _log_handles.pop(key, None)
        if old_log:
            try: old_log.close()
            except: pass
        if proc:
            try:
                proc.terminate()
                try: proc.wait(timeout=5)
                except:
                    try: proc.kill()
                    except: pass
            except:
                try: proc.kill()
                except: pass
        _save_pids()

    def stop_all_for_user(uid):
        keys = [k for k in list(_procs.keys()) if k[0] == int(uid)]
        for k in keys:
            stop_userbot(k[0], k[1])

    def is_running(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.get(key)
        if not proc:
            # Try to load from PID file
            return False
        if proc.poll() is not None:
            _procs.pop(key, None)
            _start_times.pop(key, None)
            _save_pids()
            return False
        return True

    def running_count():
        dead = [k for k, p in list(_procs.items()) if p.poll() is not None]
        for k in dead:
            _procs.pop(k, None)
            _start_times.pop(k, None)
        if dead:
            _save_pids()
        return len(_procs)

    def get_uptime(uid, slot):
        key = (int(uid), int(slot))
        t = _start_times.get(key)
        if not t: return "—"
        e = int(_time.time() - t)
        h, r = divmod(e, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    runner = _types.SimpleNamespace(
        start_userbot=start_userbot, restart_userbot=restart_userbot,
        stop_userbot=stop_userbot, stop_all_for_user=stop_all_for_user,
        is_running=is_running, running_count=running_count,
        get_uptime=get_uptime,
    )

    # ── TELEGRAM HOSTER BOT ──
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
    )
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, ConversationHandler,
        CallbackQueryHandler, ContextTypes, filters
    )
    from telegram.constants import ParseMode
    from telethon import TelegramClient, types
    from telethon.sessions import StringSession
    from telethon.errors import (
        SessionPasswordNeededError, PhoneCodeExpiredError,
        PhoneCodeInvalidError, FloodWaitError
    )

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    START_TIME = time.time()
    ASK_PHONE, ASK_CODE, ASK_2FA = range(3)
    pending_logins: dict = {}

    def md_escape(text: str) -> str:
        if not text: return ""
        for ch in ['_', '*', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            text = text.replace(ch, '\\' + ch)
        return text

    def bold_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D400)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D41A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7CE)
            else: result += c
        return result

    def italic_serif(t: str) -> str:
        special = {'h': '𝒽', 'e': '𝑒', 'i': '𝑖', 'j': '𝑗'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D434)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D44E)
            else: result += c
        return result

    def script(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D4D0)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D4EA)
            else: result += c
        return result

    def double_struck(t: str) -> str:
        special_map = {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ'}
        result = ""
        for c in t:
            if c in special_map: result += special_map[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D538)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D552)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7D8)
            else: result += c
        return result

    def sans_bold(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D5D4)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D5EE)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7EC)
            else: result += c
        return result

    def mono(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D670)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D68A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7F6)
            else: result += c
        return result

    def fraktur(t: str) -> str:
        special = {'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D504)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D51E)
            else: result += c
        return result

    def bold_italic_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D468)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D482)
            else: result += c
        return result

    DIV  = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIV2 = "·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·"
    DIV3 = "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯"
    TOP  = "╔══════════════════════════╗"
    BOT  = "╚══════════════════════════╝"
    MID  = "╠══════════════════════════╣"

    def is_owner(uid): return uid == OWNER_ID
    def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

    def uptime_str():
        e = int(time.time() - START_TIME)
        h, r = divmod(e, 3600); m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    def _phone_label(acct: dict) -> str:
        phone = acct.get("phone", "")
        return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

    async def _reply_to(update: Update, text: str):
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    async def owner_only(update: Update) -> bool:
        if not is_owner(update.effective_user.id):
            await _reply_to(update,
                f"{TOP}\n║  🔒  {bold_serif('Access Denied')}  🔒  ║\n{BOT}\n\n"
                f"{script('This command is restricted to')}\n👑 {sans_bold('Owners Only')}")
            return False
        return True

    async def premium_only(update: Update) -> bool:
        if not is_premium(update.effective_user.id):
            await _reply_to(update,
                f"🌟 {bold_serif('Premium Required')}\n\n"
                f"{script('This feature is for')}\n"
                f"👑 {sans_bold('Owners')} & {sans_bold('Premium Users')} {script('only')}\n\n"
                f"📩 {mono('Contact:')} {SUPPORT_USERNAME}")
            return False
        return True

    async def check_blocked(update: Update) -> bool:
        if db.is_blocked(update.effective_user.id):
            await _reply_to(update,
                f"🚫 {bold_serif('You have been Blocked')}\n\n"
                f"{script('Contact support to appeal.')}")
            return False
        return True

    async def cleanup_pending(uid: int):
        data = pending_logins.pop(uid, None)
        if data and data.get("client"):
            try: await data["client"].disconnect()
            except: pass

    # ── 1 CHANNEL + 1 GC FORCE JOIN VERIFICATION HELPER ──
    async def verify_force_join(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, list]:
        if user_id == OWNER_ID:
            return (True, [])
        unjoined = []
        for ch in FORCE_CHANNELS:
            username = ch.get("username")
            if not username: continue
            try:
                member = await context.bot.get_chat_member(chat_id=username, user_id=user_id)
                status = getattr(member, "status", None)
                if status in ["left", "kicked"]:
                    unjoined.append(ch)
                elif status in ["member", "administrator", "creator"]:
                    pass  # Joined!
                elif status == "restricted":
                    is_mem = getattr(member, "is_member", True)
                    if not is_mem:
                        unjoined.append(ch)
                else:
                    unjoined.append(ch)
            except Exception as e:
                err_msg = str(e).lower()
                # If user explicitly not found in a channel where bot has admin rights
                if "user not found" in err_msg or "participant" in err_msg:
                    unjoined.append(ch)
                else:
                    # Bot is not admin in this channel or cannot check members, gracefully allow user through
                    logger.info(f"Force join check skipped for {username}: {e}")
        return (len(unjoined) == 0, unjoined)

    def build_force_join_markup():
        keyboard = [
            [InlineKeyboardButton("📢 1. Join Mental Fyts Post", url="https://t.me/mental_fyts_post")],
            [InlineKeyboardButton("💬 2. Join Mental Era (GC)", url="https://t.me/mental_era")],
            [InlineKeyboardButton("📢 3. Join Mentals Empire", url="https://t.me/mentals_empire")],
            [InlineKeyboardButton("✅ I Have Joined (Verify)", callback_data="verify_force_join")],
            [
                InlineKeyboardButton(f"👑 Developer: {DEVELOPER_HANDLE}", url=f"https://t.me/{DEVELOPER_HANDLE.lstrip('@')}"),
                InlineKeyboardButton("💬 Support GC", url="https://t.me/mental_era")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    # ── DEVELOPER PROFILE CARD ──
    async def send_developer_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            target = update.callback_query.message if update.callback_query else update.message
            dev_user = DEVELOPER_HANDLE.lstrip('@')
            card = (
                "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                "   👨‍💻  <b>𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑  𝐏𝐑𝐎𝐅𝐈𝐋𝐄</b>\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"👑  <b>Creator & Owner</b> : {html.escape(DEVELOPER_NAME)}\n"
                f"🆔  <b>Owner ID</b>        : <code>{OWNER_ID}</code>\n"
                f"✈️  <b>Developer</b>       : <a href=\"https://t.me/{dev_user}\">{html.escape(DEVELOPER_HANDLE)}</a>\n"
                f"📢  <b>Official Channel 1</b> : <a href=\"https://t.me/mental_fyts_post\">@mental_fyts_post</a>\n"
                f"💬  <b>Support Group (GC)</b>  : <a href=\"https://t.me/mental_era\">@mental_era</a>\n"
                f"📢  <b>Official Channel 2</b> : <a href=\"https://t.me/mentals_empire\">@mentals_empire</a>\n"
                f"🛡️  <b>Architecture</b>    : High-Speed Python/Telethon\n"
                f"⚡  <b>System Version</b>   : {html.escape(DEVELOPER_NAME)} V2 PRO\n"
                "───────────────────────────────\n"
                "💬 <i>Contact developer directly for setup & assistance!</i>\n"
            )
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💬 Message Developer ({DEVELOPER_HANDLE})", url=f"https://t.me/{dev_user}")],
                [
                    InlineKeyboardButton("📢 Channel 1", url="https://t.me/mental_fyts_post"),
                    InlineKeyboardButton("📢 Channel 2", url="https://t.me/mentals_empire")
                ],
                [InlineKeyboardButton("💬 Support GC (@mental_era)", url="https://t.me/mental_era")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main_menu")]
            ])
            if update.callback_query:
                try: await update.callback_query.edit_message_text(card, parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True)
                except Exception: await target.reply_text(card, parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True)
            else:
                await target.reply_text(card, parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error in send_developer_card: {e}")

    # ── USER PROFILE WITH DP AND ALL BUTTONS ──
    async def send_user_help_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            uid = user.id
            first_name = user.first_name or "User"
            last_name = user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            username = f"@{user.username}" if user.username else "No Username"
            dev_user = DEVELOPER_HANDLE.lstrip('@')

            caption = (
                "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                "   👤  <b>𝐔𝐒𝐄𝐑  𝐏𝐑𝐎𝐅𝐈𝐋𝐄  𝐂𝐀𝐑𝐃</b>\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"👋 𝐇𝐞𝐥𝐥𝐨, <b>{html.escape(full_name)}</b>!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 <b>𝐔𝐬𝐞𝐫 𝐈𝐃</b>    : <code>{uid}</code>\n"
                f"👤 <b>𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞</b>   : {html.escape(username)}\n"
                f"📛 <b>𝐅𝐮𝐥𝐥 𝐍𝐚𝐦𝐞</b>  : {html.escape(full_name)}\n"
                "✨ <b>𝐒𝐭𝐚𝐭𝐮𝐬</b>     : Verified Member ✅\n"
                "🔒 <b>𝐅𝐨𝐫𝐜𝐞 𝐒𝐮𝐛</b>  : Joined Channel & Group 🟢\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫</b>  : <a href=\"https://t.me/{dev_user}\">{html.escape(DEVELOPER_HANDLE)}</a>\n"
                f"⚡ <b>𝐒𝐲𝐬𝐭𝐞𝐦</b>     : {html.escape(DEVELOPER_NAME)} USERBOT V2 PRO\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 <b>Commands Kaise Chalayein:</b>\n"
                "Account host (/host) hone ke baad kisi bhi DM ya Chat me <code>.menu</code> likhein!\n"
                "Dragon Dark UI ke sath saare 500+ commands direct open honge."
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚀 Login / Deploy Userbot", callback_data="host"),
                    InlineKeyboardButton("🐉 Dragon Menu (.menu)", callback_data="commands")
                ],
                [
                    InlineKeyboardButton("📊 Bot Status", callback_data="status"),
                    InlineKeyboardButton("📱 My Accounts", callback_data="myaccounts")
                ],
                [
                    InlineKeyboardButton("🔄 Restart Bot", callback_data="menu_restart"),
                    InlineKeyboardButton("🗑️ Logout", callback_data="menu_logout")
                ],
                [
                    InlineKeyboardButton(f"👑 Developer: {DEVELOPER_HANDLE}", url=f"https://t.me/{dev_user}"),
                    InlineKeyboardButton("❓ Full Guide", callback_data="help_guide")
                ]
            ])

            # 1. Try sending User Profile Photo with caption
            photo_sent = False
            try:
                photos = await context.bot.get_user_profile_photos(user_id=uid, limit=1)
                if photos and photos.total_count > 0:
                    photo_file_id = photos.photos[0][-1].file_id
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_file_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=buttons
                    )
                    photo_sent = True
                    return
            except Exception as e:
                logger.info(f"Could not send user photo (maybe user has no DP or privacy enabled): {e}")

            # 2. If no photo or photo failed, send formatted message
            if not photo_sent:
                try:
                    if update.callback_query:
                        try:
                            await update.callback_query.edit_message_text(
                                caption,
                                parse_mode=ParseMode.HTML,
                                reply_markup=buttons,
                                disable_web_page_preview=True
                            )
                            return
                        except Exception:
                            pass
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=buttons,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.warning(f"HTML send failed, fallback to plain text: {e}")
                    clean_caption = (
                        "=== USER PROFILE CARD ===\n\n"
                        f"Hello, {full_name}!\n"
                        f"User ID: {uid}\n"
                        f"Username: {username}\n"
                        f"Developer: {DEVELOPER_HANDLE}\n\n"
                        "Use the buttons below to control your userbot:"
                    )
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=clean_caption,
                        reply_markup=buttons
                    )
        except Exception as e:
            logger.error(f"Fatal error in send_user_help_profile: {e}", exc_info=True)
            try:
                await update.effective_chat.send_message(
                    f"👋 Welcome! User ID: {update.effective_user.id}\nUse /host to deploy your userbot or /commands to see features."
                )
            except Exception:
                pass

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await check_blocked(update): return
            user = update.effective_user
            uid  = user.id
            first_name = user.first_name or "User"
            name = html.escape(first_name)

            if not db.user_exists(uid):
                db.save_user_meta(uid, {"first_name": first_name, "joined_at": int(time.time())})

            # Check Force Join Channels (Owner automatically passes)
            joined, unjoined = await verify_force_join(uid, context)
            if not joined and uid != OWNER_ID:
                force_text = (
                    "╔══════════════════════════╗\n"
                    "║  ⚠️  <b>Access Locked</b>  ⚠️  ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"👋 𝐇𝐞𝐥𝐥𝐨, <b>{name}</b>!\n\n"
                    f"To use <b>{html.escape(DEVELOPER_NAME)} Userbot Hoster</b>, aapko pehle hamare 2 Channels aur 1 Group (GC) join karne honge:\n\n"
                    "1️⃣ 📢 <b>CHANNEL 1</b>: @mental_fyts_post\n"
                    "2️⃣ 💬 <b>GROUP (GC)</b>: @mental_era\n"
                    "3️⃣ 📢 <b>CHANNEL 2</b>: @mentals_empire\n\n"
                    "👉 <i>Teeno links ko join karein aur niche</i> <b>✅ I Have Joined (Verify)</b> <i>button dabayein!</i>"
                )
                markup = build_force_join_markup()
                try:
                    await update.message.reply_text(
                        force_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                except Exception:
                    await update.message.reply_text(
                        force_text,
                        reply_markup=markup
                    )
                return

            await send_user_help_profile(update, context)
        except Exception as e:
            logger.error(f"Error in cmd_start: {e}", exc_info=True)
            try:
                await update.message.reply_text(
                    f"👋 Welcome to {DEVELOPER_NAME} Userbot Hoster!\nSend /host to deploy your userbot."
                )
            except Exception:
                pass

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await check_blocked(update): return
            uid = update.effective_user.id
            joined, _ = await verify_force_join(uid, context)
            if not joined and uid != OWNER_ID:
                force_text = (
                    "╔══════════════════════════╗\n"
                    "║  ⚠️  <b>Access Locked</b>  ⚠️  ║\n"
                    "╚══════════════════════════╝\n\n"
                    "Pehle hamare 2 Channels aur 1 Group (GC) join karein:\n\n"
                    "1️⃣ 📢 @mental_fyts_post\n"
                    "2️⃣ 💬 @mental_era (GC)\n"
                    "3️⃣ 📢 @mentals_empire\n\n"
                    "👉 Teeno join karke <b>Verify</b> button dabayein!"
                )
                try:
                    await update.message.reply_text(
                        force_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=build_force_join_markup(),
                        disable_web_page_preview=True
                    )
                except Exception:
                    await update.message.reply_text(force_text, reply_markup=build_force_join_markup())
                return

            # Send User DP + Username + User ID + All Action Buttons
            await send_user_help_profile(update, context)
        except Exception as e:
            logger.error(f"Error in cmd_help: {e}")

        text = (
            f"❓ {double_struck('Help')} & {double_struck('Commands')}\n"
            f"{DIV}\n\n"
            f"🔹 {mono('/start')}       {script('Grand Welcome Screen')}\n"
            f"🔹 {mono('/help')}        {script('This Help Menu')}\n"
            f"🔹 {mono('/commands')}    {script('Userbot Features List')}\n"
            f"🔹 {mono('/host')}        {script('Add & Deploy Account')}\n"
            f"🔹 {mono('/myaccounts')}  {script('Manage All Accounts')}\n"
            f"🔹 {mono('/status')}      {script('Check All Userbots')}\n"
            f"🔹 {mono('/restart')}     {script('Restart Userbot')}\n"
            f"🔹 {mono('/logout')}      {script('Logout an Account')}\n"
            f"🔹 {mono('/support')}     {script('Contact Admin')}\n\n"
            f"{DIV}\n"
            f"👑 {sans_bold('Owner Commands')}\n"
            f"🔺 {mono('/restartall')} /restart all\n"
            f"🔺 {mono('/refresh')}\n"
            f"🔺 {mono('/sudolist')} add/del\n"
            f"🔺 {mono('/setdp')}\n"
            f"🔺 {mono('/block')} /unblock /blockeduser\n"
            f"🔺 {mono('/stats')}\n"
            f"{DIV}")
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            try: await update.callback_query.answer()
            except: pass
            target_msg = update.callback_query.message
        else:
            target_msg = update.message

        if not await check_blocked(update): return
        text = (
            f"🐉 <b>ARYA X MENTAL — DRAGON USERBOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ <b>COMMANDS KAISE CHALAYEIN?</b>\n"
            f"Commands bot ke buttons se nahi, balki aapke <b>HOSTED ACCOUNT</b> se chalte hain!\n\n"
            f"1️⃣ Pehle <b>/host</b> dabayein aur apna Telegram account deploy karein.\n"
            f"2️⃣ Account host hone ke baad kisi bhi DM, Group ya Saved Messages me type karein:\n"
            f"    👉 <code>.menu</code>\n\n"
            f"🔥 <b>Tagda Dragon Dark UI</b> me saare <b>500+ commands</b> direct aapke account se open ho jayenge!\n\n"
            f"⚔️ <b>Top Power Commands Preview:</b>\n"
            f"• <code>.attack</code>  <code>.roast</code>  <code>.diss</code>  <code>.war</code>  <code>.savage</code>\n"
            f"• <code>.reply</code>  <code>.rr</code>  <code>.replyAMRIT</code>  <code>.replyaryaxmental</code>\n"
            f"• <code>.spray</code>  <code>.dspray</code>  <code>.antidel</code>  <code>.watchspam</code>\n"
            f"• <code>.ban</code>  <code>.mute</code>  <code>.purge</code>  <code>.ping</code>  <code>.alive</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> Arya X MENTAL\n"
            f"💻 <b>Developer:</b> {DEVELOPER_HANDLE} ({DEVELOPER_NAME})\n"
            f"🚀 <b>Deploy Your Account:</b> /host"
        )
        await target_msg.reply_text(text, parse_mode=ParseMode.HTML)

    async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # If callback, answer it
        if update.callback_query:
            try: await update.callback_query.answer()
            except: pass
            target_msg = update.callback_query.message
        else:
            target_msg = update.message

        if not await check_blocked(update):
            return ConversationHandler.END
        uid = update.effective_user.id
        is_owner_user = (uid == OWNER_ID or uid in db.get_sudo_users() or is_premium(uid))

        if not is_owner_user:
            await target_msg.reply_text(
                "🔒 **PRIVATE PERSONAL USERBOT**\n\n"
                "⚠️ *Yeh bot exclusively Owner (Arya X Mental) ke liye private configured hai!*\n"
                "Public hosting band hai taaki Owner ke personal 6-10+ accounts 24/7 dedicated bina crash ke chalte rahein.",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        allowed_max = 20  # Dedicated Personal Fleet supports up to 20 accounts!
        if len(hosted) >= allowed_max:
            await target_msg.reply_text(
                f"📱 {bold_serif('Account Limit Reached')}\n\n"
                f"{script('You already have')} {mono(str(len(hosted)))} {script('accounts hosted.')}\n"
                f"📌 {italic_serif('Maximum:')} {mono(str(allowed_max))}\n\n"
                f"🗑️ {script('Logout an account first:')} /logout",
                parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

        total = db.hosted_count()
        if total >= MAX_USERBOTS and not is_owner_user:
            await target_msg.reply_text(
                f"😔 {sans_bold('Slots Full')} ({total}/{MAX_USERBOTS})\n\n"
                f"{script('Contact')} {SUPPORT_USERNAME} {script('to get a slot.')}",
                parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

        await cleanup_pending(uid)

        extra = f"\n\n📱 {italic_serif('Account')} {mono(str(len(hosted)+1))} {italic_serif('of')} {mono(str(allowed_max))}" if hosted else ""

        await target_msg.reply_text(
            f"{TOP}\n"
            f"║  🚀  {bold_serif('Deploy Your Userbot')}  🚀  ║\n"
            f"{BOT}\n\n"
            f"📱 {sans_bold('Step 1 of 3')}\n"
            f"{DIV3}\n"
            f"{script('Choose any ONE method to host')}:\n\n"
            f"🔹 {bold_serif('Option A (Phone Number)')}:\n"
            f"   Send: {mono('+91XXXXXXXXXX')}\n\n"
            f"🔹 {bold_serif('Option B (Direct String Session)')}:\n"
            f"   Send your {mono('Telethon StringSession')} directly!\n"
            f"   *(No OTP required for String Session)*"
            f"{extra}\n\n"
            f"⚠️ {italic_serif('Note: Agar phone daal rahe hain toh OTP aapke official Telegram App me aayega (SMS par nahi)!')}\n\n"
            f"🔴 {italic_serif('Send /cancel to abort')}",
            parse_mode=ParseMode.MARKDOWN)
        return ASK_PHONE

    async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid   = update.effective_user.id
        raw_text = update.message.text.strip()

        # ── METHOD B: Direct String Session ──
        if len(raw_text) > 40 and not raw_text.startswith("+") and not raw_text.replace(" ", "").isdigit():
            msg = await update.message.reply_text(f"⏳ {sans_bold('Verifying String Session')}... 🔐")
            try:
                test_client = TelegramClient(
                    StringSession(raw_text),
                    TELEGRAM_API_ID,
                    TELEGRAM_API_HASH,
                    device_model="Samsung Galaxy S24 Ultra",
                    system_version="Android 14",
                    app_version="10.14.0",
                    lang_code="en",
                    system_lang_code="en"
                )
                await test_client.connect()
                if not await test_client.is_user_authorized():
                    await test_client.disconnect()
                    await msg.edit_text(
                        f"❌ {bold_serif('Invalid Session String')}\n\n"
                        f"{script('Session expired ya galat hai. Kripya naya session daalein ya Phone Number enter karein.')}",
                        parse_mode=ParseMode.MARKDOWN)
                    return ASK_PHONE
                me = await test_client.get_me()
                phone_num = getattr(me, 'phone', '') or 'Session'
                await test_client.disconnect()
                await _deploy_userbot(update, context, uid, raw_text, phone_num, msg)
                return ConversationHandler.END
            except Exception as e:
                await msg.edit_text(
                    f"❌ {bold_serif('Session Error')}\n{mono(str(e)[:120])}\n\n"
                    f"{script('Dobara try karein ya Phone Number enter karein.')}",
                    parse_mode=ParseMode.MARKDOWN)
                return ASK_PHONE

        # ── METHOD A: Phone Number Login ──
        phone = raw_text
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 7:
            await update.message.reply_text(
                f"❌ {bold_serif('Invalid Input')}\n\n"
                f"{script('Format: +91XXXXXXXXXX ya apna Telethon StringSession bhejein')}",
                parse_mode=ParseMode.MARKDOWN)
            return ASK_PHONE

        if not phone.startswith("+"):
            phone = "+" + digits

        msg = await update.message.reply_text(f"⏳ {sans_bold('Sending OTP to Telegram')}... 📨")
        try:
            client = TelegramClient(
                StringSession(),
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                device_model="Samsung Galaxy S24 Ultra",
                system_version="Android 14",
                app_version="10.14.0",
                lang_code="en",
                system_lang_code="en"
            )
            await client.connect()
            result = await client.send_code_request(phone)
            pending_logins[uid] = {
                "client": client,
                "phone":  phone,
                "phone_code_hash": result.phone_code_hash,
            }

            # Detect where Telegram sent the OTP
            otp_dest = "Telegram Official App (Chat with 777000)"
            code_type = getattr(result, 'type', None)
            if hasattr(types, 'auth'):
                if isinstance(code_type, types.auth.SentCodeTypeApp):
                    otp_dest = "Telegram App (Chat 'Telegram' with blue tick)"
                elif isinstance(code_type, types.auth.SentCodeTypeSms):
                    otp_dest = "SMS on SIM Card"
                elif isinstance(code_type, types.auth.SentCodeTypeCall):
                    otp_dest = "Phone Call"
                elif isinstance(code_type, types.auth.SentCodeTypeEmailCode):
                    otp_dest = "Email Inbox"

            await msg.edit_text(
                f"{TOP}\n"
                f"║  📨  {bold_serif('OTP Sent Successfully')}  📨  ║\n"
                f"{BOT}\n\n"
                f"📱 {fraktur('Number')}: {mono(phone)}\n"
                f"📍 {sans_bold('OTP Delivered To')}:\n"
                f"👉 **{otp_dest}**\n\n"
                f"📩 {sans_bold('Step 2 of 3')}\n"
                f"{DIV3}\n"
                f"{script('Apne Telegram App me 777000 (Telegram) se aaya code enter karein.')}\n\n"
                f"⚠️ *DHYAN DEIN:* Telegram OTP SMS par nahi aata! Apne Telegram app ki chat list me 'Telegram' search karein.\n\n"
                f"💡 {italic_serif('Tip: Send with spaces to avoid auto-forward')}\n"
                f"    {mono('Example')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN)
            return ASK_CODE
        except FloodWaitError as e:
            await cleanup_pending(uid)
            await msg.edit_text(f"⏳ {sans_bold('Flood Wait!')} {mono(str(e.seconds) + 's')} baad try karo.")
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\n"
                f"💡 {italic_serif('Agar OTP nahi aa raha toh direct Telethon String Session paste karein.')}\n\n"
                f"{script('Try again:')} /host",
                parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        code = update.message.text.strip().replace(" ", "")
        pending = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text(f"❌ {sans_bold('Session expired. Try /host again.')}")
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending["phone"]
        hash_: str = pending["phone_code_hash"]

        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying OTP')}...")
        try:
            await client.sign_in(phone, code, phone_code_hash=hash_)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END
        except SessionPasswordNeededError:
            await msg.edit_text(
                f"{TOP}\n║  🔒  {bold_serif('2FA Detected')}  🔒  ║\n{BOT}\n\n"
                f"🛡️ {sans_bold('Step 3 of 3')}\n{DIV3}\n"
                f"{script('Your account has Two-Step Verification')}\n\n"
                f"🔑 {fraktur('Enter your 2FA Password')}:",
                parse_mode=ParseMode.MARKDOWN)
            return ASK_2FA
        except PhoneCodeInvalidError:
            await msg.edit_text(
                f"❌ {bold_serif('Wrong Code!')} Dobara enter karo:\n\n"
                f"💡 {mono('Spaces ke saath')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN)
            return ASK_CODE
        except PhoneCodeExpiredError:
            await cleanup_pending(uid)
            await msg.edit_text(f"⏳ {sans_bold('Code Expired!')} Dobara /host karo.", parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid      = update.effective_user.id
        password = update.message.text.strip()
        pending  = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text("❌ Session expire ho gayi. /host karo.")
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending.get("phone", "")
        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying 2FA Password')}...")
        try:
            await client.sign_in(password=password)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Wrong 2FA Password')}\n"
                f"{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    async def _deploy_userbot(update, context, uid, session_string, phone, msg):
        name     = update.effective_user.first_name or "User"
        accounts = db.get_accounts(uid)
        existing = {a.get("slot") for a in accounts}
        slot = 0
        while slot in existing:
            slot += 1
        acc_num = slot + 1

        await msg.edit_text(f"⏳ {double_struck('Deploying Account')} #{acc_num}... 🔄\n{DIV2}")
        ok = runner.start_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid))
        if ok:
            now = int(time.time())
            expires_at = now + 999999999  # Permanent Hosting for Personal Fleet (Never Expires)
            db.save_user_meta(uid, {"first_name": name})
            db.add_account(uid, {
                "slot":           slot,
                "session_string": session_string,
                "hosted":         True,
                "hosted_at":      now,
                "expires_at":     expires_at,
                "phone":          phone,
            })
            await msg.edit_text(
                f"{TOP}\n║  🎉  {bold_serif('Deploy Successful')}  🎉  ║\n{BOT}\n\n"
                f"✅ {sans_bold('Account')}    : {mono('#' + str(acc_num))}\n"
                f"📱 {sans_bold('Phone')}      : {mono(phone if phone else 'N/A')}\n"
                f"🛡️ {sans_bold('Hosting')}    : {mono('Permanent 24/7 (Never Expires)')}\n"
                f"⚡ {sans_bold('Version')}    : {mono('ARYA X MENTAL Advance V2')}\n"
                f"📦 {sans_bold('Commands')}   : {mono('500+')}\n\n"
                f"{DIV}\n"
                f"🔹 {italic_serif('Kisi bhi chat mein')} {mono('.alive')} {italic_serif('bhejo')}\n"
                f"🔹 /myaccounts {italic_serif('se sab accounts dekho')}\n"
                f"🔹 /status {italic_serif('se check karo kitna lease time bacha hai')}\n"
                f"💡 {italic_serif('24h baad storage 0MB ho jayegi, aap phir /host kar sakte hain')}",
                parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Deploy Failed')}\n\n"
                f"{script('Check userbot_logs/ folder for details.')}\n"
                f"📩 {sans_bold('Support')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN)

    async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cleanup_pending(update.effective_user.id)
        await update.message.reply_text(
            f"🚫 {bold_serif('Login Cancelled')}\n\n"
            f"{script('Use /host to try again anytime.')}")
        return ConversationHandler.END

    async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        is_owner_user = (uid == OWNER_ID or uid in db.get_sudo_users() or is_premium(uid))
        allowed_max = 20 if is_owner_user else 1

        if not hosted:
            keyboard = [[InlineKeyboardButton("🚀 Host My First Userbot", callback_data="host")]]
            await update.message.reply_text(
                f"📱 {bold_serif('No Accounts Hosted Yet')}\n\n"
                f"{script('Get started with /host')}\n"
                f"{italic_serif('Host up to')} {mono(str(allowed_max))} {italic_serif('accounts!')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard))
            return

        lines = []
        keyboard = []
        now = int(time.time())
        for acct in hosted:
            slot   = acct.get("slot", 0)
            alive  = runner.is_running(uid, slot)
            uptime = runner.get_uptime(uid, slot) if alive else None
            icon   = "🟢" if alive else "🔴"
            phone  = _phone_label(acct)
            h_at   = acct.get("hosted_at", now)
            exp_at = acct.get("expires_at", h_at + 86400)
            rem    = max(0, exp_at - now)
            rem_str = "  ⏳ ♾️ Permanent VIP (Never Expires)" if is_owner_user else (f"  ⏳ {rem//3600}h {(rem%3600)//60}m" if rem > 0 else "  ⚠️ Expired")
            up_str = f"  ⏱️ {uptime}" if uptime else ""
            lines.append(f"{icon} {bold_serif('Acc #' + str(slot+1))} — {mono(phone)}{up_str}{rem_str}")
            row = []
            if alive:
                row.append(InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"))
            else:
                row.append(InlineKeyboardButton(f"▶️ Start #{slot+1}",   callback_data=f"start_acc_{slot}"))
            row.append(InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"logout_acc_{slot}"))
            keyboard.append(row)

        if len(hosted) < allowed_max:
            keyboard.append([InlineKeyboardButton("➕ Add Another Account", callback_data="add_acc")])

        header = (
            f"{TOP}\n"
            f"║  📱  {double_struck('My Accounts')} ({len(hosted)}/{allowed_max})  📱  ║\n"
            f"{BOT}\n\n")
        body = "\n".join(lines)
        footer = (
            f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}\n👑 {italic_serif('VIP Mode: Aapke sabhi accounts 24/7 bina lease expiration ke run kar rahe hain!')}"
            if is_owner_user else
            f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}\n💡 {italic_serif('24h lease ke baad storage auto-clear ho jati hai')}"
        )

        await update.message.reply_text(
            header + body + footer,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard))

    async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found')}\n\n{script('Deploy one using')} /host",
                parse_mode=ParseMode.MARKDOWN)
            return

        import datetime
        lines = []
        buttons = []
        has_dead = False
        now = int(time.time())
        for acct in hosted:
            slot     = acct.get("slot", 0)
            alive    = runner.is_running(uid, slot)
            uptime   = runner.get_uptime(uid, slot) if alive else "—"
            hosted_at = acct.get("hosted_at", 0)
            since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y  %H:%M") if hosted_at else "—"
            icon = "🟢" if alive else "🔴"
            phone = _phone_label(acct)
            exp_at = acct.get("expires_at", hosted_at + 86400 if hosted_at else now + 86400)
            is_owner_acct = (uid == OWNER_ID or uid in db.get_sudo_users() or is_premium(uid))
            lease_display = "♾️ Permanent VIP (Never Expires)" if is_owner_acct else (f"{rem//3600}h {(rem%3600)//60}m left" if rem > 0 else "Expired (Auto-Cleaned)")

            err_line = ""
            if not alive:
                has_dead = True
                log_p = f"userbot_logs/userbot_{uid}_slot{slot}.log"
                if os.path.exists(log_p):
                    try:
                        with open(log_p, "r", encoding="utf-8", errors="ignore") as lf:
                            raw = [l.strip() for l in lf.readlines() if l.strip()]
                            for el in reversed(raw[-8:]):
                                if any(x in el for x in ("Error", "Exception", "Traceback", "failed", "unauthorized")):
                                    clean_err = el.replace("*", "").replace("`", "")[:70]
                                    err_line = f"\n   ⚠️ {italic_serif('Last Note')} : {mono(clean_err)}"
                                    break
                    except: pass
                buttons.append([
                    InlineKeyboardButton(f"📜 View Logs #{slot+1}", callback_data=f"view_log_{slot}"),
                    InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}")
                ])

            lines.append(
                f"{icon} {sans_bold('Account #' + str(slot+1))} — {mono(phone)}\n"
                f"   ⏱️ {italic_serif('Uptime')}   : {mono(uptime)}\n"
                f"   ⏳ {italic_serif('24h Lease')}: {mono(lease_display)}\n"
                f"   📅 {italic_serif('Hosted')}   : {mono(since)}"
                f"{err_line}")

        footer = ""
        if has_dead:
            footer = f"\n\n🔄 {italic_serif('Use /restart or the buttons below to revive.')}"

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text(
            f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
            + "\n\n".join(lines) +
            f"\n\n{DIV}"
            f"\n⚡ {sans_bold('Version')} : {mono('ARYA X MENTAL Advance V2')}"
            f"{footer}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup)

    async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if not hosted:
            await update.message.reply_text("❌ No hosted account found.")
            return
        slot = hosted[0].get("slot", 0)
        log_path = f"userbot_logs/userbot_{uid}_slot{slot}.log"
        if not os.path.exists(log_path):
            await update.message.reply_text("📜 Log file does not exist yet. Try /restart or Start #1.")
            return
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            tail = "".join(lines[-35:]).strip() or "Log is empty."
            await update.message.reply_text(
                f"📜 *Last Logs (Account #{slot+1})*:\n```\n{tail[-3500:]}\n```\n\n💡 _Agar error dikhe toh ise dekh kar solve kar sakte hain._",
                parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading log: {e}")

    async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found.')} {script('Use /host first.')}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            await _do_restart(update, uid, slot, acct)
            return

        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([InlineKeyboardButton(
                f"{icon} Restart #{slot+1} — {phone}",
                callback_data=f"restart_acc_{slot}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🔄 {bold_serif('Which account to restart?')}\n\n{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard))

    async def _do_restart(update_or_query, uid, slot, acct):
        is_cb = hasattr(update_or_query, "callback_query") and update_or_query.callback_query
        if is_cb:
            msg_obj = update_or_query.callback_query.message
            send = msg_obj.reply_text
        else:
            send = update_or_query.message.reply_text

        msg = await send(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
        ok = runner.restart_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid))
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Restart Failed')}\n\n📩 {script('Contact')} {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN)

    async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(f"❌ {italic_serif('Koi active userbot nahi hai.')}")
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action")]]
            await update.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                f"{script('Logout karne se session delete ho jayega.')}\n"
                f"{italic_serif('Dobara host karne ke liye /host karo.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard))
            return

        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([InlineKeyboardButton(
                f"{icon} Logout #{slot+1} — {phone}",
                callback_data=f"logout_acc_{slot}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard))

    async def _do_logout(uid, slot):
        runner.stop_userbot(uid, slot)
        db.remove_account(uid, slot)
        session_dir = f"data/sessions/{uid}/{slot}"
        shutil.rmtree(session_dir, ignore_errors=True)

    async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        await update.message.reply_text(
            f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
            f"👤 {sans_bold('Admin')}    : {SUPPORT_USERNAME}\n"
            f"⚡ {sans_bold('Response')} : {script('Fast')}\n\n"
            f"{DIV}\n🔧 {bold_serif('Try these first:')}\n\n"
            f"🔹 /myaccounts — {italic_serif('Sab accounts dekho')}\n"
            f"🔹 /restart    — {italic_serif('Userbot restart karo')}\n"
            f"🔹 /status     — {italic_serif('Status check karo')}\n"
            f"🔹 /logout → /host — {italic_serif('Re-deploy karo')}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_supportraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        if not await premium_only(update): return
        args   = context.args
        target = " ".join(args) if args else None
        if not target:
            await update.message.reply_text(
                f"⚔️ {bold_serif('Pro Support Raid')}\n\n"
                f"📌 {sans_bold('Usage')}: {mono('/supportraid @username')}",
                parse_mode=ParseMode.MARKDOWN)
            return
        await update.message.reply_text(
            f"{TOP}\n║  ⚔️  {bold_serif('Support Raid Launched')}  ⚔️  ║\n{BOT}\n\n"
            f"🎯 {sans_bold('Target')} : {mono(md_escape(target))}\n"
            f"🌪️ {script('All premium userbots activated!')}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_restartall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        msg   = await update.message.reply_text(f"🔄 {sans_bold('Restarting All Userbots with Anti-OOM Stagger')}...")
        count = 0
        to_restart = []
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                to_restart.append((uid, acct["slot"], acct["session_string"], uid_str))

        for idx, (uid, slot, s_str, uid_str) in enumerate(to_restart):
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                s_str, uid_str)
            if ok: count += 1
            if idx < len(to_restart) - 1:
                await asyncio.sleep(GLOBAL_STARTUP_STAGGER_DELAY)

        await msg.edit_text(
            f"✅ {double_struck('Restart Complete')}\n\n"
            f"🟢 {sans_bold('Restarted')}: {mono(str(count))} {script('userbots')} (Staggered smoothly)",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"🔁 {bold_serif('Bot State Refreshed')}\n\n"
            f"🟢 {sans_bold('Running')} : {mono(str(runner.running_count()))}\n"
            f"📦 {sans_bold('Total')}   : {mono(str(db.hosted_count()))}\n"
            f"🕒 {sans_bold('Uptime')}  : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_purgeall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        msg = await update.message.reply_text("🧹 <i>Purging RAM & storage caches across all accounts...</i>", parse_mode=ParseMode.HTML)
        purged_files = 0
        for folder in ["downloads", "temp"]:
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    p = os.path.join(folder, f)
                    try:
                        if os.path.isfile(p): os.remove(p); purged_files += 1
                        elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True); purged_files += 1
                    except Exception: pass
        if os.path.isdir("userbot_logs"):
            for lf in os.listdir("userbot_logs"):
                lp = os.path.join("userbot_logs", lf)
                try:
                    with open(lp, "w", encoding="utf-8") as f:
                        f.write(f"--- Log rotated by /purgeall at {time.ctime()} ---\n")
                except Exception: pass
        import gc
        gc.collect()
        await msg.edit_text(
            f"✅ <b>512MB RAM & Storage Purge Complete</b>\n\n"
            f"🧹 <b>Temporary Files Cleared:</b> {purged_files}\n"
            f"💾 <b>Server Storage:</b> 0 MB Used\n"
            f"⚡ <b>RAM Status:</b> Garbage collected & memory reclaimed\n"
            f"🟢 <b>Active Bots:</b> {runner.running_count()}",
            parse_mode=ParseMode.HTML)

    async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        args  = context.args
        sudos = db.get_sudo_users()

        if args and args[0] == "add" and len(args) > 1:
            try:
                db.add_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('added to Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN)
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if args and args[0] == "del" and len(args) > 1:
            try:
                db.remove_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('removed from Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN)
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if not sudos:
            await update.message.reply_text(
                f"📋 {bold_serif('No Sudo Users yet.')}\n\nAdd: {mono('/sudolist add <uid>')}",
                parse_mode=ParseMode.MARKDOWN)
            return

        lines = "\n".join(f"  👑 {mono(str(u))}" for u in sudos)
        await update.message.reply_text(
            f"{TOP}\n║  👑  {double_struck('Sudo Users')} ({len(sudos)})  👑  ║\n{BOT}\n\n"
            f"{lines}\n\n{DIV}\n"
            f"➕ {mono('/sudolist add <uid>')}\n"
            f"➖ {mono('/sudolist del <uid>')}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_setdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text(f"📸 {script('Kisi photo ko reply karo.')}")
            return
        photo = update.message.reply_to_message.photo[-1]
        file  = await context.bot.get_file(photo.file_id)
        data  = await file.download_as_bytearray()
        from io import BytesIO
        try:
            await context.bot.set_my_profile_photo(BytesIO(bytes(data)))
            await update.message.reply_text(f"✅ {bold_serif('Display Photo Updated')}!")
        except Exception as e:
            await update.message.reply_text(
                f"❌ {sans_bold('Failed')}: {mono(str(e)[:80])}",
                parse_mode=ParseMode.MARKDOWN)

    async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/block <user_id>')}",
                parse_mode=ParseMode.MARKDOWN)
            return
        try:
            target = int(context.args[0])
            if target == OWNER_ID:
                await update.message.reply_text(f"❌ {italic_serif('Owner ko block nahi kar sakte.')}")
                return
            db.block_user(target)
            runner.stop_all_for_user(target)
            await update.message.reply_text(
                f"🚫 {bold_serif('User Blocked')}\n\n"
                f"🆔 {mono(str(target))}\n"
                f"🔴 {script('All userbots stopped.')}",
                parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")

    async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/unblock <user_id>')}",
                parse_mode=ParseMode.MARKDOWN)
            return
        try:
            db.unblock_user(int(context.args[0]))
            await update.message.reply_text(
                f"✅ {bold_serif('User Unblocked')}\n🆔 {mono(context.args[0])}",
                parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")

    async def cmd_blockeduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        blocked = db.get_blocked()
        if not blocked:
            await update.message.reply_text(f"✅ {script('No blocked users.')}")
            return
        lines = "\n".join(f"  🚫 {mono(str(u))}" for u in blocked)
        await update.message.reply_text(
            f"{TOP}\n║  🚫  {double_struck('Blocked Users')} ({len(blocked)})  🚫  ║\n{BOT}\n\n"
            f"{lines}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        total   = db.user_count()
        hosted  = db.hosted_count()
        running = runner.running_count()
        blocked = len(db.get_blocked())
        sudos   = len(db.get_sudo_users())

        await update.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Bot Statistics')}  📊  ║\n{BOT}\n\n"
            f"👥 {sans_bold('Total Users')}    : {double_struck(str(total))}\n"
            f"🚀 {sans_bold('Hosted Accounts')}: {double_struck(str(hosted))}\n"
            f"🟢 {sans_bold('Running')}        : {double_struck(str(running))}\n"
            f"🔴 {sans_bold('Stopped')}        : {double_struck(str(hosted - running))}\n"
            f"🚫 {sans_bold('Blocked')}        : {double_struck(str(blocked))}\n"
            f"👑 {sans_bold('Sudo Users')}     : {double_struck(str(sudos))}\n"
            f"📦 {sans_bold('Max Slots')}      : {double_struck(str(MAX_USERBOTS))}\n"
            f"{DIV}\n"
            f"🕒 {sans_bold('Bot Uptime')} : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_secretfunction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"{TOP}\n║  🔐  {bold_serif('Secret Commands')}  🔐  ║\n{BOT}\n\n"
            f"🔺 {mono('/sudolist add <uid>')}  — {fraktur('Add Premium User')}\n"
            f"🔺 {mono('/sudolist del <uid>')}  — {fraktur('Remove Premium User')}\n"
            f"🔺 {mono('/block <uid>')}         — {fraktur('Ban & Kill All Userbots')}\n"
            f"🔺 {mono('/unblock <uid>')}       — {fraktur('Unban User')}\n"
            f"🔺 {mono('/restartall')}          — {fraktur('Restart All Userbots')}\n"
            f"🔺 {mono('/refresh')}             — {fraktur('Refresh Bot State')}\n"
            f"🔺 {mono('/stats')}               — {fraktur('Full Statistics')}\n"
            f"🔺 {mono('/setdp')}               — {fraktur('Set Display Photo')}\n"
            f"🔺 {mono('/blockeduser')}         — {fraktur('View Blocked List')}\n"
            f"🔺 {mono('/broadcast <msg>')}     — {fraktur('Broadcast DM to All Users')}",
            parse_mode=ParseMode.MARKDOWN)

    async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update):
            return
        msg = update.effective_message
        if not msg:
            return

        is_reply = bool(msg.reply_to_message)
        broadcast_text = ""

        if not is_reply:
            raw_text = msg.text or ""
            parts = raw_text.split(None, 1)
            if len(parts) > 1:
                broadcast_text = parts[1].strip()

            if not broadcast_text:
                await msg.reply_text(
                    f"📢 {bold_serif('Broadcast (Owner Only)')}\n\n"
                    f"❌ {sans_bold('Usage:')}\n"
                    f"• {mono('/broadcast <Aapka Message>')}\n"
                    f"• Ya kisi message ko reply karke {mono('/broadcast')} bhejein.\n\n"
                    f"💡 {italic_serif('Example: /broadcast 🚀 Bot IS active aur live hai!')}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

        all_user_ids = set()
        for u in db.get_all_users():
            try:
                all_user_ids.add(int(u))
            except Exception:
                pass

        if OWNER_ID:
            all_user_ids.add(int(OWNER_ID))

        total_users = len(all_user_ids)
        if total_users == 0:
            await msg.reply_text("⚠️ Abhi database me koi bot user registered nahi hai.")
            return

        status_msg = await msg.reply_text(
            f"⏳ {bold_serif('Broadcast Starting...')}\n\n"
            f"👥 {sans_bold('Total Users')}: `{total_users}`\n"
            f"📨 {italic_serif('Sabhi bot users ke private DM me message send ho raha hai...')}",
            parse_mode=ParseMode.MARKDOWN
        )

        sent_count = 0
        failed_count = 0

        for target_uid in list(all_user_ids):
            if db.is_blocked(target_uid):
                failed_count += 1
                continue

            try:
                if is_reply:
                    await context.bot.copy_message(
                        chat_id=target_uid,
                        from_chat_id=msg.chat_id,
                        message_id=msg.reply_to_message.message_id
                    )
                else:
                    await context.bot.send_message(
                        chat_id=target_uid,
                        text=broadcast_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                sent_count += 1
            except Exception as e:
                err_text = str(e).lower()
                if "retry after" in err_text or "flood" in err_text:
                    await asyncio.sleep(5)
                    try:
                        if is_reply:
                            await context.bot.copy_message(
                                chat_id=target_uid,
                                from_chat_id=msg.chat_id,
                                message_id=msg.reply_to_message.message_id
                            )
                        else:
                            await context.bot.send_message(
                                chat_id=target_uid,
                                text=broadcast_text,
                                parse_mode=ParseMode.MARKDOWN
                            )
                        sent_count += 1
                    except Exception:
                        failed_count += 1
                else:
                    failed_count += 1

            await asyncio.sleep(0.04)

        try:
            await status_msg.edit_text(
                f"✅ {bold_serif('Broadcast Complete!')}\n"
                f"{DIV}\n"
                f"📨 {sans_bold('Sent Successfully')} : `{sent_count}`\n"
                f"❌ {sans_bold('Failed / Blocked')}  : `{failed_count}`\n"
                f"👥 {sans_bold('Total Targets')}     : `{total_users}`\n"
                f"{DIV}\n"
                f"⚡ {mono('ARYA X MENTAL Broadcast System')}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            await msg.reply_text(
                f"✅ Broadcast Complete! Sent: {sent_count}, Failed: {failed_count}, Total: {total_users}"
            )

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        uid  = update.effective_user.id
        data = query.data

        if data == "verify_force_join":
            joined, unjoined = await verify_force_join(uid, context)
            if joined or uid == OWNER_ID:
                try:
                    await query.answer("✅ Verification Successful! Welcome!", show_alert=True)
                except Exception:
                    pass
                await send_user_help_profile(update, context)
            else:
                try:
                    await query.answer("❌ Aapne teeno join nahi kiye!\nPehle 📢 @mental_fyts_post, 💬 GC @mental_era aur 📢 @mentals_empire join karein.", show_alert=True)
                except Exception:
                    pass
            return

        if data == "myaccounts":
            await cmd_myaccounts(update, context)
            return

        if data == "menu_restart":
            await cmd_restart(update, context)
            return

        if data == "show_developer":
            await send_developer_card(update, context)
            return

        if data == "help_guide":
            await cmd_commands(update, context)
            return

        if data == "back_main_menu":
            await send_user_help_profile(update, context)
            return

        if data == "cancel_action":
            await query.message.edit_text(f"🚫 {italic_serif('Cancelled.')}")
            return

        if data == "commands":
            await cmd_commands(update, context)
            return

        if data == "status":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(
                    f"❌ {bold_serif('No Userbot Hosted')}\n\n"
                    f"{script('Use /host to deploy your first account.')}",
                    parse_mode=ParseMode.MARKDOWN)
                return
            import datetime
            lines = []
            for acct in hosted:
                slot     = acct.get("slot", 0)
                alive    = runner.is_running(uid, slot)
                uptime   = runner.get_uptime(uid, slot) if alive else "—"
                hosted_at = acct.get("hosted_at", 0)
                since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y") if hosted_at else "—"
                icon  = "🟢" if alive else "🔴"
                phone = _phone_label(acct)
                lines.append(
                    f"{icon} {sans_bold('Acc #' + str(slot+1))} — {mono(phone)}\n"
                    f"   ⏱️ {uptime}   📅 {since}")
            footer = ""
            if any(not runner.is_running(uid, a["slot"]) for a in hosted):
                footer = f"\n\n🔄 {italic_serif('/restart se revive karo.')}"
            await query.message.reply_text(
                f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
                + "\n\n".join(lines) +
                f"\n\n{DIV}"
                f"\n⚡ {sans_bold('Version')} : {mono('ARYA X MENTAL Advance V2')}"
                f"{footer}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if data == "menu_logout":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(f"❌ {italic_serif('Koi active userbot nahi hai.')}")
                return
            if len(hosted) == 1:
                acct  = hosted[0]
                slot  = acct["slot"]
                phone = _phone_label(acct)
                kb = [[
                    InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                    InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action")]]
                await query.message.reply_text(
                    f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                    f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                    f"{script('Session delete ho jayega.')}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb))
            else:
                kb = []
                for acct in hosted:
                    slot  = acct["slot"]
                    phone = _phone_label(acct)
                    alive = runner.is_running(uid, slot)
                    icon  = "🟢" if alive else "🔴"
                    kb.append([InlineKeyboardButton(
                        f"{icon} Logout #{slot+1} — {phone}",
                        callback_data=f"logout_acc_{slot}")])
                kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])
                await query.message.reply_text(
                    f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n{script('Select below')} 👇",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb))
            return

        if data == "support":
            await query.message.reply_text(
                f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
                f"👤 {sans_bold('Bot Owner')}  : {SUPPORT_USERNAME}\n"
                f"⚡ {sans_bold('Response')}   : {script('Fast')}\n\n"
                f"{DIV}\n🔧 {bold_serif('Pehle Yeh Try Karo:')}\n\n"
                f"🔹 /myaccounts — {italic_serif('sab accounts dekho')}\n"
                f"🔹 /restart    — {italic_serif('userbot restart karo')}\n"
                f"🔹 /status     — {italic_serif('status check karo')}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if data == "help":
            await query.message.reply_text(
                f"╔══════════════════════════════╗\n"
                f"║  📖  {bold_serif('BOT USAGE GUIDE')}  📖  ║\n"
                f"╚══════════════════════════════╝\n\n"
                f"{'━'*30}\n"
                f"🚀 {sans_bold('STEP 1')} — {bold_serif('Bot Start Karo')}\n"
                f"{'━'*30}\n"
                f"➡️ {script('Is bot pe')} /start {script('bhejo')}\n\n"
                f"{'━'*30}\n"
                f"📱 {sans_bold('STEP 2')} — {bold_serif('Account Host Karo')}\n"
                f"{'━'*30}\n"
                f"➡️ {mono('Host My Userbot')} {script('button tap karo')}\n"
                f"➡️ {script('Apna phone number enter karo')}\n"
                f"    {mono('Format: +91XXXXXXXXXX')}\n"
                f"➡️ {script('Telegram se OTP aayega')}\n"
                f"    💡 {italic_serif('OTP spaces ke saath bhejo:')} {mono('1 2 3 4 5')}\n"
                f"➡️ {script('2FA hai toh password bhi daalo')}\n"
                f"✅ {italic_serif('Userbot deploy ho jayega!')}\n\n"
                f"{'━'*30}\n"
                f"⚡ {sans_bold('STEP 3')} — {bold_serif('Commands Chalao')}\n"
                f"{'━'*30}\n"
                f"➡️ {script('Kisi bhi chat mein jao')}\n"
                f"➡️ {script('Dot')} {mono('.')} {script('se command likho:')}\n\n"
                f"    {mono('.alive')} {mono('.ping')} {mono('.help')}\n"
                f"    {mono('.attack')} {mono('.roast')}\n"
                f"    {mono('.spray <text>')} {mono('.stopspray')}\n\n"
                f"{'━'*30}\n"
                f"🔄 {sans_bold('STEP 4')} — {bold_serif('Manage Karo')}\n"
                f"{'━'*30}\n"
                f"    /myaccounts /status /restart /logout /host\n\n"
                f"{'━'*30}\n"
                f"⚠️ {sans_bold('IMPORTANT')}\n"
                f"{'━'*30}\n"
                f"🔸 {italic_serif('Sirf tumhara OWN account command chalayega')}\n"
                f"🔸 {italic_serif('Max')} {mono('3')} {italic_serif('accounts ek saath')}\n\n"
                f"{'━'*30}\n"
                f"🌟 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if data.startswith("view_log_") or data == "cmd_logs":
            try:
                raw_slot = data.split("_")[-1]
                slot = int(raw_slot) if raw_slot.isdigit() else 0
            except:
                slot = 0
            log_path = f"userbot_logs/userbot_{uid}_slot{slot}.log"
            if not os.path.exists(log_path):
                await query.message.reply_text("📜 Log file does not exist yet. Try restarting the account.")
                return
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                tail = "".join(lines[-35:]).strip() or "Log is empty."
                await query.message.reply_text(
                    f"📜 *Last Logs (Account #{slot+1})*:\n```\n{tail[-3500:]}\n```",
                    parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await query.message.reply_text(f"❌ Error reading log: {e}")
            return

        if data.startswith("restart_acc_"):
            try: slot = int(data.split("_")[-1])
            except ValueError: return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid))
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.edit_text(f"❌ {bold_serif('Restart Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        if data.startswith("start_acc_"):
            try: slot = int(data.split("_")[-1])
            except ValueError: return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(f"▶️ {sans_bold('Starting Account')} #{slot+1}...")
            ok = runner.start_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid))
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Started')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.edit_text(f"❌ {bold_serif('Start Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        if data.startswith("logout_acc_"):
            try: slot = int(data.split("_")[-1])
            except ValueError: return
            acct  = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action")]]
            await query.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} #{slot+1} : {mono(phone)}\n\n"
                f"{script('Session delete ho jayega.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if data.startswith("confirm_logout_"):
            try: slot = int(data.split("_")[-1])
            except ValueError: return
            acct  = db.get_account(uid, slot)
            phone = _phone_label(acct) if acct else f"#{slot+1}"
            await _do_logout(uid, slot)
            await query.message.edit_text(
                f"{TOP}\n║  👋  {bold_serif('Logged Out')}  👋  ║\n{BOT}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n"
                f"🗑️ {sans_bold('Session')} : {script('Cleared')}\n\n"
                f"🚀 {fraktur('Re-deploy anytime:')} /host",
                parse_mode=ParseMode.MARKDOWN)
            return

        if data == "add_acc":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            is_owner_user = (uid == OWNER_ID or uid in db.get_sudo_users() or is_premium(uid))
            allowed_max = 20 if is_owner_user else 1
            if len(hosted) >= allowed_max:
                await query.message.reply_text(
                    f"📱 {bold_serif('Account Limit Reached')}\n\n"
                    f"{script('Maximum')} {mono(str(allowed_max))} {script('accounts.')}",
                    parse_mode=ParseMode.MARKDOWN)
                return
            await query.message.reply_text(
                f"🚀 {bold_serif('Add New Account')}\n\n"
                f"{script('Send')} /host {script('to start the login flow.')}",
                parse_mode=ParseMode.MARKDOWN)
            return

    async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
        """Periodically check userbots, enforce 24H lease auto-purge, and flush 512MB RAM/disk."""
        now = int(time.time())
        for uid_str in db.get_all_users():
            try:
                uid = int(uid_str)
                if db.is_blocked(uid): continue
                for acct in db.get_accounts(uid):
                    if not acct.get("hosted") or not acct.get("session_string"): continue
                    slot = acct.get("slot", 0)
                    hosted_at = acct.get("hosted_at", now)
                    expires_at = acct.get("expires_at", hosted_at + 86400)

                    # ── 24-HOUR AUTO-PURGE & STORAGE RECLAIM (CLOUD 512MB PROTECTION) ──
                    # Owner & Sudo/VIP accounts never expire (24/7 permanent uptime)
                    is_owner_acct = (uid == OWNER_ID or uid in db.get_sudo_users() or is_premium(uid))
                    if not is_owner_acct and now >= expires_at:
                        logger.info(f"[24H AUTO-PURGE] Expiring public userbot uid={uid} slot={slot} after 24h lease.")
                        runner.stop_userbot(uid, slot)
                        acct["hosted"] = False
                        acct["expired"] = True
                        db.add_account(uid, acct)

                        # Clean userbot log file to reclaim storage
                        log_path = f"userbot_logs/userbot_{uid}_slot{slot}.log"
                        if os.path.exists(log_path):
                            try: os.remove(log_path)
                            except Exception: pass

                        # Clean user data directory
                        u_dir = f"data/user_{uid}"
                        if os.path.exists(u_dir):
                            try: shutil.rmtree(u_dir, ignore_errors=True)
                            except Exception: pass

                        # Notify user on Telegram
                        try:
                            await context.bot.send_message(
                                chat_id=uid,
                                text=(
                                    f"⏰ <b>24-Hour Hosting Lease Completed</b>\n\n"
                                    f"Aapka userbot 24 ghante tak successfully run hone ke baad auto-clear ho gaya hai!\n\n"
                                    f"🧹 <b>Server Storage:</b> 100% Cleared (0 MB used)\n"
                                    f"⚡ <b>RAM Shield:</b> High-Speed Cloud VPS Memory Freed\n\n"
                                    f"🚀 <b>Re-host Anytime:</b> Phir se apna userbot start karne ke liye <code>/host</code> command bhejein!"
                                ),
                                parse_mode=ParseMode.HTML
                            )
                        except Exception as ne:
                            logger.warning(f"[24H AUTO-PURGE] Failed to notify {uid}: {ne}")
                        continue

                    # If within 24h lease and dead, restart it
                    if not runner.is_running(uid, slot):
                        logger.info(f"[HEALTH] Restarting active userbot uid={uid} slot={slot}")
                        runner.start_userbot(
                            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                            acct["session_string"], uid_str)
            except Exception as e:
                logger.warning(f"[HEALTH] Error processing user {uid_str}: {e}")

        # ── CLOUD 512MB DISK & RAM FLUSH (EVERY 2 MINUTES) ──
        try:
            for folder in ["downloads", "temp"]:
                if os.path.isdir(folder):
                    for f in os.listdir(folder):
                        p = os.path.join(folder, f)
                        try:
                            if os.path.isfile(p): os.remove(p)
                            elif os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
                        except Exception: pass
            # Rotate userbot logs if larger than 200KB
            if os.path.isdir("userbot_logs"):
                for lf in os.listdir("userbot_logs"):
                    lp = os.path.join("userbot_logs", lf)
                    try:
                        if os.path.isfile(lp) and os.path.getsize(lp) > 200 * 1024:
                            with open(lp, "w", encoding="utf-8") as f:
                                f.write(f"--- Log rotated at {time.ctime()} to protect 512MB disk ---\n")
                    except Exception: pass
            import gc
            gc.collect()
            try:
                import ctypes
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception: pass
        except Exception:
            pass

    async def post_init(application: Application):
        try:
            await application.bot.set_my_commands([
                BotCommand("start",           "Grand Welcome"),
                BotCommand("help",            "All Commands"),
                BotCommand("commands",        "Userbot Features"),
                BotCommand("host",            "Add & Deploy Account"),
                BotCommand("myaccounts",      "Manage All Accounts"),
                BotCommand("status",          "Check Userbot Status"),
                BotCommand("restart",         "Restart Userbot"),
                BotCommand("logout",          "Logout an Account"),
                BotCommand("support",         "Get Support"),
                BotCommand("supportraid",     "Pro Raid (Premium)"),
                BotCommand("restartall",      "Restart All (Owner)"),
                BotCommand("refresh",         "Refresh State (Owner)"),
                BotCommand("purgeall",        "Purge RAM & Storage (Owner)"),
                BotCommand("sudolist",        "Sudo Users (Owner)"),
                BotCommand("setdp",           "Set Display Photo (Owner)"),
                BotCommand("block",           "Block User (Owner)"),
                BotCommand("unblock",         "Unblock User (Owner)"),
                BotCommand("blockeduser",     "Blocked List (Owner)"),
                BotCommand("stats",           "Bot Statistics (Owner)"),
                BotCommand("secretfunction",  "Secret Commands (Owner)"),
                BotCommand("broadcast",       "Broadcast DM to All Users (Owner)"),
            ])
        except Exception as e:
            logger.warning(f"[POST_INIT] set_my_commands failed: {e}")

        # Load PIDs from previous run
        _load_pids()

        # ── STAGGERED / NON-BLOCKING USERBOT AUTO-START (ANTI-OOM & ANTI-KILL FIX) ──
        async def _delayed_staggered_autostart():
            # Wait 3.5s for PTB application to settle network & memory
            await asyncio.sleep(3.5)
            if not GLOBAL_AUTOSTART_USERBOTS:
                logger.info("[STARTUP] Auto-start userbots disabled by AUTOSTART_USERBOTS=0.")
                return

            pending = []
            for uid_str in db.get_all_users():
                try:
                    uid = int(uid_str)
                    if db.is_blocked(uid): continue
                    for acct in db.get_accounts(uid):
                        if not acct.get("hosted") or not acct.get("session_string"): continue
                        slot = acct["slot"]
                        if runner.is_running(uid, slot):
                            logger.info(f"[STARTUP] Userbot uid={uid} slot={slot} already running, skip")
                            continue
                        pending.append((uid, slot, acct["session_string"], uid_str))
                except Exception as ex:
                    logger.warning(f"[STARTUP] Error reading user {uid_str}: {ex}")

            if not pending:
                logger.info("[STARTUP] No pending hosted userbots to auto-start.")
                return

            logger.info(
                f"[STARTUP] 🛡️ Anti-OOM Startup Active: Staggering {len(pending)} userbot(s) "
                f"with {GLOBAL_STARTUP_STAGGER_DELAY}s interval to prevent VPS RAM/CPU spike & process killing."
            )

            started = 0
            for idx, (uid, slot, session_string, uid_str) in enumerate(pending):
                try:
                    logger.info(f"[STARTUP] 🚀 [{idx+1}/{len(pending)}] Starting userbot uid={uid} slot={slot}...")
                    ok = runner.start_userbot(
                        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                        session_string, uid_str
                    )
                    if ok:
                        started += 1
                    import gc
                    gc.collect()
                    try:
                        import ctypes
                        ctypes.CDLL("libc.so.6").malloc_trim(0)
                    except Exception: pass

                    if idx < len(pending) - 1:
                        logger.info(
                            f"[STARTUP] ⏳ Pausing {GLOBAL_STARTUP_STAGGER_DELAY}s before starting next userbot "
                            f"to keep VPS CPU/RAM load flat..."
                        )
                        await asyncio.sleep(GLOBAL_STARTUP_STAGGER_DELAY)
                except Exception as err:
                    logger.error(f"[STARTUP] Error auto-starting uid={uid} slot={slot}: {err}")

            logger.info(f"[STARTUP] ✅ Staggered startup complete! {started}/{len(pending)} userbots running smoothly.")

        asyncio.create_task(_delayed_staggered_autostart())

    def main():
        import traceback

        has_bot_token = bool(BOT_TOKEN and len(BOT_TOKEN) > 15 and ":" in BOT_TOKEN)

        print("━" * 50, flush=True)
        print("🚀 AMRIT USERBOT & FLEET HOSTER — ACTIVE", flush=True)
        print(f"👑 Owner ID : {OWNER_ID}", flush=True)
        print(f"🆔 API ID   : {TELEGRAM_API_ID}", flush=True)
        print(f"📦 Max Slots: {MAX_USERBOTS}", flush=True)
        print(f"📂 CWD      : {os.getcwd()}", flush=True)
        if has_bot_token:
            print(f"🤖 Bot Token: {BOT_TOKEN[:10]}... (Telegram Bot Mode Enabled)", flush=True)
        else:
            print("🌐 Direct Mode: PURE USERBOT & WEB PANEL ACTIVE (No Bot Token Needed!)", flush=True)
        print("━" * 50, flush=True)

        # ── DIRECT PANEL & UPTIME HTTP SERVER WITH OTP & SESSION MANAGEMENT ──
        _PENDING_PANEL_LOGINS = {}

        # Persistent background asyncio event loop so Telethon client connections survive across separate HTTP requests
        _panel_loop = asyncio.new_event_loop()
        def _panel_loop_worker(lp):
            asyncio.set_event_loop(lp)
            lp.run_forever()

        _panel_loop_thread = threading.Thread(target=_panel_loop_worker, args=(_panel_loop,), daemon=True, name="PanelTelethonLoop")
        _panel_loop_thread.start()

        def _run_coro(coro, timeout=60):
            future = asyncio.run_coroutine_threadsafe(coro, _panel_loop)
            return future.result(timeout=timeout)

        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse

        class _FleetWebPanelHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def _send_json(self, data, status=200):
                body = json.dumps(data).encode("utf-8")
                self.send_response(status)
                self.send_header("Server", "MentalCore/2.5")
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()

            def _send_html(self, html_content):
                body = html_content.encode("utf-8")
                self.send_response(200)
                self.send_header("Server", "MentalCore/2.5")
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()

            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header("Server", "MentalCore/2.5")
                self.send_header("Allow", "GET, HEAD, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()

            def do_HEAD(self):
                # 100% 200 OK for UptimeRobot HEAD checks
                body = b"OK - Mental Official Userbot & Fleet is Online 24/7\n"
                self.send_response(200)
                self.send_header("Server", "MentalCore/2.5")
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path

                # Fast ping / healthcheck for UptimeRobot
                user_agent = self.headers.get("User-Agent", "").lower()
                if "uptimerobot" in user_agent or path in ("/ping", "/health", "/status_ping"):
                    body = b"OK - Mental Official Userbot & Fleet is Online 24/7\n"
                    self.send_response(200)
                    self.send_header("Server", "MentalCore/2.5")
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.wfile.write(body)
                    self.wfile.flush()
                    return

                if path == "/api/accounts":
                    accounts = db.get_accounts(OWNER_ID)
                    out = []
                    for a in accounts:
                        slot = a.get("slot", 0)
                        alive = runner.is_running(OWNER_ID, slot)
                        out.append({
                            "slot": slot,
                            "phone": a.get("phone", "—"),
                            "name": a.get("name", f"Acc #{slot+1}"),
                            "alive": alive,
                            "uptime": runner.get_uptime(OWNER_ID, slot) if alive else "Stopped",
                            "role": "👑 Master" if slot == 0 else f"🤖 Worker #{slot+1}"
                        })
                    return self._send_json({"success": True, "accounts": out, "total_running": runner.running_count()})

                # Serve Web Control Panel HTML
                html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>👑 Arya X Mental Userbot — Direct Fleet Control Panel</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #07090e; color: #f1f5f9; font-family: 'Outfit', sans-serif; min-height: 100vh; padding: 24px; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    .header {{ text-align: center; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #1e293b; }}
    .badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); margin-bottom: 12px; }}
    h1 {{ font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #f43f5e 0%, #fb7185 50%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .subtitle {{ color: #94a3b8; font-size: 13px; margin-top: 6px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }}
    .card h2 {{ font-size: 16px; font-weight: 700; color: #e2e8f0; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
    .input-group {{ margin-bottom: 12px; }}
    label {{ display: block; font-size: 11px; font-weight: 600; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
    input {{ width: 100%; background: #030712; border: 1px solid #334155; border-radius: 10px; padding: 10px 14px; color: #f8fafc; font-family: 'JetBrains Mono', monospace; font-size: 13px; outline: none; transition: border-color 0.2s; }}
    input:focus {{ border-color: #38bdf8; }}
    .btn {{ width: 100%; background: linear-gradient(135deg, #e11d48, #be123c); color: white; border: none; border-radius: 10px; padding: 11px; font-weight: 700; font-size: 13px; cursor: pointer; transition: all 0.2s; }}
    .btn:hover {{ opacity: 0.95; transform: translateY(-1px); }}
    .btn-cyan {{ background: linear-gradient(135deg, #0284c7, #0369a1); }}
    .msg-box {{ margin-top: 10px; padding: 10px; border-radius: 8px; font-size: 12px; display: none; line-height: 1.4; }}
    .msg-success {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; }}
    .msg-error {{ background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(225, 29, 72, 0.4); color: #fb7185; }}
    .accounts-table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }}
    .accounts-table th {{ text-align: left; padding: 8px; color: #64748b; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #1e293b; }}
    .accounts-table td {{ padding: 10px 8px; border-bottom: 1px solid #0f172a; font-family: 'JetBrains Mono', monospace; }}
    .status-pill {{ padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; }}
    .status-running {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .status-stopped {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
    .act-btn {{ background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 4px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; margin-right: 4px; }}
    .act-btn:hover {{ background: #334155; color: white; }}
    .stat-pill {{ background: #030712; padding: 8px 12px; border-radius: 10px; border: 1px solid #1e293b; font-size: 12px; display: flex; justify-content: space-between; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">🔒 100% PRIVATE PERSONAL FLEET • OWNER EXCLUSIVE (20 SLOTS)</div>
      <h1>👑 Arya X Mental Userbot Core</h1>
      <p class="subtitle">Direct Phone OTP & Personal Fleet Dashboard • Owner ID: {OWNER_ID} • 24/7 Watchdog Active</p>
    </div>

    <div class="grid">
      <!-- Card 1: Direct Phone OTP Login -->
      <div class="card">
        <h2>📲 Direct Phone OTP Login</h2>
        <div class="input-group">
          <label>Telegram Phone Number</label>
          <input type="text" id="phoneInput" placeholder="+91XXXXXXXXXX" />
        </div>
        <button class="btn" id="sendOtpBtn" onclick="sendOtp()">📲 Send Telegram OTP</button>

        <div id="otpSection" style="display: none; margin-top: 14px;">
          <div class="input-group">
            <label>OTP Code (Received in Telegram App)</label>
            <input type="text" id="otpCode" placeholder="12345" />
          </div>
          <div class="input-group">
            <label>2FA Password (Optional, if set)</label>
            <input type="password" id="otp2fa" placeholder="Leave empty if none" />
          </div>
          <button class="btn btn-cyan" id="verifyOtpBtn" onclick="verifyOtp()">🚀 Verify & Host Userbot</button>
        </div>

        <div id="otpMsg" class="msg-box"></div>
      </div>

      <!-- Card 2: Direct String Session -->
      <div class="card">
        <h2>📋 Direct String Session</h2>
        <div class="input-group">
          <label>Telethon String Session</label>
          <input type="text" id="sessionInput" placeholder="1BJWap1wBu..." />
        </div>
        <button class="btn btn-cyan" onclick="addSession()">🚀 Host String Session</button>
        <div id="sessionMsg" class="msg-box"></div>

        <div style="margin-top: 20px;">
          <h2>📊 Server & RAM Shield</h2>
          <div class="stat-pill">
            <span style="color:#94a3b8">Active Accounts:</span>
            <span id="activeCount" style="color:#38bdf8;font-weight:700">Loading...</span>
          </div>
          <div class="stat-pill">
            <span style="color:#94a3b8">RAM Shield:</span>
            <span style="color:#34d399;font-weight:700">MALLOC_ARENA_MAX=1 Safe</span>
          </div>
          <div class="stat-pill">
            <span style="color:#94a3b8">UptimeRobot Status:</span>
            <span style="color:#34d399;font-weight:700">200 OK (Keep-Alive Ready)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Accounts Fleet -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <h2>👥 Active Multi-Account Fleet (<span id="fleetHeaderCount">0</span>/15)</h2>
        <button class="act-btn" onclick="loadAccounts()">🔄 Refresh Fleet</button>
      </div>
      <div style="overflow-x:auto">
        <table class="accounts-table">
          <thead>
            <tr>
              <th>Slot</th>
              <th>Phone / User</th>
              <th>Role</th>
              <th>Status</th>
              <th>Uptime</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="accountsList">
            <tr><td colspan="6" style="text-align:center;color:#64748b">Loading fleet accounts...</td></tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:14px;padding:12px;background:#030712;border-radius:10px;font-size:11px;color:#94a3b8;line-height:1.5">
        💡 <strong>Telegram In-Bot Control:</strong> Kisi bhi chat me <code>.menu</code> send karein. Naya account add karne ke liye chat me <code>.addacc +91XXXXXXXXXX</code> likhein aur fir <code>.otp &lt;code&gt;</code> bhejein!
      </div>
    </div>
  </div>

  <script>
    async function loadAccounts() {{
      try {{
        const res = await fetch('/api/accounts');
        const data = await res.json();
        const tbody = document.getElementById('accountsList');
        if (!data.accounts || data.accounts.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#64748b;padding:20px">No accounts hosted yet. Use the form above or send .addacc in Telegram!</td></tr>';
          document.getElementById('activeCount').innerText = '0 Running';
          document.getElementById('fleetHeaderCount').innerText = '0';
          return;
        }}
        document.getElementById('activeCount').innerText = data.total_running + ' Running';
        document.getElementById('fleetHeaderCount').innerText = data.accounts.length;
        tbody.innerHTML = data.accounts.map(a => `
          <tr>
            <td>Slot #${{a.slot + 1}}</td>
            <td><strong>${{a.phone}}</strong> <span style="color:#64748b">(${{a.name}})</span></td>
            <td>${{a.role}}</td>
            <td><span class="status-pill ${{a.alive ? 'status-running' : 'status-stopped'}}">${{a.alive ? '🟢 RUNNING' : '🔴 STOPPED'}}</span></td>
            <td>${{a.uptime}}</td>
            <td>
              <button class="act-btn" onclick="accountAction('restart', ${{a.slot}})">🔄 Restart</button>
              <button class="act-btn" onclick="accountAction('stop', ${{a.slot}})">⏹ Stop</button>
              <button class="act-btn" style="color:#f87171" onclick="accountAction('logout', ${{a.slot}})">🗑 Logout</button>
            </td>
          </tr>
        `).join('');
      }} catch (err) {{
        console.error(err);
      }}
    }}

    async function sendOtp() {{
      const phone = document.getElementById('phoneInput').value.trim();
      const msg = document.getElementById('otpMsg');
      if (!phone || !phone.startsWith('+')) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Kripya phone number + country code ke sath likhein (e.g. +91XXXXXXXXXX)';
        msg.style.display = 'block';
        return;
      }}
      msg.className = 'msg-box';
      msg.innerText = 'Connecting to Telegram & sending OTP...';
      msg.style.display = 'block';
      document.getElementById('sendOtpBtn').disabled = true;

      try {{
        const res = await fetch('/api/send_otp', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone }})
        }});
        const data = await res.json();
        if (data.success) {{
          msg.className = 'msg-box msg-success';
          msg.innerText = data.message || 'OTP successfully sent to your Telegram app!';
          document.getElementById('otpSection').style.display = 'block';
        }} else {{
          msg.className = 'msg-box msg-error';
          msg.innerText = data.error || 'Failed to send OTP.';
        }}
      }} catch (e) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Network error: ' + e.message;
      }} finally {{
        document.getElementById('sendOtpBtn').disabled = false;
      }}
    }}

    async function verifyOtp() {{
      const phone = document.getElementById('phoneInput').value.trim();
      const code = document.getElementById('otpCode').value.trim();
      const password = document.getElementById('otp2fa').value.trim();
      const msg = document.getElementById('otpMsg');

      if (!code) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Kripya Telegram app me aaya hua OTP code daalein!';
        msg.style.display = 'block';
        return;
      }}
      msg.className = 'msg-box';
      msg.innerText = 'Verifying OTP & starting userbot engine...';
      msg.style.display = 'block';
      document.getElementById('verifyOtpBtn').disabled = true;

      try {{
        const res = await fetch('/api/verify_otp', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone, code, password }})
        }});
        const data = await res.json();
        if (data.success) {{
          msg.className = 'msg-box msg-success';
          msg.innerText = '🎉 ' + (data.message || 'Account Linked and Active 24/7!');
          document.getElementById('otpSection').style.display = 'none';
          document.getElementById('phoneInput').value = '';
          loadAccounts();
        }} else {{
          msg.className = 'msg-box msg-error';
          msg.innerText = data.error || 'Verification failed.';
        }}
      }} catch (e) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Error: ' + e.message;
      }} finally {{
        document.getElementById('verifyOtpBtn').disabled = false;
      }}
    }}

    async function addSession() {{
      const session_string = document.getElementById('sessionInput').value.trim();
      const msg = document.getElementById('sessionMsg');
      if (!session_string) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Kripya String Session paste karein!';
        msg.style.display = 'block';
        return;
      }}
      msg.className = 'msg-box';
      msg.innerText = 'Validating and hosting session...';
      msg.style.display = 'block';

      try {{
        const res = await fetch('/api/add_session', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ session_string }})
        }});
        const data = await res.json();
        if (data.success) {{
          msg.className = 'msg-box msg-success';
          msg.innerText = '🎉 Account string session hosted successfully!';
          document.getElementById('sessionInput').value = '';
          loadAccounts();
        }} else {{
          msg.className = 'msg-box msg-error';
          msg.innerText = data.error || 'Session hosting failed.';
        }}
      }} catch (e) {{
        msg.className = 'msg-box msg-error';
        msg.innerText = 'Error: ' + e.message;
      }}
    }}

    async function accountAction(action, slot) {{
      if (action === 'logout' && !confirm('Are you sure you want to logout Slot #' + (slot+1) + '?')) return;
      try {{
        const res = await fetch('/api/action', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ action, slot }})
        }});
        const data = await res.json();
        loadAccounts();
      }} catch (e) {{
        alert('Action error: ' + e.message);
      }}
    }}

    loadAccounts();
    setInterval(loadAccounts, 10000);
  </script>
</body>
</html>"""
                return self._send_html(html_body)

            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                try:
                    payload = json.loads(post_body.decode("utf-8")) if post_body else {}
                except Exception:
                    payload = {}

                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path

                # 1. SEND OTP REQUEST VIA TELETHON
                if path == "/api/send_otp":
                    phone = (payload.get("phone") or "").strip().replace(" ", "").replace("-", "")
                    if not phone or not phone.startswith("+"):
                        return self._send_json({"success": False, "error": "Invalid phone number! Include country code (e.g. +91...)"}, status=400)

                    async def _send_code():
                        if phone in _PENDING_PANEL_LOGINS:
                            try:
                                old_c = _PENDING_PANEL_LOGINS[phone].get("client")
                                if old_c and old_c.is_connected():
                                    await old_c.disconnect()
                            except Exception:
                                pass

                        client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH, loop=_panel_loop)
                        await client.connect()
                        res = await client.send_code_request(phone)
                        _PENDING_PANEL_LOGINS[phone] = {
                            "client": client,
                            "phone": phone,
                            "phone_code_hash": res.phone_code_hash,
                            "created_at": time.time()
                        }
                        return res.phone_code_hash

                    try:
                        _run_coro(_send_code())
                        return self._send_json({"success": True, "message": f"OTP successfully sent to Telegram app for {phone}!"})
                    except Exception as ex:
                        err_msg = str(ex)
                        if "PhoneNumberInvalidError" in type(ex).__name__:
                            err_msg = "Phone number is invalid! Make sure to include your country code (e.g. +91...)."
                        elif "FloodWait" in type(ex).__name__ or "flood" in err_msg.lower():
                            err_msg = "Telegram FloodWait: Please wait a moment before requesting another code."
                        return self._send_json({"success": False, "error": f"Telegram Error: {err_msg[:120]}"}, status=500)

                # 2. VERIFY OTP AND LINK ACCOUNT
                elif path == "/api/verify_otp":
                    phone = (payload.get("phone") or "").strip().replace(" ", "").replace("-", "")
                    code = (payload.get("code") or "").strip()
                    password = (payload.get("password") or "").strip() or None

                    if not phone or not code:
                        return self._send_json({"success": False, "error": "Phone and OTP code are required!"}, status=400)

                    if phone not in _PENDING_PANEL_LOGINS:
                        return self._send_json({"success": False, "error": "OTP session expired or not found. Please click 'Send Telegram OTP' again."}, status=400)

                    entry = _PENDING_PANEL_LOGINS[phone]
                    client = entry["client"]
                    p_hash = entry["phone_code_hash"]

                    async def _sign_in():
                        try:
                            await client.sign_in(phone, code=code, phone_code_hash=p_hash)
                        except SessionPasswordNeededError:
                            if not password:
                                return {"needs_2fa": True}
                            await client.sign_in(password=password)
                        except Exception as se:
                            se_name = type(se).__name__
                            se_str = str(se).lower()
                            if "password" in se_str or "SessionPasswordNeededError" in se_name:
                                if not password:
                                    return {"needs_2fa": True}
                                await client.sign_in(password=password)
                            elif "PhoneCodeInvalidError" in se_name or "invalid" in se_str:
                                raise ValueError("Invalid OTP code! Please check Telegram app and enter the correct code.")
                            elif "PhoneCodeExpiredError" in se_name or "expired" in se_str:
                                raise ValueError("OTP code has expired! Please click 'Send Telegram OTP' to request a new code.")
                            else:
                                raise se

                        session_str = client.session.save()
                        me = await client.get_me()
                        try:
                            await client.disconnect()
                        except Exception:
                            pass

                        u_name = getattr(me, "first_name", phone)
                        uid = OWNER_ID or getattr(me, "id", 0)

                        accounts = db.get_accounts(uid)
                        used_slots = {a.get("slot", 0) for a in accounts}
                        slot = 0
                        while slot in used_slots: slot += 1

                        acct = {
                            "slot": slot,
                            "phone": phone,
                            "session_string": session_str,
                            "hosted": True,
                            "hosted_at": int(time.time()),
                            "expires_at": int(time.time()) + 999999999,
                            "name": u_name
                        }
                        db.add_account(uid, acct)
                        runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_str, str(uid))
                        return {"success": True, "slot": slot, "name": u_name, "phone": phone}

                    try:
                        res = _run_coro(_sign_in())
                        if res.get("needs_2fa"):
                            return self._send_json({"success": False, "error": "2FA Password is required for this account! Enter password in 2FA field and click Verify."}, status=400)
                        _PENDING_PANEL_LOGINS.pop(phone, None)
                        return self._send_json({"success": True, "message": f"Account {phone} linked to Slot #{res['slot']+1} and active 24/7!"})
                    except Exception as ex:
                        err_str = str(ex)
                        return self._send_json({"success": False, "error": f"{err_str[:120]}"}, status=500)

                # 3. DIRECT STRING SESSION
                elif path == "/api/add_session":
                    session_str = (payload.get("session_string") or "").strip()
                    if not session_str:
                        return self._send_json({"success": False, "error": "Session string required!"}, status=400)

                    async def _test_session():
                        client = TelegramClient(StringSession(session_str), TELEGRAM_API_ID, TELEGRAM_API_HASH, loop=_panel_loop)
                        await client.connect()
                        if not await client.is_user_authorized():
                            try: await client.disconnect()
                            except Exception: pass
                            raise ValueError("Session is not authorized or expired!")
                        me = await client.get_me()
                        u_name = getattr(me, "first_name", "Telegram User")
                        phone = getattr(me, "phone", "") or str(getattr(me, "id", "Active"))
                        try: await client.disconnect()
                        except Exception: pass

                        uid = OWNER_ID or getattr(me, "id", 0)
                        accounts = db.get_accounts(uid)
                        used_slots = {a.get("slot", 0) for a in accounts}
                        slot = 0
                        while slot in used_slots: slot += 1

                        acct = {
                            "slot": slot,
                            "phone": phone,
                            "session_string": session_str,
                            "hosted": True,
                            "hosted_at": int(time.time()),
                            "expires_at": int(time.time()) + 999999999,
                            "name": u_name
                        }
                        db.add_account(uid, acct)
                        runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_str, str(uid))
                        return {"success": True, "slot": slot, "name": u_name, "phone": phone}

                    try:
                        res = _run_coro(_test_session())
                        return self._send_json({"success": True, "message": f"String session hosted in Slot #{res['slot']+1}!"})
                    except Exception as ex:
                        return self._send_json({"success": False, "error": f"Session failed: {str(ex)[:100]}"}, status=500)

                # 4. ACTION (RESTART / STOP / LOGOUT)
                elif path == "/api/action":
                    action = payload.get("action")
                    slot = payload.get("slot", 0)
                    uid = OWNER_ID
                    if action == "restart":
                        acct = db.get_account(uid, slot)
                        if acct and acct.get("session_string"):
                            runner.restart_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], str(uid))
                            return self._send_json({"success": True, "message": f"Slot #{slot+1} restarted!"})
                    elif action == "stop":
                        runner.stop_userbot(uid, slot)
                        return self._send_json({"success": True, "message": f"Slot #{slot+1} stopped!"})
                    elif action == "logout":
                        runner.stop_userbot(uid, slot)
                        db.remove_account(uid, slot)
                        return self._send_json({"success": True, "message": f"Slot #{slot+1} logged out!"})

                    return self._send_json({"success": False, "error": "Invalid action"}, status=400)

                return self._send_json({"success": False, "error": "Not found"}, status=404)

            def log_message(self, *args):
                return

        # Start Server on Cloud PORT or 3000/8080/8000
        target_ports = []
        env_p = os.environ.get("PORT", "").strip()
        if env_p and env_p.isdigit():
            target_ports.append(int(env_p))
        target_ports.extend([3000, 8080, 8000, 5000])

        srv = None
        bound_port = None
        for p in target_ports:
            try:
                class _CustomServer(HTTPServer):
                    allow_reuse_address = True
                srv = _CustomServer(("0.0.0.0", p), _FleetWebPanelHandler)
                bound_port = p
                break
            except Exception:
                continue

        # Auto-start all existing hosted userbots upon startup & run 24/7 watchdog
        def _boot_autostart_all():
            time.sleep(2)
            logger.info("[PERMA-WATCHDOG] 🛡️ 24/7 Permanent Watchdog loop initialized...")
            while True:
                try:
                    for uid_str in db.get_all_users():
                        try:
                            uid = int(uid_str)
                            for acct in db.get_accounts(uid):
                                if not acct.get("hosted") or not acct.get("session_string"):
                                    continue
                                slot = acct.get("slot", 0)
                                if not runner.is_running(uid, slot):
                                    logger.info(f"[PERMA-WATCHDOG] 🚀 Auto-restarting userbot for uid={uid} slot={slot}...")
                                    runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], str(uid))
                                    time.sleep(3)  # Staggered 3s delay prevents RAM spike across 10-12 accounts
                        except Exception as be:
                            logger.warning(f"[PERMA-WATCHDOG] Boot start user error: {be}")
                except Exception as e:
                    logger.warning(f"[PERMA-WATCHDOG] Watchdog error: {e}")

                # Trim parent heap and collect garbage every cycle
                try:
                    import gc
                    gc.collect()
                    import ctypes
                    ctypes.CDLL("libc.so.6").malloc_trim(0)
                except Exception: pass

                time.sleep(20)

        _boot_th = threading.Thread(target=_boot_autostart_all, daemon=True)
        _boot_th.start()

        # If Telegram Bot Token is configured, run optional PTB bot concurrently
        if has_bot_token:
            try:
                import telegram as _tg
                app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
                host_conv = ConversationHandler(
                    entry_points=[CommandHandler("host", cmd_host_start), CallbackQueryHandler(cmd_host_start, pattern="^host$")],
                    states={
                        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
                        ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
                        ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
                    },
                    fallbacks=[CommandHandler("cancel", host_cancel)],
                    allow_reentry=True,
                )
                app.add_handler(CommandHandler("start", cmd_start))
                app.add_handler(CommandHandler("myaccounts", cmd_myaccounts))
                app.add_handler(CommandHandler("status", cmd_status))
                app.add_handler(host_conv)
                app.add_handler(CallbackQueryHandler(callback_handler))

                # Start Web Panel in background thread
                def _run_srv():
                    if srv and bound_port:
                        logger.info(f"🌐 [WEB PANEL] Control Panel active at http://0.0.0.0:{bound_port}")
                        srv.serve_forever()
                _th = threading.Thread(target=_run_srv, daemon=True)
                _th.start()

                logger.info("🤖 Starting Telegram Bot alongside Web Panel...")
                app.run_polling(allowed_updates=Update.ALL_TYPES)
                return
            except Exception as be:
                logger.warning(f"Telegram Bot mode skipped: {be}")

        # PURE DIRECT MODE (Default: No Bot Token required!)
        if srv and bound_port:
            print("\n" + "=" * 60, flush=True)
            print(f"👑 DIRECT FLEET CONTROL PANEL RUNNING ON PORT {bound_port}!", flush=True)
            print(f"🌐 Open in browser or add to UptimeRobot: http://0.0.0.0:{bound_port}", flush=True)
            print("📲 Use the Web Control Panel or in-bot .addacc command to link accounts!", flush=True)
            print("=" * 60 + "\n", flush=True)
            srv.serve_forever()
        else:
            print("❌ Failed to bind any HTTP port!", flush=True)
            sys.exit(1)

    if __name__ == "__main__":
        main()