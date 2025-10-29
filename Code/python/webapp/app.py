import os
import csv
import sys
import socket
import logging
import subprocess
import threading
import queue
import uuid
import json
import datetime
import time
from typing import List, Dict, Any, Optional, Tuple
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, stream_with_context, send_file
from io import BytesIO
try:
    import mss  # type: ignore
except Exception:
    mss = None  # type: ignore
try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None  # type: ignore
try:
    import win32gui  # type: ignore
    import win32con  # type: ignore
except Exception:
    win32gui = None  # type: ignore
    win32con = None  # type: ignore

try:
    import win32api  # type: ignore
except Exception:
    win32api = None  # type: ignore

try:
    import win32process  # type: ignore
except Exception:
    win32process = None  # type: ignore
try:
    import win32clipboard  # type: ignore
except Exception:
    win32clipboard = None  # type: ignore
try:
    import win32api, win32con, win32gui  # already imported above but ensure consistency
except Exception:
    pass

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

try:
    import matlab.engine  # type: ignore
except Exception:
    matlab = None  # type: ignore

try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

# 定义Windows常量（防止某些系统缺少这些常量）
if win32con:
    if not hasattr(win32con, 'HWND_TOPMOST'):
        win32con.HWND_TOPMOST = -1
    if not hasattr(win32con, 'HWND_NOTOPMOST'):
        win32con.HWND_NOTOPMOST = -2
    if not hasattr(win32con, 'SWP_NOMOVE'):
        win32con.SWP_NOMOVE = 0x0002
    if not hasattr(win32con, 'SWP_NOSIZE'):
        win32con.SWP_NOSIZE = 0x0001
    if not hasattr(win32con, 'SWP_SHOWWINDOW'):
        win32con.SWP_SHOWWINDOW = 0x0040
    if not hasattr(win32con, 'SW_RESTORE'):
        win32con.SW_RESTORE = 9
    if not hasattr(win32con, 'SW_SHOW'):
        win32con.SW_SHOW = 5

# 减少噪声
logging.getLogger("pyngrok").setLevel(logging.CRITICAL)
logging.getLogger("pyngrok.process.ngrok").setLevel(logging.CRITICAL)
os.environ.setdefault("NGROK_UPDATE", "false")

# 配置waitress日志级别
logging.getLogger("waitress.queue").setLevel(logging.ERROR)
logging.getLogger("waitress").setLevel(logging.WARNING)

# 配置werkzeug日志级别
logging.getLogger("werkzeug").setLevel(logging.WARNING)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("WEBAPP_SECRET_KEY", "dev-secret-key")

# 配置Flask应用
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用静态文件缓存
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大请求体16MB
# 会话 Cookie 基本配置（默认本地开发安全、兼容性）
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 默认本地
app.config['SESSION_COOKIE_SECURE'] = False    # 动态根据请求切换

# 添加请求处理中间件
@app.before_request
def before_request():
    # 设置请求开始时间
    request.start_time = time.time()
    # 更新session访问时间
    update_session_access()
    # 动态判断公网/HTTPS环境，调整会话 Cookie 以避免跨域/HTTPS 丢失
    try:
        xf_proto = (request.headers.get('X-Forwarded-Proto') or '').lower()
        is_https = bool(getattr(request, 'is_secure', False)) or ('https' in xf_proto)
        if is_https:
            # 公网/HTTPS：Chrome 等要求 SameSite=None 必须搭配 Secure
            app.config['SESSION_COOKIE_SECURE'] = True
            app.config['SESSION_COOKIE_SAMESITE'] = 'None'
        else:
            app.config['SESSION_COOKIE_SECURE'] = False
            app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    except Exception:
        pass
    # 强制先进行用户分级（除去分级页与静态/api健康等白名单）
    try:
        path = request.path or "/"
        whitelist = {
            "/role", "/role/set", "/api/role/set", "/health",
            "/api/stream/matlab", "/api/run/stream", "/api/run/poll"
        }
        if path.startswith("/static/") or path.startswith("/api/") and path not in {"/api/stream/matlab", "/api/run/stream", "/api/run/poll"}:
            return None
        if path not in whitelist:
            if not session.get("role"):
                return redirect(url_for("role_select"))
    except Exception:
        pass

@app.after_request
def after_request(response):
    # 记录请求处理时间
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        if duration > 1.0:  # 只记录超过1秒的请求
            print(f"[slow_request] {request.method} {request.path} took {duration:.2f}s")
    
    # 添加性能优化头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

# ---------------- Process runner state ----------------
RUNS: Dict[str, Dict[str, Any]] = {}
RUNS_LOCK = threading.Lock()

# ---------------- Session data storage ----------------
SESSION_DATA: Dict[str, Dict[str, Any]] = {}
SESSION_DATA_LOCK = threading.Lock()

# ---------------- Quick phrases state ----------------
QUICK_PHRASES_FILE = os.path.join(os.path.dirname(__file__), "quick_phrases.json")

# ---------------- MATLAB Engine (lazy) ----------------
MATLAB_ENGINE = None
MATLAB_ENGINE_LOCK = threading.Lock()

def get_matlab_engine():
    global MATLAB_ENGINE
    if matlab is None:
        return None
    with MATLAB_ENGINE_LOCK:
        if MATLAB_ENGINE is None:
            try:
                MATLAB_ENGINE = matlab.engine.start_matlab()
            except Exception:
                MATLAB_ENGINE = None
        return MATLAB_ENGINE

# ---------------- Remote control password storage ----------------
APP_DIR = os.path.dirname(__file__)
REMOTE_MOUSE_PW_FILE = os.path.join(APP_DIR, "remote_mouse_password.txt")
REMOTE_KEYBOARD_PW_FILE = os.path.join(APP_DIR, "remote_keyboard_password.txt")
ROLES_PW_FILE = os.path.join(APP_DIR, "roles_passwords.json")

def _read_password(file_path: str) -> Optional[str]:
    try:
        if not os.path.isfile(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            pw = f.read().strip()
            return pw or None
    except Exception:
        return None

def _ensure_roles_passwords() -> Dict[str, str]:
    # 创建或读取统一的角色密码文件
    try:
        if not os.path.isfile(ROLES_PW_FILE):
            with open(ROLES_PW_FILE, 'w', encoding='utf-8') as f:
                json.dump({"admin": "1234", "user": "1234"}, f, ensure_ascii=False, indent=2)
        with open(ROLES_PW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            admin_pw = str(data.get("admin", "")).strip()
            user_pw = str(data.get("user", "")).strip()
            return {"admin": admin_pw, "user": user_pw}
    except Exception:
        return {"admin": "", "user": ""}


# ---------------- Running Tasks Management ----------------

# 全局运行任务管理
RUNS: Dict[str, Dict[str, Any]] = {}
RUNS_LOCK = threading.Lock()

def resolve_script_by_task(task: str) -> Optional[str]:
    mt_dir, ppo_dir = get_repo_roots()
    # New mapping:
    # ppo -> Parameter design (PPO.py)
    # run_sim -> Simulation verification (run_simulink.py)
    # run_sim_def -> Custom simulation verification (run_defined_simulink.py)
    if task == "ppo":
        path = os.path.join(ppo_dir, "PPO_main.py")
        return path if os.path.isfile(path) else None
    if task == "run_sim":
        path = os.path.join(ppo_dir, "run_simulink.py")
        return path if os.path.isfile(path) else None
    if task == "run_sim_def":
        path = os.path.join(ppo_dir, "run_defined_simulink.py")
        return path if os.path.isfile(path) else None
    return None

def run_python_script_realtime(script_path: str, cwd: Optional[str] = None, extra_args: Optional[List[str]] = None) -> str:
    """运行Python脚本并实时返回输出"""
    run_id = str(uuid.uuid4())
    
    def reader_thread() -> None:
        try:
            cmd = [sys.executable, "-u", script_path]
            if extra_args:
                cmd.extend(extra_args)
            
            env = os.environ.copy()
            env.setdefault("PYTHONIOENCODING", "utf-8")
            env.setdefault("PYTHONUTF8", "1")
            env.setdefault("PYTHONUNBUFFERED", "1")

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=False,
                bufsize=0,
                cwd=cwd,
                env=env,
            )
            
            q: queue.Queue[str] = queue.Queue()
            
            with RUNS_LOCK:
                RUNS[run_id] = {
                    "proc": proc,
                    "queue": q,
                    "buffer": [],
                    "start_time": time.time()
                }
            
            # 读取输出
            assert proc.stdout is not None
            for raw in proc.stdout:
                try:
                    line = smart_decode(raw).rstrip("\r\n")
                except Exception:
                    # Fallback: replace undecodable chars
                    try:
                        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                    except Exception:
                        line = "[decode_error]"
                if line:
                    q.put(line)
                    with RUNS_LOCK:
                        if run_id in RUNS:
                            RUNS[run_id]["buffer"].append(line)
            
            q.put("[runner] __PROC_EOF__")
            
        except Exception as e:
            with RUNS_LOCK:
                if run_id in RUNS:
                    RUNS[run_id]["error"] = str(e)
            print(f"Error in reader_thread: {e}")
    
    # 启动读取线程
    thread = threading.Thread(target=reader_thread, daemon=True)
    thread.start()
    
    return run_id

# ---------------- Role selection (Admin/User) ----------------

def load_roles_passwords() -> Dict[str, str]:
    """从 JSON 文件加载角色密码"""
    try:
        roles_file = os.path.join(os.path.dirname(__file__), "roles_passwords.json")
        with open(roles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading roles passwords: {e}")
        return {"admin": "", "user": ""}

@app.route("/role", methods=["GET"])
def role_select():
    # 简化的用户登录页面，不区分用户类别
    return render_template("role.html", title="用户登录")


@app.route("/role/set", methods=["POST"])
def role_set():
    role = (request.form.get("role") or "").strip()
    password = (request.form.get("password") or "").strip()
    
    if role not in {"admin", "user"}:
        return redirect(url_for("role_select"))
    
    # 从 JSON 文件读取密码进行验证
    roles_passwords = load_roles_passwords()
    expected_password = roles_passwords.get(role, "")
    
    if password == expected_password:
        session["role"] = role
        session["username"] = role
        return redirect(url_for("index"))
    else:
        return render_template("role.html", title="用户登录", error="密码错误")


@app.route("/api/role/set", methods=["POST"])
def api_role_set():
    """用户登录接口"""
    payload = request.get_json(silent=True) or {}
    role = (payload.get("role") or "").strip()
    password = (payload.get("password") or "").strip()
    
    if role not in {"admin", "user"}:
        return jsonify({"error": "invalid_role"}), 400
    
    # 从 JSON 文件读取密码进行验证
    roles_passwords = load_roles_passwords()
    expected_password = roles_passwords.get(role, "")
    
    if password == expected_password:
        session["role"] = role
        session["username"] = role
        return jsonify({"ok": True, "role": role})
    else:
        return jsonify({"error": "bad_password"}), 403


@app.route("/logout", methods=["POST", "GET"])
def logout():
    try:
        session.pop("role", None)
    except Exception:
        pass
    try:
        clear_session_data()
    except Exception:
        pass
    return redirect(url_for("role_select"))

def _get_default_simulink_model_path() -> Optional[str]:
    # 尝试从项目的 Simulink 目录选择一个 .slx 文件作为默认模型
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
        simulink_dir = os.path.join(project_root, 'Simulink')
        if not os.path.isdir(simulink_dir):
            return None
        # 优先常用名
        preferred = [
            'Interleaved_parallel_buck.slx',
            'Interleaved_parallel_buck_test.slx',
        ]
        for name in preferred:
            p = os.path.join(simulink_dir, name)
            if os.path.isfile(p):
                return p
        # 否则取第一个 .slx
        for fn in os.listdir(simulink_dir):
            if fn.lower().endswith('.slx'):
                return os.path.join(simulink_dir, fn)
        return None
    except Exception:
        return None


def require_openai_client() -> Any:
    if OpenAI is None:
        print("[startup] Missing dependency: openai. Install via: pip install openai", file=sys.stderr)
        raise RuntimeError("OpenAI client not installed")
    return OpenAI


def has_server_api_key() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def get_client() -> Any:
    api_key: str = session.get("api_key") or os.environ.get("OPENAI_API_KEY", "").strip()
    base_url: str = session.get("base_url") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").strip()
    if not api_key:
        raise RuntimeError("Missing API key. Set it on the configuration page or via OPENAI_API_KEY.")
    Client = require_openai_client()
    return Client(api_key=api_key, base_url=base_url)


def get_repo_roots() -> Tuple[str, str]:
    # webapp/app.py -> .../Code/python/webapp
    code_python_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    mt_dir = os.path.join(code_python_dir, "MT-ResNet")
    ppo_dir = os.path.join(code_python_dir, "PPO")
    return mt_dir, ppo_dir


def smart_decode(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except Exception:
        try:
            return data.decode("gbk")
        except Exception:
            return data.decode("utf-8", errors="replace")


def run_python_script(script_path: str, cwd: Optional[str] = None, timeout_sec: int = 300, extra_args: Optional[List[str]] = None) -> Tuple[int, str, str]:
    python_exe = sys.executable
    args = [python_exe, "-u", script_path]
    if extra_args:
        args.extend(extra_args)
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONUNBUFFERED", "1")
    try:
        completed = subprocess.run(
            args,
            cwd=cwd or os.path.dirname(script_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            text=False,
            env=env,
        )
        out = smart_decode(completed.stdout or b"")
        err = smart_decode(completed.stderr or b"")
        return completed.returncode, out, err
    except subprocess.TimeoutExpired as exc:
        out = smart_decode(exc.stdout or b"") if hasattr(exc, "stdout") else ""
        err = smart_decode(exc.stderr or b"") if hasattr(exc, "stderr") else "Timeout"
        return 124, out, err
    except Exception as exc:
        return 1, "", f"Execution error: {exc}"




# ---------- Context windowing & summarization ----------





def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"



def normalize_output_format(text: str) -> str:
    """规范化输出格式，确保整洁规范"""
    if not text:
        return ""
    
    import re
    
    # 去除零宽字符和特殊字符
    text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
    
    # 规范化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 处理转义的换行符
    text = text.replace('\\n', '\n')
    
    # 修复标点符号被错误换行的问题
    text = re.sub(r'([：。，；！？])\s*\n\s*', r'\1 ', text)
    text = re.sub(r'([：。，；！？])\s*\n', r'\1 ', text)
    
    # 修复不合理的换行 - 在句子中间被强制换行的情况
    text = re.sub(r'([^。！？\n])\s*\n\s*([^#\*\-\d\s])', r'\1 $2', text)
    
    # 修复公式和计算中的换行问题
    text = re.sub(r'([=≈<>])\s*\n\s*', r'\1 ', text)
    text = re.sub(r'([A-Za-z_]+)\s*\n\s*([=≈<>])', r'\1 $2', text)
    
    # 修复更多格式问题
    text = re.sub(r'([a-zA-Z0-9])\s*\n\s*([a-zA-Z0-9])', r'\1$2', text)
    text = re.sub(r'(\d+)\s*\n\s*([a-zA-Z%Ωμµ]+)', r'\1$2', text)
    
    # 修复括号内容被换行分割
    text = re.sub(r'\(\s*\n\s*', r'(', text)
    text = re.sub(r'\s*\n\s*\)', r')', text)
    
    # 修复引号内容被换行分割
    text = re.sub(r'["""\']\s*\n\s*', r'"', text)
    text = re.sub(r'\s*\n\s*["""\']', r'"', text)
    
    # 修复冒号后的不必要换行
    text = re.sub(r'：\s*\n\s*([^#\*\-\d\s])', r'：$1', text)
    
    # 更强力的换行修复 - 处理更多边缘情况
    text = re.sub(r'([\u4e00-\u9fff])\s*\n\s*([\u4e00-\u9fff])', r'\1$2', text)
    text = re.sub(r'([a-zA-Z])\s*\n\s*([a-zA-Z])', r'\1$2', text)
    text = re.sub(r'(\d+)\s*\n\s*([%Ωμµ°C°F])', r'\1$2', text)
    
    # 修复括号内的换行
    text = re.sub(r'（\s*\n\s*', r'（', text)
    text = re.sub(r'\s*\n\s*）', r'）', text)
    
    # 修复方括号内的换行
    text = re.sub(r'\[\s*\n\s*', r'[', text)
    text = re.sub(r'\s*\n\s*\]', r']', text)
    
    # 修复数学符号前后的换行
    text = re.sub(r'([+\-*/=<>])\s*\n\s*', r'\1 ', text)
    text = re.sub(r'\s*\n\s*([+\-*/=<>])', r' $1', text)
    
    # 修复单位符号前的换行
    text = re.sub(r'(\d+)\s*\n\s*(V|A|W|Hz|kHz|MHz|GHz|Ω|F|μF|mF|H|μH|mH)', r'\1$2', text)
    
    # 合并多余空行（最多保留两个连续换行）
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 去除首尾空行
    text = re.sub(r'^\n+', '', text)
    text = re.sub(r'\n+$', '', text)
    
    return text


def clean_saved_content(text: str) -> str:
    """清理保存内容中的转义字符，确保保存格式正确"""
    if not text:
        return ""
    
    # 处理转义的换行符
    text = text.replace('\\n', '\n')
    
    # 处理其他转义字符
    text = text.replace('\\t', '\t')
    text = text.replace('\\r', '\r')
    
    # 确保换行符正确
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text

# ---------------- Session data management ----------------

def get_session_id() -> str:
    """获取或创建session ID"""
    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
    return session_id


def get_session_data(key: str, default: Any = None) -> Any:
    """从服务器端存储获取session数据"""
    session_id = get_session_id()
    with SESSION_DATA_LOCK:
        if session_id not in SESSION_DATA:
            SESSION_DATA[session_id] = {}
        return SESSION_DATA[session_id].get(key, default)


def set_session_data(key: str, value: Any) -> None:
    """设置服务器端session数据"""
    session_id = get_session_id()
    with SESSION_DATA_LOCK:
        if session_id not in SESSION_DATA:
            SESSION_DATA[session_id] = {}
        SESSION_DATA[session_id][key] = value


def clear_session_data() -> None:
    """清空服务器端session数据"""
    session_id = get_session_id()
    with SESSION_DATA_LOCK:
        if session_id in SESSION_DATA:
            SESSION_DATA[session_id] = {}


def cleanup_old_sessions() -> None:
    """清理旧的session数据（超过1小时未使用）"""
    current_time = time.time()
    with SESSION_DATA_LOCK:
        to_remove = []
        for session_id, data in SESSION_DATA.items():
            last_access = data.get("last_access", 0)
            if current_time - last_access > 3600:  # 1小时
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del SESSION_DATA[session_id]


def update_session_access() -> None:
    """更新session访问时间"""
    session_id = get_session_id()
    with SESSION_DATA_LOCK:
        if session_id in SESSION_DATA:
            SESSION_DATA[session_id]["last_access"] = time.time()


@app.route("/", methods=["GET"])
def index():
    # 简化的主页面，直接显示功能界面
    if not session.get("role"):
        return redirect(url_for("role_select"))
    return render_template("main.html")


@app.route("/health", methods=["GET"])
def health():
    try:
        _ = require_openai_client()
        return jsonify({"status": "ok"}), 200
    except Exception as exc:
        return jsonify({"status": "error", "detail": str(exc)}), 500

# --------- Lightweight ping endpoint for measuring preview latency ---------
@app.route("/api/preview/ping", methods=["GET"])
def api_preview_ping():
    # Simple endpoint to measure round-trip time from client
    # Optionally include server timestamp for future use
    return jsonify({"ok": True, "server_ts": time.time()})

@app.route("/api/run/start", methods=["POST"])
def run_start():
    payload = request.json or {}
    task = (payload.get("task") or "").strip()
    # Allowed values after remapping
    if task not in {"ppo", "run_sim", "run_sim_def"}:
        return jsonify({"error": "invalid_task"}), 400
    script = resolve_script_by_task(task)
    if not script:
        return jsonify({"error": "script_not_found"}), 404
    run_id = run_python_script_realtime(script_path=script)

    # Wait briefly for the startup line to be appended to buffer to avoid double printing
    initial_next = 0
    for _ in range(50):  # up to ~500ms
        with RUNS_LOCK:
            info = RUNS.get(run_id, {})
            initial_next = len(info.get("buffer", []))
        if initial_next > 0:
            break
        import time as _t
        _t.sleep(0.01)

    return jsonify({"run_id": run_id, "next": initial_next})

@app.route("/api/run/once", methods=["POST"])
def run_once():
    payload = request.json or {}
    task = (payload.get("task") or "").strip()
    timeout_sec = int(os.environ.get("TOOL_TIMEOUT", "300"))
    if task not in {"ppo", "run_sim", "run_sim_def"}:
        return jsonify({"error": "invalid_task"}), 400
    script = resolve_script_by_task(task)
    if not script:
        return jsonify({"error": "script_not_found"}), 404
    code, out, err = run_python_script(script_path=script, timeout_sec=timeout_sec)
    return jsonify({"returncode": code, "stdout": out, "stderr": err})

@app.route("/api/run/stream", methods=["GET"])
def run_stream():
    run_id = (request.args.get("run_id") or "").strip()
    if not run_id:
        return Response("event: error\ndata: missing_run_id\n\n", mimetype="text/event-stream")

    with RUNS_LOCK:
        info = RUNS.get(run_id)
    if not info:
        return Response("event: error\ndata: run_not_found\n\n", mimetype="text/event-stream")

    q: "queue.Queue[str]" = info["queue"]
    proc: subprocess.Popen = info["proc"]

    def gen():
        last_line = None
        while True:
            try:
                line = q.get(timeout=0.5)  # 增加超时时间
            except Exception:
                if proc.poll() is not None:
                    break
                yield ": keep-alive\n\n"
                continue
            if line == "[runner] __PROC_EOF__":
                break
            if line == last_line:
                continue
            last_line = line
            # 确保输出立即刷新
            yield f"data: {line}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return Response(
        stream_with_context(gen()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/run/poll", methods=["GET"])
def run_poll():
    run_id = (request.args.get("run_id") or "").strip()
    cursor_str = (request.args.get("cursor") or "0").strip()
    try:
        cursor = int(cursor_str)
    except Exception:
        cursor = 0
    
    with RUNS_LOCK:
        info = RUNS.get(run_id)
        if not info:
            return jsonify({"error": "run_not_found"}), 404
        buf: List[str] = info.setdefault("buffer", [])
        proc: subprocess.Popen = info["proc"]
    
    # 检查进程是否还在运行
    if proc.poll() is not None and not buf:
        return jsonify({"lines": [], "next": cursor, "done": True})
    
    if cursor < 0 or cursor > len(buf):
        cursor = 0
    lines = buf[cursor:]
    done = False
    if lines and lines[-1] == "[runner] __PROC_EOF__":
        done = True
    elif proc.poll() is not None and not lines:
        done = True
    
    return jsonify({"lines": lines, "next": cursor + len(lines), "done": done})


@app.route("/api/run/input", methods=["POST"])
def run_input():
    payload = request.json or {}
    run_id = (payload.get("run_id") or "").strip()
    text = (payload.get("text") or "").replace("\r", "")
    if not run_id:
        return jsonify({"error": "missing_run_id"}), 400
    with RUNS_LOCK:
        info = RUNS.get(run_id)
    if not info:
        return jsonify({"error": "run_not_found"}), 404
    proc: subprocess.Popen = info["proc"]
    try:
        assert proc.stdin is not None
        # 追加换行，模拟按下回车键
        proc.stdin.write((text + "\n").encode("utf-8"))
        proc.stdin.flush()
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/run/stop", methods=["POST"])
def run_stop():
    payload = request.json or {}
    run_id = (payload.get("run_id") or "").strip()
    if not run_id:
        return jsonify({"error": "missing_run_id"}), 400
    with RUNS_LOCK:
        info = RUNS.pop(run_id, None)
    if not info:
        return jsonify({"error": "run_not_found"}), 404
    proc: subprocess.Popen = info["proc"]
    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@app.route("/run", methods=["GET"])
def run_page():
    task = (request.args.get("task") or "").strip()
    if task not in {"ppo", "run_sim", "run_sim_def", "eda"}:
        return redirect(url_for("index"))
    return render_template("run.html", title="AI+电力电子 - 运行", task=task)

@app.route("/schematic_editor", methods=["GET"])
def schematic_editor_page():
    """原理图编辑器页面 - 双相交错并联Buck整体设计"""
    return render_template("schematic_editor.html")

@app.route("/custom_schematic_editor", methods=["GET"])
def custom_schematic_editor_page():
    """自定义原理图设计编辑器页面"""
    return render_template("custom_schematic_editor.html")

@app.route("/database_manager", methods=["GET"])
def database_manager_page():
    """数据库维护管理页面"""
    if not session.get("role"):
        return redirect(url_for("role_select"))
    return render_template("database_manager.html")


# ==================== 数据库维护管理 API ====================

class CSVDataManager:
    """CSV数据文件管理类"""
    
    def __init__(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.data_dirs = {
            'Input_Data': os.path.join(root, "Data", "Input_Data"),
            'Visualization': os.path.join(root, "Visualization")
        }
        self.base_dir = root
    
    def get_all_csv_files(self):
        """获取所有CSV文件"""
        csv_files = []
        for dir_name, dir_path in self.data_dirs.items():
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.endswith('.csv'):
                        csv_files.append({
                            'name': file,
                            'display_name': f"{dir_name}/{file}",
                            'path': os.path.join(dir_path, file),
                            'directory': dir_name
                        })
        return csv_files
    
    def get_csv_file_path(self, display_name):
        """根据显示名称获取文件路径"""
        parts = display_name.split('/', 1)
        if len(parts) == 2:
            dir_name, file_name = parts
            if dir_name in self.data_dirs:
                return os.path.join(self.data_dirs[dir_name], file_name)
        return None
    
    def get_csv_info(self, file_path):
        """获取CSV文件信息"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return {
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'shape': df.shape
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_csv_data(self, file_path, page=1, per_page=50, search_query=None):
        """获取CSV文件数据（支持分页和搜索）"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # 搜索
            if search_query:
                mask = df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
                df = df[mask]
            
            total = len(df)
            
            # 分页
            start = (page - 1) * per_page
            end = start + per_page
            df_page = df.iloc[start:end]
            
            # 将NaN替换为None（在JSON中会转换为null）
            df_page = df_page.replace({pd.NA: None, float('nan'): None})
            df_page = df_page.where(pd.notnull(df_page), None)
            
            # 转换为字典列表，添加行索引
            data = []
            for idx, row in df_page.iterrows():
                row_dict = {'_index': int(idx)}
                row_dict.update(row.to_dict())
                data.append(row_dict)
            
            return {
                'data': data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_record(self, file_path, index, data):
        """更新记录"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # 移除索引字段
            if '_index' in data:
                del data['_index']
            
            # 更新数据
            for col, value in data.items():
                if col in df.columns:
                    # 尝试转换数据类型
                    try:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            if value == '' or pd.isna(value):
                                df.at[index, col] = None
                            else:
                                df.at[index, col] = pd.to_numeric(value)
                        else:
                            df.at[index, col] = value
                    except:
                        df.at[index, col] = value
            
            # 保存
            df.to_csv(file_path, index=False)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_record(self, file_path, index):
        """删除记录"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            df = df.drop(index)
            df.to_csv(file_path, index=False)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_record(self, file_path, data):
        """添加记录"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # 移除索引字段
            if '_index' in data:
                del data['_index']
            
            # 创建新行
            new_row = {}
            for col in df.columns:
                if col in data:
                    value = data[col]
                    # 尝试转换数据类型
                    try:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            if value == '' or pd.isna(value):
                                new_row[col] = None
                            else:
                                new_row[col] = pd.to_numeric(value)
                        else:
                            new_row[col] = value
                    except:
                        new_row[col] = value
                else:
                    new_row[col] = None
            
            # 添加新行
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(file_path, index=False)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_csv(self, file_path, uploaded_file):
        """导入CSV文件（覆盖原文件）"""
        try:
            import pandas as pd
            # 读取原文件获取列信息
            original_df = pd.read_csv(file_path)
            original_columns = set(original_df.columns)
            
            # 读取上传的文件
            uploaded_df = pd.read_csv(uploaded_file)
            uploaded_columns = set(uploaded_df.columns)
            
            # 检查列是否一致
            if original_columns != uploaded_columns:
                missing_cols = original_columns - uploaded_columns
                extra_cols = uploaded_columns - original_columns
                error_msg = "数据格式不一致！\n"
                if missing_cols:
                    error_msg += f"缺少列: {', '.join(missing_cols)}\n"
                if extra_cols:
                    error_msg += f"多余列: {', '.join(extra_cols)}"
                return {'success': False, 'error': error_msg}
            
            # 备份原文件
            backup_path = file_path + f'.backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # 保存新文件
            uploaded_df.to_csv(file_path, index=False)
            
            return {'success': True, 'rows_imported': len(uploaded_df)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_stats(self):
        """获取文件统计信息"""
        stats = {}
        import pandas as pd
        for dir_name, dir_path in self.data_dirs.items():
            if os.path.exists(dir_path):
                csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
                stats[dir_name] = {
                    'file_count': len(csv_files),
                    'files': []
                }
                for file in csv_files:
                    file_path = os.path.join(dir_path, file)
                    file_size = os.path.getsize(file_path)
                    modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    try:
                        df = pd.read_csv(file_path)
                        row_count = len(df)
                    except:
                        row_count = 0
                    
                    stats[dir_name]['files'].append({
                        'name': file,
                        'size_kb': round(file_size / 1024, 2),
                        'rows': row_count,
                        'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
        return stats
    
    def scan_old_files(self, days):
        """扫描超过指定天数未修改的文件"""
        from datetime import timedelta
        cutoff_date = datetime.datetime.now() - timedelta(days=days)
        old_files = []
        
        for root, dirs, files in os.walk(self.base_dir):
            # 跳过某些系统目录
            if '.git' in root or '__pycache__' in root or 'node_modules' in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if modified_time < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        rel_path = os.path.relpath(file_path, self.base_dir)
                        old_files.append({
                            'path': rel_path,
                            'full_path': file_path,
                            'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'size_kb': round(file_size / 1024, 2),
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        })
                except:
                    continue
        
        # 按修改时间排序
        old_files.sort(key=lambda x: x['modified'])
        return old_files
    
    def delete_files(self, file_paths):
        """删除指定的文件"""
        results = {'success': [], 'failed': []}
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    results['success'].append(file_path)
                else:
                    results['failed'].append({'path': file_path, 'error': '文件不存在'})
            except Exception as e:
                results['failed'].append({'path': file_path, 'error': str(e)})
        
        return results
    
    def check_corrupted_files(self):
        """检查损坏的文件（所有文件类型）"""
        corrupted_files = []
        
        for root, dirs, files in os.walk(self.base_dir):
            # 跳过某些系统目录
            if '.git' in root or '__pycache__' in root or 'node_modules' in root or '.slxc' in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.base_dir)
                
                try:
                    # 检查文件是否可访问
                    if not os.path.exists(file_path):
                        corrupted_files.append({
                            'path': rel_path,
                            'full_path': file_path,
                            'type': '未知',
                            'error': '文件不存在或无法访问'
                        })
                        continue
                    
                    # 获取文件大小
                    file_size = os.path.getsize(file_path)
                    
                    # 检查文件大小异常（0字节）
                    if file_size == 0:
                        corrupted_files.append({
                            'path': rel_path,
                            'full_path': file_path,
                            'type': self._get_file_type(file),
                            'error': '文件大小为0字节（空文件）'
                        })
                        continue
                    
                    # 针对不同文件类型进行检查
                    if file.endswith('.csv'):
                        # CSV文件检查
                        try:
                            import pandas as pd
                            df = pd.read_csv(file_path)
                            if len(df) == 0:
                                corrupted_files.append({
                                    'path': rel_path,
                                    'full_path': file_path,
                                    'type': 'CSV',
                                    'error': 'CSV文件无数据'
                                })
                            elif len(df.columns) == 0:
                                corrupted_files.append({
                                    'path': rel_path,
                                    'full_path': file_path,
                                    'type': 'CSV',
                                    'error': 'CSV文件无列'
                                })
                        except Exception as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': 'CSV',
                                'error': f'CSV格式错误: {str(e)}'
                            })
                    
                    elif file.endswith('.json'):
                        # JSON文件检查
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json.load(f)
                        except json.JSONDecodeError as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': 'JSON',
                                'error': f'JSON格式错误: {str(e)}'
                            })
                        except Exception as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': 'JSON',
                                'error': f'无法读取: {str(e)}'
                            })
                    
                    elif file.endswith(('.py', '.m', '.txt', '.md', '.html', '.bat')):
                        # 文本文件检查
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                f.read()
                        except UnicodeDecodeError:
                            try:
                                with open(file_path, 'r', encoding='gbk') as f:
                                    f.read()
                            except Exception as e:
                                corrupted_files.append({
                                    'path': rel_path,
                                    'full_path': file_path,
                                    'type': self._get_file_type(file),
                                    'error': f'文件编码错误: {str(e)}'
                                })
                        except Exception as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': self._get_file_type(file),
                                'error': f'无法读取: {str(e)}'
                            })
                    
                    elif file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        # 图片文件检查
                        try:
                            with open(file_path, 'rb') as f:
                                header = f.read(8)
                                if len(header) < 8:
                                    corrupted_files.append({
                                        'path': rel_path,
                                        'full_path': file_path,
                                        'type': '图片',
                                        'error': '文件头不完整，可能已损坏'
                                    })
                        except Exception as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': '图片',
                                'error': f'无法读取: {str(e)}'
                            })
                    
                    elif file.endswith('.zip'):
                        # ZIP文件检查
                        try:
                            import zipfile
                            with zipfile.ZipFile(file_path, 'r') as zip_file:
                                bad_file = zip_file.testzip()
                                if bad_file:
                                    corrupted_files.append({
                                        'path': rel_path,
                                        'full_path': file_path,
                                        'type': 'ZIP',
                                        'error': f'压缩文件损坏: {bad_file}'
                                    })
                        except Exception as e:
                            corrupted_files.append({
                                'path': rel_path,
                                'full_path': file_path,
                                'type': 'ZIP',
                                'error': f'压缩文件错误: {str(e)}'
                            })
                
                except Exception as e:
                    corrupted_files.append({
                        'path': rel_path,
                        'full_path': file_path,
                        'type': '未知',
                        'error': f'检查时出错: {str(e)}'
                    })
        
        return corrupted_files
    
    def _get_file_type(self, filename):
        """获取文件类型描述"""
        ext = os.path.splitext(filename)[1].lower()
        type_map = {
            '.csv': 'CSV',
            '.json': 'JSON',
            '.py': 'Python',
            '.m': 'MATLAB',
            '.txt': '文本',
            '.md': 'Markdown',
            '.html': 'HTML',
            '.bat': '批处理',
            '.png': 'PNG图片',
            '.jpg': 'JPG图片',
            '.jpeg': 'JPEG图片',
            '.gif': 'GIF图片',
            '.zip': 'ZIP压缩',
            '.keras': 'Keras模型',
            '.h5': 'HDF5',
            '.pkl': 'Pickle',
            '.npz': 'NumPy',
            '.mat': 'MATLAB数据',
        }
        return type_map.get(ext, f'{ext[1:].upper()}文件' if ext else '未知')


# 初始化数据管理器
csv_data_manager = CSVDataManager()


@app.route('/api/db/files', methods=['GET'])
def db_get_files():
    """获取所有CSV文件"""
    files = csv_data_manager.get_all_csv_files()
    return jsonify({'success': True, 'files': files})


@app.route('/api/db/file/info', methods=['GET'])
def db_get_file_structure():
    """获取文件结构"""
    display_name = request.args.get('file')
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    info = csv_data_manager.get_csv_info(file_path)
    if 'error' in info:
        return jsonify({'success': False, 'error': info['error']})
    
    return jsonify({'success': True, **info})


@app.route('/api/db/file/data', methods=['GET'])
def db_get_file_records():
    """获取文件数据"""
    display_name = request.args.get('file')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', None)
    
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    result = csv_data_manager.get_csv_data(file_path, page, per_page, search)
    
    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']})
    
    return jsonify({'success': True, **result})


@app.route('/api/db/file/record', methods=['POST'])
def db_create_record():
    """创建记录"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以创建记录'})
    
    data = request.json
    display_name = data.get('file')
    record_data = data.get('data')
    
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    result = csv_data_manager.add_record(file_path, record_data)
    return jsonify(result)


@app.route('/api/db/file/record/<int:record_index>', methods=['PUT'])
def db_update_record_route(record_index):
    """更新记录"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以编辑记录'})
    
    data = request.json
    display_name = data.get('file')
    record_data = data.get('data')
    
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    result = csv_data_manager.update_record(file_path, record_index, record_data)
    return jsonify(result)


@app.route('/api/db/file/record/<int:record_index>', methods=['DELETE'])
def db_delete_record_route(record_index):
    """删除记录"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以删除记录'})
    
    display_name = request.args.get('file')
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    result = csv_data_manager.delete_record(file_path, record_index)
    return jsonify(result)


@app.route('/api/db/file/import', methods=['POST'])
def db_import_csv():
    """导入CSV文件"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以导入数据'})
    
    display_name = request.form.get('file')
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件上传'})
    
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})
    
    if not uploaded_file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': '只支持CSV文件'})
    
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path:
        return jsonify({'success': False, 'error': '文件路径无效'})
    
    result = csv_data_manager.import_csv(file_path, uploaded_file)
    return jsonify(result)


@app.route('/api/db/file/export', methods=['GET'])
def db_export_csv():
    """导出CSV文件"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以导出数据'})
    
    display_name = request.args.get('file')
    file_path = csv_data_manager.get_csv_file_path(display_name)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    return send_file(file_path, as_attachment=True, download_name=display_name.replace('/', '_'))


@app.route('/api/db/stats', methods=['GET'])
def db_get_stats():
    """获取统计信息"""
    stats = csv_data_manager.get_file_stats()
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/db/cleanup/scan', methods=['POST'])
def db_scan_old_files():
    """扫描旧文件"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以扫描文件'})
    
    data = request.json
    period = data.get('period', 'month')
    
    days_map = {
        'week': 7,
        'month': 30,
        'half_year': 180,
        'year': 365
    }
    
    days = days_map.get(period, 30)
    old_files = csv_data_manager.scan_old_files(days)
    
    return jsonify({'success': True, 'files': old_files, 'count': len(old_files)})


@app.route('/api/db/cleanup/delete', methods=['POST'])
def db_delete_old_files():
    """删除旧文件"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以删除文件'})
    
    data = request.json
    file_paths = data.get('files', [])
    
    results = csv_data_manager.delete_files(file_paths)
    
    return jsonify({
        'success': True,
        'deleted_count': len(results['success']),
        'failed_count': len(results['failed']),
        'details': results
    })


@app.route('/api/db/cleanup/check_corrupted', methods=['GET'])
def db_check_corrupted():
    """检查损坏的文件"""
    # 检查用户权限
    if not session.get('role') or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '权限不足：只有管理员可以检查文件'})
    
    corrupted = csv_data_manager.check_corrupted_files()
    return jsonify({'success': True, 'files': corrupted, 'count': len(corrupted)})



def maybe_start_ngrok(port: int) -> Optional[str]:
    # 默认不启用，需显式设置 NGROK_ENABLED=1
    enabled = os.environ.get("NGROK_ENABLED", "1").strip() in {"1", "true", "True", "YES", "yes"}
    if not enabled:
        print("[startup] 公网访问未启用。设置 NGROK_ENABLED=1(并配置 NGROK_AUTHTOKEN)以生成公网地址")
        return None
    try:
        from pyngrok import ngrok, conf
        # 不再使用任何默认token，必须显式配置 NGROK_AUTHTOKEN
        authtoken = os.environ.get("NGROK_AUTHTOKEN", "32h2gdIW04qFjVnTERxYRemGSWB_5HmvaBa4tzL4hrgFXnCxQ").strip()
        if not authtoken:
            print("[ngrok] 未配置 NGROK_AUTHTOKEN，已跳过启动。", file=sys.stderr)
            print(f"[startup] 请分享固定公网地址: https://ai_power_electronics.aipowerelectronics.top")
            return None
        region = os.environ.get("NGROK_REGION", "auto").strip()
        domain = os.environ.get("NGROK_DOMAIN", "").strip()  # 新增：配置固定域名

        # DNS可达性预检测，避免在网络不可达时频繁报错
        try:
            import socket
            # 先检测 DNS 解析
            socket.gethostbyname("connect.ngrok-agent.com")
            # 再检测到 443 的连通性（短超时）
            with socket.create_connection(("connect.ngrok-agent.com", 443), timeout=3):
                pass
        except Exception:
            print("[ngrok] connect.ngrok-agent.com:443 不可达，跳过本轮启动", file=sys.stderr)
            return None
        c = conf.get_default()
        if authtoken:
            c.auth_token = authtoken
        if region:
            c.region = region
            
        try:
            for t in ngrok.get_tunnels():
                try:
                    ngrok.disconnect(t.public_url)
                except Exception:
                    pass
        except Exception:
            pass
            
        # 使用固定域名配置启动隧道
        if domain:
            try:
                public_tunnel = ngrok.connect(
                    addr=port,
                    proto="http",
                    bind_tls=True,
                    domain=domain  # 使用固定域名
                )
                print(f"[startup] 使用固定域名: {domain}")
            except Exception as e:
                print(f"[startup] 固定域名配置失败，切换到动态域名: {e}", file=sys.stderr)
                public_tunnel = ngrok.connect(addr=port, proto="http", bind_tls=True)
        else:
            public_tunnel = ngrok.connect(addr=port, proto="http", bind_tls=True)
            
        public_url = public_tunnel.public_url
        return public_url
    except Exception as exc:
        print(f"[startup] 启动 ngrok 失败（已忽略，仅影响公网访问）: {exc}", file=sys.stderr)
        return None


def _ngrok_watchdog(port: int) -> None:
    """后台守护：定期检查ngrok隧道，断开则尝试重连。
    仅在NGROK_ENABLED为真时运行。
    """
    try:
        from pyngrok import ngrok
    except Exception:
        return
    enabled = os.environ.get("NGROK_ENABLED", "0").strip() in {"1", "true", "True", "YES", "yes"}
    if not enabled:
        return
    failures = 0
    while True:
        try:
            tunnels = []
            try:
                tunnels = ngrok.get_tunnels()
            except Exception:
                tunnels = []
            if not tunnels:
                # 无token时不重试，避免无谓日志
                if not os.environ.get("NGROK_AUTHTOKEN", "").strip():
                    return
                print("[ngrok] 隧道丢失，尝试重连...", file=sys.stderr)
                try:
                    if maybe_start_ngrok(port):
                        failures = 0
                    else:
                        failures += 1
                except Exception:
                    failures += 1
        except Exception as _:
            failures += 1
        # 若连续失败达到8次（~16分钟内退避），停止重试避免刷屏
        if failures >= 8:
            print("[ngrok] 连续失败次数过多，停止重试。", file=sys.stderr)
            return
        # 退避：失败越多，等待越久，最多10分钟
        delay = 120 * max(1, min(5, failures))
        import time as _t
        _t.sleep(delay)


# ---------------- MATLAB/Simulink MJPEG streaming (optional) ----------------

def _find_window_rect(target: str = "auto") -> Optional[Tuple[int, int, int, int]]:
    """Detect MATLAB or Simulink main window rectangle on Windows.
    Returns (left, top, right, bottom) or None if unavailable.
    """
    if win32gui is None:
        return None

    wanted = []
    t = (target or "auto").lower()
    if t == "matlab":
        wanted = ["MATLAB"]
    elif t == "simulink":
        wanted = ["Simulink"]
    else:
        wanted = ["Simulink", "MATLAB"]

    matches: list[Tuple[int, Tuple[int, int, int, int]]] = []

    def _enum_handler(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd) or ""
            if not title:
                return
            for kw in wanted:
                if kw.lower() in title.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    # 过滤最小化窗口
                    if rect and (rect[2] - rect[0] > 100) and (rect[3] - rect[1] > 100):
                        matches.append((hwnd, rect))
                        return
        except Exception:
            return

    try:
        win32gui.EnumWindows(_enum_handler, None)
    except Exception:
        return None

    if not matches:
        return None
    # 选取面积最大的匹配窗口
    hwnd, rect = max(matches, key=lambda x: (x[1][2] - x[1][0]) * (x[1][3] - x[1][1]))
    return rect


def _find_window_hwnd(target: str = "auto") -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
    """Return (hwnd, rect) for MATLAB/Simulink-related top-level window.
    Strategy:
    1) Title contains desired keywords
    2) Or process executable ends with matlab.exe (requires psutil + win32process)
    Select the largest visible window.
    """
    if win32gui is None:
        return None
    wanted = []
    t = (target or "auto").lower()
    if t == "matlab":
        wanted = ["MATLAB"]
    elif t == "simulink":
        wanted = ["Simulink"]
    else:
        wanted = ["Simulink", "MATLAB"]

    matches: list[Tuple[int, Tuple[int, int, int, int]]] = []

    def _enum_handler(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd) or ""
            if not title:
                title = ""
            rect = win32gui.GetWindowRect(hwnd)
            if not rect or (rect[2] - rect[0] <= 100) or (rect[3] - rect[1] <= 100):
                return

            title_hit = any(kw.lower() in (title.lower() if title else "") for kw in wanted)
            proc_hit = False
            if not title_hit and win32process is not None and psutil is not None:
                try:
                    tid, pid = win32process.GetWindowThreadProcessId(hwnd)
                    p = psutil.Process(pid)
                    exe = (p.name() or "").lower()
                    if exe.endswith("matlab.exe"):
                        proc_hit = True
                except Exception:
                    proc_hit = False

            if title_hit or proc_hit:
                matches.append((hwnd, rect))
        except Exception:
            return

    try:
        win32gui.EnumWindows(_enum_handler, None)
    except Exception:
        return None
    if not matches:
        return None
    return max(matches, key=lambda x: (x[1][2] - x[1][0]) * (x[1][3] - x[1][1]))


def _grab_frame(rect: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
    """Capture a screenshot (full screen or region) and return JPEG bytes."""
    bbox = None
    if rect is not None:
        left, top, right, bottom = rect
        width = max(1, right - left)
        height = max(1, bottom - top)
        bbox = {"left": int(left), "top": int(top), "width": int(width), "height": int(height)}

    try:
        if mss is not None:
            with mss.mss() as sct:
                monitor = bbox or sct.monitors[1]
                img = sct.grab(monitor)
                if Image is not None:
                    pil_img = Image.frombytes("RGB", img.size, img.rgb)
                    buf = BytesIO()
                    pil_img.save(buf, format="JPEG", quality=80)
                    return buf.getvalue()
                return None
        if Image is not None:
            try:
                from PIL import ImageGrab  # type: ignore
            except Exception:
                return None
            if bbox is None:
                pil_img = ImageGrab.grab()
            else:
                box = (bbox["left"], bbox["top"], bbox["left"] + bbox["width"], bbox["top"] + bbox["height"])
                pil_img = ImageGrab.grab(bbox=box)
            buf = BytesIO()
            pil_img = pil_img.convert("RGB")
            pil_img.save(buf, format="JPEG", quality=80)
            return buf.getvalue()
        return None
    except Exception:
        return None


def _mjpeg_generator(target: str = "auto", fps: int = 5):
    interval = max(1, int(1000 / max(1, fps))) / 1000.0
    boundary = b"--frame"
    try:
        # 优化：target=screen 时复用单个 mss 实例以降低开销
        if str(target).lower() == "screen" and mss is not None and Image is not None:
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    # 动态质量：高帧率降低质量以减小编码耗时
                    jpeg_quality = 60 if fps >= 30 else (70 if fps >= 15 else 80)
                    while True:
                        img = sct.grab(monitor)
                        pil_img = Image.frombytes("RGB", img.size, img.rgb)
                        buf = BytesIO()
                        pil_img.save(buf, format="JPEG", quality=jpeg_quality)
                        frame = buf.getvalue()
                        yield boundary + b"\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n" + frame + b"\r\n"
                        time.sleep(interval)
            except GeneratorExit:
                return
            except Exception:
                pass
        # 回退：优先窗口区域；若未找到且目标不是 screen，则输出黑屏，避免展示非目标内容
        while True:
            tgt = str(target).lower()
            frame = None
            
            # 普通用户特殊处理：只显示MATLAB/Simulink窗口，否则黑屏
            if session.get("role") == "user":
                # 检查是否有MATLAB/Simulink窗口
                matlab_rect = _find_window_rect("matlab")
                simulink_rect = _find_window_rect("simulink")
                
                if matlab_rect or simulink_rect:
                    # 有MATLAB或Simulink窗口时，显示全屏内容
                    frame = _grab_frame(None)
                else:
                    # 没有MATLAB/Simulink窗口时，显示黑屏
                    frame = None
            else:
                # 管理员保持原有逻辑
                rect = None if tgt == "screen" else _find_window_rect(target)
                frame = _grab_frame(rect)
                if frame is None:
                    if tgt == "screen":
                        frame = _grab_frame(None)
                    else:
                        frame = None
            
            if frame is None:
                if Image is not None:
                    img = Image.new("RGB", (640, 360), (0, 0, 0))
                    buf = BytesIO()
                    img.save(buf, format="JPEG", quality=70)
                    frame = buf.getvalue()
                else:
                    time.sleep(interval)
                    continue
            yield boundary + b"\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n" + frame + b"\r\n"
            time.sleep(interval)
    except GeneratorExit:
        return
    except Exception:
        return


@app.route("/api/stream/matlab", methods=["GET"])
def stream_matlab():
    if os.environ.get("STREAM_ENABLED", "1").strip() not in {"1", "true", "True", "YES", "yes"}:
        return jsonify({"error": "stream_disabled"}), 403
    if os.name != "nt":
        return jsonify({"error": "windows_only"}), 400
    if (mss is None and Image is None):
        return jsonify({"error": "missing_capture_deps", "detail": "install mss or pillow"}), 500

    target = (request.args.get("target") or "auto").strip()
    try:
        fps = int(request.args.get("fps") or "5")
    except Exception:
        fps = 5

    return Response(
        stream_with_context(_mjpeg_generator(target=target, fps=fps)),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


# ---------------- Windows 窗口控制 API ----------------

def _move_resize_window(hwnd: int, left: int, top: int, width: int, height: int) -> bool:
    try:
        if win32gui is None:
            return False
        # 尝试解除置顶/最小化状态
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        except Exception:
            pass
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception:
            pass
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        win32gui.MoveWindow(hwnd, int(left), int(top), int(max(1, width)), int(max(1, height)), True)
        return True
    except Exception:
        return False


def _set_window_topmost(hwnd: int, topmost: bool = True) -> bool:
    try:
        if win32gui is None or win32con is None:
            return False
        flag_hwnd = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(
            hwnd,
            flag_hwnd,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
        )
        return True
    except Exception:
        return False


def _minimize_other_windows():
    """最小化除MATLAB/Simulink外的所有窗口"""
    try:
        if win32gui is None or win32con is None:
            return False
        matlab_simulink_hwnds = set()
        
        # 收集MATLAB/Simulink窗口句柄
        def collect_target_windows(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = win32gui.GetWindowText(hwnd) or ""
                if ("MATLAB" in title or "matlab" in title.lower() or 
                    "Simulink" in title or "simulink" in title.lower()):
                    matlab_simulink_hwnds.add(hwnd)
            except Exception:
                return
        win32gui.EnumWindows(collect_target_windows, None)
        
        # 最小化其他窗口
        def minimize_other_windows(hwnd, _):
            try:
                if hwnd in matlab_simulink_hwnds:
                    return
                if not win32gui.IsWindowVisible(hwnd):
                    return
                # 跳过系统窗口和桌面
                if win32gui.GetParent(hwnd) != 0:
                    return
                title = win32gui.GetWindowText(hwnd) or ""
                if not title:  # 跳过无标题窗口
                    return
                # 最小化窗口
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            except Exception:
                return
        win32gui.EnumWindows(minimize_other_windows, None)
        return True
    except Exception:
        return False


@app.route("/api/window/info", methods=["GET"])
def api_window_info():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    target = (request.args.get("target") or "auto").strip()
    res = _find_window_hwnd(target)
    if not res:
        diag = {
            "found": False,
            "reason": "no_match",
            "deps": {
                "win32gui": bool(win32gui),
                "win32process": bool(win32process),
                "psutil": bool(psutil)
            },
            "target": target
        }
        return jsonify(diag)
    hwnd, rect = res
    left, top, right, bottom = rect
    info = {
        "found": True,
        "hwnd": hwnd,
        "rect": {"left": left, "top": top, "right": right, "bottom": bottom, "width": right - left, "height": bottom - top}
    }
    # 附加进程名供诊断
    try:
        if win32process is not None and psutil is not None:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            p = psutil.Process(pid)
            info["process"] = {"pid": pid, "name": p.name()}
    except Exception:
        pass
    return jsonify(info)


@app.route("/api/window/activate", methods=["POST"])
def api_window_activate():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    target = (request.json or {}).get("target", "auto")
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    errors = []
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    except Exception as e:
        errors.append(f"show:{e}")
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception as e:
        errors.append(f"restore:{e}")
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        errors.append(f"fg:{e}")
    if errors:
        return jsonify({"ok": True, "warnings": errors})
    return jsonify({"ok": True})


@app.route("/api/window/maximize", methods=["POST"])
def api_window_maximize():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    target = (request.json or {}).get("target", "auto")
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/window/topmost", methods=["POST"])
def api_window_topmost():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    target = data.get("target", "auto")
    enable = bool(data.get("enable", True))
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    ok = _set_window_topmost(hwnd, enable)
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": "topmost_failed"}), 500


@app.route("/api/window/minimize_others", methods=["POST"])
def api_window_minimize_others():
    """最小化除MATLAB/Simulink外的所有窗口（仅普通用户）"""
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    # 仅普通用户可调用
    if session.get("role") != "user":
        return jsonify({"error": "user_only"}), 403
    ok = _minimize_other_windows()
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": "minimize_failed"}), 500


@app.route("/api/window/minimize", methods=["POST"])
def api_window_minimize():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    target = (request.json or {}).get("target", "auto")
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/window/restore", methods=["POST"])
def api_window_restore():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    target = (request.json or {}).get("target", "auto")
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/window/move_resize", methods=["POST"])
def api_window_move_resize():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    target = data.get("target", "auto")
    left = int(data.get("left", 0))
    top = int(data.get("top", 0))
    width = int(data.get("width", 1280))
    height = int(data.get("height", 720))
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    ok = _move_resize_window(hwnd, left, top, width, height)
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": "move_resize_failed"}), 500


@app.route("/api/window/fit_screen", methods=["POST"])
def api_window_fit_screen():
    if os.name != "nt" or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    target = data.get("target", "auto")
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    try:
        # 获取主屏幕分辨率
        if win32api is not None:
            width = win32api.GetSystemMetrics(0)
            height = win32api.GetSystemMetrics(1)
        else:
            width, height = 1920, 1080
        ok = _move_resize_window(hwnd, 0, 0, width, height)
        return jsonify({"ok": bool(ok)}) if ok else (jsonify({"error": "fit_failed"}), 500)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------- Simulink 缩放/实际大小 API ----------------

def _simulink_set_zoom(zoom: str = "100%", model: Optional[str] = None) -> Tuple[bool, str]:
    eng = get_matlab_engine()
    if eng is None:
        return False, "matlab_engine_not_available"
    try:
        # 确保打开 Simulink
        try:
            eng.eval("ver('simulink');", nargout=0)
        except Exception:
            pass
        # 确定目标系统
        target_sys = None
        if model:
            try:
                eng.load_system(model, nargout=0)
                target_sys = model
            except Exception as e:
                # 若 load_system 失败，继续尝试使用当前/根模型
                target_sys = None
        if target_sys is None:
            try:
                target_sys = eng.bdroot(nargout=1)
                if not target_sys:
                    target_sys = None
            except Exception:
                target_sys = None
        if target_sys is None:
            try:
                models = eng.find_system('SearchDepth', 0)
                if models:
                    target_sys = models[0]
            except Exception:
                pass
        # 若仍无打开模型，尝试自动打开项目默认模型
        if target_sys is None:
            default_model_path = _get_default_simulink_model_path()
            if default_model_path:
                try:
                    eng.load_system(default_model_path, nargout=0)
                    # bdroot 可能返回文件名对应的系统名
                    target_sys = eng.bdroot(nargout=1)
                except Exception as e:
                    return False, f"auto_open_failed:{e}"
        if target_sys is None:
            return False, "no_open_model"

        # 归一化 zoom 输入
        zl = (str(zoom) or "").strip().lower()
        candidates: list[str] = []
        if zl in {"actual", "actualsize", "actual_size", "100%", "100"}:
            candidates = ["100", "100%"]
        elif zl in {"fit", "fitview", "fit to view", "fit_to_view"}:
            # 不同版本的 Simulink 接受不同关键字，逐个尝试
            candidates = ["FitSystem", "Fit to view", "fit to view", "fit"]
        else:
            v = zl.replace("%", "")
            if v.isdigit():
                candidates = [v, f"{v}%"]
            else:
                candidates = [str(zoom)]

        errors: list[str] = []
        for c in candidates:
            try:
                eng.set_param(target_sys, 'ZoomFactor', c, nargout=0)
                return True, "ok"
            except Exception as e:
                errors.append(f"{c}:{e}")
                continue
        return False, ";".join(errors) or "set_param_failed"
    except Exception as e:
        return False, f"error:{e}"


@app.route("/api/simulink/zoom", methods=["POST"])
def api_simulink_zoom():
    data = request.json or {}
    zoom = str(data.get("zoom", "100%"))
    model = data.get("model")
    ok, msg = _simulink_set_zoom(zoom, model)
    if ok:
        return jsonify({"ok": True, "zoom": zoom, "model": model or "auto"})
    return jsonify({"error": msg}), 500


@app.route("/api/simulink/actual_size", methods=["POST"])
def api_simulink_actual_size():
    ok, msg = _simulink_set_zoom("100%", (request.json or {}).get("model"))
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": msg}), 500


@app.route("/api/simulink/fit_view", methods=["POST"])
def api_simulink_fit_view():
    ok, msg = _simulink_set_zoom("fit to view", (request.json or {}).get("model"))
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": msg}), 500


# ---------------- 远程鼠标控制（Windows） ----------------

def _window_client_area(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
    try:
        rect = win32gui.GetWindowRect(hwnd)
        return rect  # (left, top, right, bottom)
    except Exception:
        return None


def is_mouse_authed() -> bool:
    try:
        # 管理员免密
        if session.get("role") == "admin":
            return True
        # 普通用户需完成控制验证
        return bool(get_session_data("mouse_authed", False)) and bool(get_session_data("user_control_verified", False))
    except Exception:
        return False


def is_keyboard_authed() -> bool:
    try:
        if session.get("role") == "admin":
            return True
        return bool(get_session_data("keyboard_authed", False))
    except Exception:
        return False


@app.route("/api/remote_control/verify", methods=["POST"])
def api_remote_control_verify():
    # 普通用户用于启用远程鼠标控制的会话级验证
    role = session.get("role")
    if role == "admin":
        set_session_data("user_control_verified", True)
        return jsonify({"ok": True, "role": role})
    if role != "user":
        return jsonify({"error": "no_role"}), 403
    payload = request.json or {}
    pw = (payload.get("password") or "").strip()
    # 与角色登录密码隔离：这里仅校验远程鼠标专用密码文件
    required = _read_password(REMOTE_MOUSE_PW_FILE) or ""
    if required and pw != required:
        return jsonify({"error": "bad_password"}), 403
    set_session_data("user_control_verified", True)
    return jsonify({"ok": True})


@app.route("/api/input/mouse_click", methods=["POST"])
def api_mouse_click():
    if os.name != "nt" or win32gui is None or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    # password check (mouse)
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    target = (data.get("target") or "auto").strip()
    button = (data.get("button") or "left").strip().lower()  # left|right
    x = float(data.get("x", 0))
    y = float(data.get("y", 0))
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, _ = res
    area = _window_client_area(hwnd)
    if not area:
        return jsonify({"error": "rect_failed"}), 500
    left, top, right, bottom = area
    abs_x = int(left + x)
    abs_y = int(top + y)
    try:
        # 移动并点击
        win32api.SetCursorPos((abs_x, abs_y))
        if button == 'right':
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
        else:
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_move", methods=["POST"])
def api_mouse_move():
    if os.name != "nt" or win32api is None or win32gui is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    target = (data.get("target") or "auto").strip()
    x = float(data.get("x", 0))
    y = float(data.get("y", 0))
    res = _find_window_hwnd(target)
    if not res:
        return jsonify({"error": "not_found"}), 404
    hwnd, rect = res
    left, top, right, bottom = rect
    try:
        win32api.SetCursorPos((int(left + x), int(top + y)))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_wheel", methods=["POST"])
def api_mouse_wheel():
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    # 普通用户仅允许在 MATLAB/Simulink 活动窗口进行滚轮
    try:
        if session.get("role") == "user":
            res = _find_window_hwnd("auto")
            if not res:
                return jsonify({"error": "matlab_not_running"}), 403
            hwnd, _ = res
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
    except Exception:
        pass
    delta = int(data.get("delta", 120))  # 正为上滚，负为下滚
    try:
        win32api.mouse_event(0x0800, 0, 0, delta, 0)  # MOUSEEVENTF_WHEEL
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- 远程键盘输入（Windows） ----------------

def _get_virtual_key_code(key: str) -> Optional[int]:
    """获取虚拟键码"""
    if not key:
        return None
    
    # 字母键
    if len(key) == 1 and key.isalpha():
        return ord(key.upper())
    
    # 数字键
    if len(key) == 1 and key.isdigit():
        return ord(key)
    
    # 特殊键映射
    key_map = {
        # 功能键
        'F1': win32con.VK_F1, 'F2': win32con.VK_F2, 'F3': win32con.VK_F3, 'F4': win32con.VK_F4,
        'F5': win32con.VK_F5, 'F6': win32con.VK_F6, 'F7': win32con.VK_F7, 'F8': win32con.VK_F8,
        'F9': win32con.VK_F9, 'F10': win32con.VK_F10, 'F11': win32con.VK_F11, 'F12': win32con.VK_F12,
        
        # 方向键
        'ArrowUp': win32con.VK_UP, 'ArrowDown': win32con.VK_DOWN,
        'ArrowLeft': win32con.VK_LEFT, 'ArrowRight': win32con.VK_RIGHT,
        'Up': win32con.VK_UP, 'Down': win32con.VK_DOWN,
        'Left': win32con.VK_LEFT, 'Right': win32con.VK_RIGHT,
        
        # 编辑键
        'Backspace': win32con.VK_BACK, 'Delete': win32con.VK_DELETE,
        'Insert': win32con.VK_INSERT, 'Home': win32con.VK_HOME,
        'End': win32con.VK_END, 'PageUp': win32con.VK_PRIOR,
        'PageDown': win32con.VK_NEXT,
        
        # 控制键
        'Enter': win32con.VK_RETURN, 'Tab': win32con.VK_TAB,
        'Escape': win32con.VK_ESCAPE, 'Space': win32con.VK_SPACE,
        'CapsLock': win32con.VK_CAPITAL, 'NumLock': win32con.VK_NUMLOCK,
        'ScrollLock': win32con.VK_SCROLL,
        
        # 小键盘
        'Numpad0': win32con.VK_NUMPAD0, 'Numpad1': win32con.VK_NUMPAD1,
        'Numpad2': win32con.VK_NUMPAD2, 'Numpad3': win32con.VK_NUMPAD3,
        'Numpad4': win32con.VK_NUMPAD4, 'Numpad5': win32con.VK_NUMPAD5,
        'Numpad6': win32con.VK_NUMPAD6, 'Numpad7': win32con.VK_NUMPAD7,
        'Numpad8': win32con.VK_NUMPAD8, 'Numpad9': win32con.VK_NUMPAD9,
        'NumpadAdd': win32con.VK_ADD, 'NumpadSubtract': win32con.VK_SUBTRACT,
        'NumpadMultiply': win32con.VK_MULTIPLY, 'NumpadDivide': win32con.VK_DIVIDE,
        'NumpadDecimal': win32con.VK_DECIMAL, 'NumpadEnter': win32con.VK_RETURN,
        
        # 标点符号
        'Semicolon': ord(';'), 'Equal': ord('='), 'Comma': ord(','),
        'Minus': ord('-'), 'Period': ord('.'), 'Slash': ord('/'),
        'Backquote': ord('`'), 'BracketLeft': ord('['), 'Backslash': ord('\\'),
        'BracketRight': ord(']'), 'Quote': ord("'"),
        
        # 其他常用键
        'PrintScreen': win32con.VK_SNAPSHOT, 'Pause': win32con.VK_PAUSE,
        'ContextMenu': win32con.VK_APPS,
        
        # 浏览器和系统键
        'BrowserBack': win32con.VK_BROWSER_BACK,
        'BrowserForward': win32con.VK_BROWSER_FORWARD,
        'BrowserRefresh': win32con.VK_BROWSER_REFRESH,
        'BrowserStop': win32con.VK_BROWSER_STOP,
        'BrowserSearch': win32con.VK_BROWSER_SEARCH,
        'BrowserFavorites': win32con.VK_BROWSER_FAVORITES,
        'BrowserHome': win32con.VK_BROWSER_HOME,
        
        # 音量控制
        'VolumeMute': win32con.VK_VOLUME_MUTE,
        'VolumeDown': win32con.VK_VOLUME_DOWN,
        'VolumeUp': win32con.VK_VOLUME_UP,
        
        # 媒体控制
        'MediaNextTrack': win32con.VK_MEDIA_NEXT_TRACK,
        'MediaPreviousTrack': win32con.VK_MEDIA_PREV_TRACK,
        'MediaStop': win32con.VK_MEDIA_STOP,
        'MediaPlayPause': win32con.VK_MEDIA_PLAY_PAUSE,
        
        # 启动键
        'LaunchMail': win32con.VK_LAUNCH_MAIL,
        'LaunchMediaSelect': win32con.VK_LAUNCH_MEDIA_SELECT,
        'LaunchApp1': win32con.VK_LAUNCH_APP1,
        'LaunchApp2': win32con.VK_LAUNCH_APP2,
        
        # 特殊字符（通过Shift+数字键产生）
        'Digit1': ord('1'), 'Digit2': ord('2'), 'Digit3': ord('3'),
        'Digit4': ord('4'), 'Digit5': ord('5'), 'Digit6': ord('6'),
        'Digit7': ord('7'), 'Digit8': ord('8'), 'Digit9': ord('9'),
        'Digit0': ord('0'),
        
        # 字母键（通过code映射）
        'KeyA': ord('A'), 'KeyB': ord('B'), 'KeyC': ord('C'), 'KeyD': ord('D'),
        'KeyE': ord('E'), 'KeyF': ord('F'), 'KeyG': ord('G'), 'KeyH': ord('H'),
        'KeyI': ord('I'), 'KeyJ': ord('J'), 'KeyK': ord('K'), 'KeyL': ord('L'),
        'KeyM': ord('M'), 'KeyN': ord('N'), 'KeyO': ord('O'), 'KeyP': ord('P'),
        'KeyQ': ord('Q'), 'KeyR': ord('R'), 'KeyS': ord('S'), 'KeyT': ord('T'),
        'KeyU': ord('U'), 'KeyV': ord('V'), 'KeyW': ord('W'), 'KeyX': ord('X'),
        'KeyY': ord('Y'), 'KeyZ': ord('Z'),
    }
    
    return key_map.get(key)


def _get_modifier_key_code(modifier: str) -> Optional[int]:
    """获取修饰键的虚拟键码"""
    modifier_map = {
        'ctrl': win32con.VK_CONTROL,
        'control': win32con.VK_CONTROL,
        'alt': win32con.VK_MENU,
        'shift': win32con.VK_SHIFT,
        'win': win32con.VK_LWIN,
        'windows': win32con.VK_LWIN,
        'meta': win32con.VK_LWIN,
    }
    return modifier_map.get(modifier.lower())


def _send_text_via_clipboard(text: str) -> bool:
    # 方案：优先使用 pyperclip；失败则回退到 Win32 剪贴板 API（win32clipboard 或 ctypes）
    # 1) pyperclip
    try:
        import pyperclip  # type: ignore
        try:
            pyperclip.copy(text)
            if win32api is None or win32con is None:
                return False
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception:
            pass
    except Exception:
        pass

    # 2) win32clipboard（若可用）
    try:
        if win32clipboard is not None and win32con is not None and win32api is not None:
            try:
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                finally:
                    win32clipboard.CloseClipboard()
            except Exception:
                # 保底关闭，避免剪贴板占用
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            # 发送 Ctrl+V
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
    except Exception:
        pass

    # 3) ctypes 直接调用 Win32 剪贴板
    try:
        import ctypes
        if win32api is None or win32con is None:
            return False
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        if user32.OpenClipboard(0) == 0:
            return False
        try:
            user32.EmptyClipboard()
            data = (text or "").encode("utf-16-le") + b"\x00\x00"
            h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h_global:
                return False
            p_data = kernel32.GlobalLock(h_global)
            if not p_data:
                kernel32.GlobalFree(h_global)
                return False
            ctypes.memmove(p_data, data, len(data))
            kernel32.GlobalUnlock(h_global)
            if user32.SetClipboardData(CF_UNICODETEXT, h_global) == 0:
                kernel32.GlobalFree(h_global)
                return False
        finally:
            user32.CloseClipboard()
        # 发送 Ctrl+V
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False


@app.route("/api/input/keyboard_text", methods=["POST"])
def api_keyboard_text():
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_KEYBOARD_PW_FILE)
    if required and (not is_keyboard_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    # 普通用户仅允许在 MATLAB/Simulink 进行键盘输入
    try:
        if session.get("role") == "user":
            res = _find_window_hwnd("auto")
            if not res:
                return jsonify({"error": "matlab_not_running"}), 403
            hwnd, _ = res
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
    except Exception:
        pass
    text = str(data.get("text") or "")
    if not text:
        return jsonify({"error": "empty_text"}), 400
    ok = _send_text_via_clipboard(text)
    if ok:
        return jsonify({"ok": True})
    return jsonify({"error": "send_failed_install_pyperclip"}), 500


@app.route("/api/input/keyboard_key", methods=["POST"])
def api_keyboard_key():
    """发送单个键盘按键"""
    if os.name != "nt" or win32api is None or win32con is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_KEYBOARD_PW_FILE)
    if required and (not is_keyboard_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    # 管理员用户无需窗口限制，普通用户仅允许在MATLAB/Simulink窗口操作
    try:
        if session.get("role") == "user":
            res = _find_window_hwnd("auto")
            if not res:
                return jsonify({"error": "matlab_not_running"}), 403
            hwnd, _ = res
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
    except Exception:
        pass
    
    key = data.get("key", "").strip()
    action = data.get("action", "press")  # press, down, up
    modifiers = data.get("modifiers", [])  # ctrl, alt, shift, win
    
    if not key:
        return jsonify({"error": "empty_key"}), 400
    
    try:
        # 获取虚拟键码
        vk_code = _get_virtual_key_code(key)
        if vk_code is None:
            return jsonify({"error": f"unsupported_key: {key}"}), 400
        
        # 处理修饰键
        modifier_codes = []
        for mod in modifiers:
            mod_code = _get_modifier_key_code(mod)
            if mod_code:
                modifier_codes.append(mod_code)
        
        # 按下修饰键
        for mod_code in modifier_codes:
            win32api.keybd_event(mod_code, 0, 0, 0)
            time.sleep(0.01)  # 短暂延迟确保修饰键先按下
        
        # 执行主键操作
        if action == "down":
            win32api.keybd_event(vk_code, 0, 0, 0)
        elif action == "up":
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:  # press (默认)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        # 释放修饰键
        for mod_code in reversed(modifier_codes):  # 反向释放
            win32api.keybd_event(mod_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
        
        return jsonify({"ok": True, "key": key, "action": action, "modifiers": modifiers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/keyboard_sequence", methods=["POST"])
def api_keyboard_sequence():
    """发送键盘按键序列"""
    if os.name != "nt" or win32api is None or win32con is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_KEYBOARD_PW_FILE)
    if required and (not is_keyboard_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    # 管理员用户无需窗口限制，普通用户仅允许在MATLAB/Simulink窗口操作
    try:
        if session.get("role") == "user":
            res = _find_window_hwnd("auto")
            if not res:
                return jsonify({"error": "matlab_not_running"}), 403
            hwnd, _ = res
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
    except Exception:
        pass
    
    sequence = data.get("sequence", [])
    if not sequence:
        return jsonify({"error": "empty_sequence"}), 400
    
    try:
        for key_info in sequence:
            key = key_info.get("key", "")
            action = key_info.get("action", "press")
            modifiers = key_info.get("modifiers", [])
            delay = key_info.get("delay", 0.05)  # 按键间延迟
            
            if not key:
                continue
            
            # 获取虚拟键码
            vk_code = _get_virtual_key_code(key)
            if vk_code is None:
                continue
            
            # 处理修饰键
            modifier_codes = []
            for mod in modifiers:
                mod_code = _get_modifier_key_code(mod)
                if mod_code:
                    modifier_codes.append(mod_code)
            
            # 按下修饰键
            for mod_code in modifier_codes:
                win32api.keybd_event(mod_code, 0, 0, 0)
                time.sleep(0.01)
            
            # 执行主键操作
            if action == "down":
                win32api.keybd_event(vk_code, 0, 0, 0)
            elif action == "up":
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:  # press
                win32api.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 释放修饰键
            for mod_code in reversed(modifier_codes):
                win32api.keybd_event(mod_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.01)
            
            # 按键间延迟
            if delay > 0:
                time.sleep(delay)
        
        return jsonify({"ok": True, "sequence_length": len(sequence)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- 焦点控制与诊断（已移除本轮新增端点，恢复到上次对话前状态） ----------------

@app.route("/api/input/mouse_click_screen", methods=["POST"])
def api_mouse_click_screen():
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    # 支持归一化坐标 [0,1] 或像素坐标
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    button = (data.get("button") or "left").strip().lower()
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        # 普通用户仅允许点击 MATLAB/Simulink 窗口区域内
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        win32api.SetCursorPos((x, y))
        if button == 'right':
            win32api.mouse_event(0x0008, 0, 0, 0, 0)
            win32api.mouse_event(0x0010, 0, 0, 0, 0)
        elif button == 'middle':
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
        else:
            win32api.mouse_event(0x0002, 0, 0, 0, 0)
            win32api.mouse_event(0x0004, 0, 0, 0, 0)
        return jsonify({"ok": True, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_press", methods=["POST"])
def api_mouse_press():
    """按下鼠标按钮（不释放）"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    button = (data.get("button") or "left").strip().lower()
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        
        win32api.SetCursorPos((x, y))
        if button == 'right':
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
        elif button == 'middle':
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
        else:
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        return jsonify({"ok": True, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_release", methods=["POST"])
def api_mouse_release():
    """释放鼠标按钮"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    button = (data.get("button") or "left").strip().lower()
    try:
        if button == 'right':
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
        elif button == 'middle':
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
        else:
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_drag", methods=["POST"])
def api_mouse_drag():
    """拖拽操作：从起点拖拽到终点"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    # 起点和终点坐标
    start_x_norm = data.get("start_x_norm")
    start_y_norm = data.get("start_y_norm")
    end_x_norm = data.get("end_x_norm")
    end_y_norm = data.get("end_y_norm")
    button = (data.get("button") or "left").strip().lower()
    duration = float(data.get("duration", 0.5))  # 拖拽持续时间（秒）
    
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        
        if start_x_norm is not None and start_y_norm is not None:
            start_x = int(max(0, min(1, float(start_x_norm))) * screen_w)
            start_y = int(max(0, min(1, float(start_y_norm))) * screen_h)
        else:
            start_x = int(data.get("start_x", 0))
            start_y = int(data.get("start_y", 0))
            
        if end_x_norm is not None and end_y_norm is not None:
            end_x = int(max(0, min(1, float(end_x_norm))) * screen_w)
            end_y = int(max(0, min(1, float(end_y_norm))) * screen_h)
        else:
            end_x = int(data.get("end_x", 0))
            end_y = int(data.get("end_y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= start_x <= right and top <= start_y <= bottom):
                    return jsonify({"error": "start_outside_matlab_window"}), 403
                if not (left <= end_x <= right and top <= end_y <= bottom):
                    return jsonify({"error": "end_outside_matlab_window"}), 403
        except Exception:
            pass
        
        # 移动到起点
        win32api.SetCursorPos((start_x, start_y))
        
        # 按下鼠标按钮
        if button == 'right':
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
        elif button == 'middle':
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
        else:
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        
        # 平滑拖拽到终点 - 使用贝塞尔曲线和更高帧率
        steps = max(20, int(duration * 120))  # 120fps for smoother movement
        
        # 使用缓动函数实现更自然的拖拽效果
        def ease_in_out_cubic(t):
            """三次缓动函数，开始和结束时较慢，中间较快"""
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 3) / 2
        
        for i in range(steps + 1):
            linear_progress = i / steps
            # 应用缓动函数
            eased_progress = ease_in_out_cubic(linear_progress)
            
            # 计算当前位置
            current_x = int(start_x + (end_x - start_x) * eased_progress)
            current_y = int(start_y + (end_y - start_y) * eased_progress)
            
            # 移动到新位置
            win32api.SetCursorPos((current_x, current_y))
            
            # 动态调整延迟时间，开始和结束时稍慢
            if i < steps * 0.1 or i > steps * 0.9:
                # 开始和结束阶段稍慢
                time.sleep(duration / steps * 1.2)
            else:
                # 中间阶段正常速度
                time.sleep(duration / steps)
        
        # 释放鼠标按钮
        if button == 'right':
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
        elif button == 'middle':
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
        else:
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            
        return jsonify({"ok": True, "start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_double_click", methods=["POST"])
def api_mouse_double_click():
    """双击操作"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    button = (data.get("button") or "left").strip().lower()
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        
        win32api.SetCursorPos((x, y))
        
        # 执行双击
        if button == 'right':
            # 右键双击
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
            time.sleep(0.05)  # 短暂延迟
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
        elif button == 'middle':
            # 中键双击
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
            time.sleep(0.05)  # 短暂延迟
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
        else:
            # 左键双击
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            time.sleep(0.05)  # 短暂延迟
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            
        return jsonify({"ok": True, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 全局异步操作状态管理
_async_operations = {}
_operation_lock = threading.Lock()


@app.route("/api/input/mouse_async_press", methods=["POST"])
def api_mouse_async_press():
    """异步按下鼠标按钮（支持长时间按住）"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    button = (data.get("button") or "left").strip().lower()
    operation_id = data.get("operation_id", f"press_{int(time.time() * 1000)}")
    
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        
        # 移动到指定位置
        win32api.SetCursorPos((x, y))
        
        # 按下鼠标按钮
        if button == 'right':
            win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
        elif button == 'middle':
            win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
        else:
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        
        # 记录操作状态
        with _operation_lock:
            _async_operations[operation_id] = {
                "type": "press",
                "button": button,
                "x": x,
                "y": y,
                "start_time": time.time(),
                "active": True
            }
        
        return jsonify({"ok": True, "operation_id": operation_id, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_async_release", methods=["POST"])
def api_mouse_async_release():
    """异步释放鼠标按钮"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    operation_id = data.get("operation_id")
    button = (data.get("button") or "left").strip().lower()
    
    try:
        # 释放鼠标按钮
        if button == 'right':
            win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
        elif button == 'middle':
            win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
        else:
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        
        # 更新操作状态
        if operation_id:
            with _operation_lock:
                if operation_id in _async_operations:
                    _async_operations[operation_id]["active"] = False
                    _async_operations[operation_id]["end_time"] = time.time()
        
        return jsonify({"ok": True, "operation_id": operation_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_async_move", methods=["POST"])
def api_mouse_async_move():
    """异步移动鼠标（在按住状态下）"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    operation_id = data.get("operation_id")
    
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        
        # 移动鼠标
        win32api.SetCursorPos((x, y))
        
        # 更新操作状态
        if operation_id:
            with _operation_lock:
                if operation_id in _async_operations:
                    _async_operations[operation_id]["x"] = x
                    _async_operations[operation_id]["y"] = y
                    _async_operations[operation_id]["last_move"] = time.time()
        
        return jsonify({"ok": True, "operation_id": operation_id, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_move_async", methods=["POST"])
def api_mouse_move_async():
    """异步鼠标移动（用于实时拖拽）"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    x_norm = data.get("x_norm")
    y_norm = data.get("y_norm")
    operation_id = data.get("operation_id")
    
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        
        if x_norm is not None and y_norm is not None:
            x = int(max(0, min(1, float(x_norm))) * screen_w)
            y = int(max(0, min(1, float(y_norm))) * screen_h)
        else:
            x = int(data.get("x", 0))
            y = int(data.get("y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= x <= right and top <= y <= bottom):
                    return jsonify({"error": "outside_matlab_window"}), 403
        except Exception:
            pass
        
        # 移动鼠标到新位置
        win32api.SetCursorPos((x, y))
        
        # 更新操作状态
        if operation_id:
            with _operation_lock:
                if operation_id in _async_operations:
                    _async_operations[operation_id]["x"] = x
                    _async_operations[operation_id]["y"] = y
                    _async_operations[operation_id]["last_move"] = time.time()
        
        return jsonify({"ok": True, "operation_id": operation_id, "x": x, "y": y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/mouse_async_drag", methods=["POST"])
def api_mouse_async_drag():
    """异步拖拽操作（支持长时间拖拽和同步操作）"""
    if os.name != "nt" or win32api is None:
        return jsonify({"error": "windows_only"}), 400
    
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if required and (not is_mouse_authed()) and provided != required:
        return jsonify({"error": "unauthorized"}), 403
    
    # 起点和终点坐标
    start_x_norm = data.get("start_x_norm")
    start_y_norm = data.get("start_y_norm")
    end_x_norm = data.get("end_x_norm")
    end_y_norm = data.get("end_y_norm")
    button = (data.get("button") or "left").strip().lower()
    operation_id = data.get("operation_id", f"drag_{int(time.time() * 1000)}")
    duration = float(data.get("duration", 0.5))  # 拖拽持续时间（秒）
    async_mode = data.get("async", False)  # 是否异步模式
    
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        
        if start_x_norm is not None and start_y_norm is not None:
            start_x = int(max(0, min(1, float(start_x_norm))) * screen_w)
            start_y = int(max(0, min(1, float(start_y_norm))) * screen_h)
        else:
            start_x = int(data.get("start_x", 0))
            start_y = int(data.get("start_y", 0))
            
        if end_x_norm is not None and end_y_norm is not None:
            end_x = int(max(0, min(1, float(end_x_norm))) * screen_w)
            end_y = int(max(0, min(1, float(end_y_norm))) * screen_h)
        else:
            end_x = int(data.get("end_x", 0))
            end_y = int(data.get("end_y", 0))
        
        # 普通用户仅允许在 MATLAB/Simulink 窗口区域内操作
        try:
            if session.get("role") == "user":
                res = _find_window_hwnd("auto")
                if not res:
                    return jsonify({"error": "matlab_not_running"}), 403
                _, rect = res
                left, top, right, bottom = rect
                if not (left <= start_x <= right and top <= start_y <= bottom):
                    return jsonify({"error": "start_outside_matlab_window"}), 403
                if not (left <= end_x <= right and top <= end_y <= bottom):
                    return jsonify({"error": "end_outside_matlab_window"}), 403
        except Exception:
            pass
        
        if async_mode:
            # 异步模式：立即返回，在后台执行拖拽
            def async_drag():
                try:
                    # 移动到起点
                    win32api.SetCursorPos((start_x, start_y))
                    
                    # 按下鼠标按钮
                    if button == 'right':
                        win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
                    elif button == 'middle':
                        win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
                    else:
                        win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
                    
                    # 记录操作状态
                    with _operation_lock:
                        _async_operations[operation_id] = {
                            "type": "drag",
                            "button": button,
                            "start_x": start_x,
                            "start_y": start_y,
                            "end_x": end_x,
                            "end_y": end_y,
                            "current_x": start_x,
                            "current_y": start_y,
                            "start_time": time.time(),
                            "active": True
                        }
                    
                    # 平滑拖拽到终点 - 使用优化的缓动算法
                    steps = max(20, int(duration * 120))  # 120fps for smoother movement
                    
                    # 使用缓动函数实现更自然的拖拽效果
                    def ease_in_out_cubic(t):
                        """三次缓动函数，开始和结束时较慢，中间较快"""
                        if t < 0.5:
                            return 4 * t * t * t
                        else:
                            return 1 - pow(-2 * t + 2, 3) / 2
                    
                    for i in range(steps + 1):
                        linear_progress = i / steps
                        # 应用缓动函数
                        eased_progress = ease_in_out_cubic(linear_progress)
                        
                        # 计算当前位置
                        current_x = int(start_x + (end_x - start_x) * eased_progress)
                        current_y = int(start_y + (end_y - start_y) * eased_progress)
                        win32api.SetCursorPos((current_x, current_y))
                        
                        # 更新操作状态
                        with _operation_lock:
                            if operation_id in _async_operations:
                                _async_operations[operation_id]["current_x"] = current_x
                                _async_operations[operation_id]["current_y"] = current_y
                        
                        # 动态调整延迟时间，开始和结束时稍慢
                        if i < steps * 0.1 or i > steps * 0.9:
                            # 开始和结束阶段稍慢
                            time.sleep(duration / steps * 1.2)
                        else:
                            # 中间阶段正常速度
                            time.sleep(duration / steps)
                    
                    # 释放鼠标按钮
                    if button == 'right':
                        win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
                    elif button == 'middle':
                        win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
                    else:
                        win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                    
                    # 完成操作
                    with _operation_lock:
                        if operation_id in _async_operations:
                            _async_operations[operation_id]["active"] = False
                            _async_operations[operation_id]["end_time"] = time.time()
                            
                except Exception as e:
                    # 清理操作状态
                    with _operation_lock:
                        if operation_id in _async_operations:
                            _async_operations[operation_id]["active"] = False
                            _async_operations[operation_id]["error"] = str(e)
            
            # 启动异步拖拽
            import threading
            thread = threading.Thread(target=async_drag, daemon=True)
            thread.start()
            
            return jsonify({"ok": True, "operation_id": operation_id, "async": True})
        else:
            # 同步模式：原有逻辑
            # 移动到起点
            win32api.SetCursorPos((start_x, start_y))
            
            # 按下鼠标按钮
            if button == 'right':
                win32api.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
            elif button == 'middle':
                win32api.mouse_event(0x0020, 0, 0, 0, 0)  # MIDDLEDOWN
            else:
                win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            
            # 平滑拖拽到终点
            steps = max(10, int(duration * 60))  # 60fps
            for i in range(steps + 1):
                progress = i / steps
                current_x = int(start_x + (end_x - start_x) * progress)
                current_y = int(start_y + (end_y - start_y) * progress)
                win32api.SetCursorPos((current_x, current_y))
                time.sleep(duration / steps)
            
            # 释放鼠标按钮
            if button == 'right':
                win32api.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
            elif button == 'middle':
                win32api.mouse_event(0x0040, 0, 0, 0, 0)  # MIDDLEUP
            else:
                win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                
            return jsonify({"ok": True, "start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/input/auth_mouse", methods=["POST"])
def api_auth_mouse():
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_MOUSE_PW_FILE)
    if not required:
        set_session_data("mouse_authed", True)
        return jsonify({"ok": True, "note": "no_password_required"})
    if provided == required:
        set_session_data("mouse_authed", True)
        return jsonify({"ok": True})
    return jsonify({"error": "unauthorized"}), 403


@app.route("/api/input/auth_keyboard", methods=["POST"])
def api_auth_keyboard():
    data = request.json or {}
    provided = (data.get("password") or "").strip()
    required = _read_password(REMOTE_KEYBOARD_PW_FILE)
    if not required:
        set_session_data("keyboard_authed", True)
        return jsonify({"ok": True, "note": "no_password_required"})
    if provided == required:
        set_session_data("keyboard_authed", True)
        return jsonify({"ok": True})
    return jsonify({"error": "unauthorized"}), 403

@app.route("/api/custom_params", methods=["POST"])
def api_custom_params():
    try:
        data = request.get_json(force=True, silent=True) or {}
        required_keys = ["f", "L", "C", "Ron", "RL", "RC"]
        for k in required_keys:
            if k not in data:
                return jsonify({"status": "error", "error": f"缺少参数: {k}"}), 400
        try:
            f = float(data.get("f"))
            L = float(data.get("L"))
            C = float(data.get("C"))
            Ron = float(data.get("Ron"))
            RL = float(data.get("RL"))
            RC = float(data.get("RC"))
        except Exception:
            return jsonify({"status": "error", "error": "参数必须为数值"}), 400

        # 计算 Visualization 目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        viz_dir = os.path.join(root, "Visualization")
        os.makedirs(viz_dir, exist_ok=True)
        csv_path = os.path.join(viz_dir, "self_defined_para.csv")

        # 写入与参考文件一致的表头与键名/单位
        rows = [
            ("parameter", "value"),
            ("f(Hz)", f),
            ("L(H)", L),
            ("C(F)", C),
            ("Ron", Ron),
            ("RL", RL),
            ("RC", RC),
        ]
        with open(csv_path, "w", newline='', encoding="utf-8") as fp:
            writer = csv.writer(fp)
            for r in rows:
                writer.writerow(r)

        return jsonify({"status": "success", "path": csv_path})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/eda/custom_design", methods=["POST"])
def api_eda_custom_design():
    try:
        data = request.get_json(force=True, silent=True) or {}
        # 基本校验：拓扑、Vin、Vout
        topology = (data.get("topology") or "").strip()
        if not topology:
            return jsonify({"status": "error", "error": "缺少参数: topology"}), 400
        try:
            Vin = float(data.get("Vin"))
            Vout = float(data.get("Vout"))
        except Exception:
            return jsonify({"status": "error", "error": "Vin/Vout 必须为数值"}), 400

        # 可选项，允许为空
        def _to_float(name):
            try:
                v = data.get(name)
                if v is None or v == "":
                    return ""
                return float(v)
            except Exception:
                return ""

        def _to_int(name):
            try:
                v = data.get(name)
                if v is None or v == "":
                    return ""
                return int(v)
            except Exception:
                return ""

        Iout = _to_float("Iout")
        f = _to_float("f")
        ripple_v = _to_float("ripple_v")
        ripple_i = _to_float("ripple_i")
        layers = _to_int("layers")
        copper_oz = _to_float("copper_oz")
        clearance = _to_float("clearance")
        creepage = _to_float("creepage")
        temp_ambient = _to_float("temp_ambient")
        efficiency = _to_float("efficiency")
        notes = (data.get("notes") or "").strip()

        # 目标CSV路径
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        viz_dir = os.path.join(root, "Visualization")
        os.makedirs(viz_dir, exist_ok=True)
        csv_path = os.path.join(viz_dir, "eda_custom_design.csv")

        # 写入CSV，首行表头 + key与单位，尽量贴近 self_defined_para.csv 的风格
        rows = [
            ("parameter", "value"),
            ("topology", topology),
            ("Vin(V)", Vin),
            ("Vout(V)", Vout),
            ("Iout(A)", Iout),
            ("f(Hz)", f),
            ("Vripple(%)", ripple_v),
            ("Iripple(%)", ripple_i),
            ("PCB_layers", layers),
            ("Copper(oz)", copper_oz),
            ("Clearance(mm)", clearance),
            ("Creepage(mm)", creepage),
            ("AmbientTemp(C)", temp_ambient),
            ("EfficiencyTarget(%)", efficiency),
            ("Notes", notes),
        ]

        with open(csv_path, "w", newline='', encoding="utf-8") as fp:
            writer = csv.writer(fp)
            for r in rows:
                writer.writerow(r)

        # 生成设计需求文字描述
        requirement_text = f"""原理图设计需求说明

====================================
基本参数
====================================
拓扑类型：{topology}
输入电压：{Vin}V
输出电压：{Vout}V"""

        if Iout:
            requirement_text += f"\n输出电流：{Iout}A"
        
        if f:
            if f >= 1000000:
                requirement_text += f"\n开关频率：{f}Hz ({f/1000000:.1f}MHz)"
            elif f >= 1000:
                requirement_text += f"\n开关频率：{f}Hz ({f/1000:.1f}kHz)"
            else:
                requirement_text += f"\n开关频率：{f}Hz"

        requirement_text += "\n\n====================================\n性能要求\n===================================="
        
        if ripple_v:
            requirement_text += f"\n输出电压纹波：{ripple_v}%"
        if ripple_i:
            requirement_text += f"\n输出电流纹波：{ripple_i}%"
        if efficiency:
            requirement_text += f"\n效率目标：{efficiency}%"

        requirement_text += "\n\n====================================\nPCB设计要求\n===================================="
        
        if layers:
            requirement_text += f"\nPCB层数：{layers}层"
        if copper_oz:
            requirement_text += f"\n铜厚：{copper_oz}oz"
        if clearance:
            requirement_text += f"\n最小电气间隙：{clearance}mm"
        if creepage:
            requirement_text += f"\n最小爬电距离：{creepage}mm"
        if temp_ambient:
            requirement_text += f"\n环境温度：{temp_ambient}°C"

        if notes:
            requirement_text += f"\n\n====================================\n其他注意事项\n====================================\n{notes}"

        # 保存到txt文件
        txt_path = os.path.join(viz_dir, "schematic_design_requirement.txt")
        with open(txt_path, "w", encoding="utf-8") as fp:
            fp.write(requirement_text)

        return jsonify({
            "status": "success", 
            "path": csv_path,
            "txt_path": txt_path,
            "requirement_text": requirement_text
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/eda/test_click", methods=["POST"])
def api_eda_test_click():
    """测试KiCad窗口的点击位置（仅移动鼠标，不点击）
    
    POST参数：
    - offset_x: 距离右边缘的像素，默认18
    - offset_y: 距离顶部的像素，默认55
    - click: 是否实际点击（默认false，仅移动鼠标）
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        offset_x = int(data.get('offset_x', 18))
        offset_y = int(data.get('offset_y', 55))
        do_click = data.get('click', False)
        
        if not (win32gui and win32api):
            return jsonify({"status": "error", "error": "Windows API不可用"}), 400
        
        # 查找KiCad窗口
        def find_kicad_window():
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if ('PCB Editor' in title or 'pcbnew' in title.lower() or 
                        'Two_Phase_Buck' in title or '.kicad_pcb' in title):
                        hwnds.append((hwnd, title))
                return True
            
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            return hwnds[0] if hwnds else None
        
        result = find_kicad_window()
        if not result:
            return jsonify({"status": "error", "error": "未找到KiCad PCB编辑器窗口"}), 404
        
        kicad_hwnd, window_title = result
        rect = win32gui.GetWindowRect(kicad_hwnd)
        left, top, right, bottom = rect
        
        # 尝试激活窗口（如果需要点击）
        activation_success = False
        if do_click:
            print("尝试激活窗口...")
            try:
                # 模拟Alt键释放
                win32api.keybd_event(0x12, 0, 0x0002, 0)
                time.sleep(0.05)
                
                # 使用AttachThreadInput
                current_thread = win32api.GetCurrentThreadId()
                target_thread, _ = win32process.GetWindowThreadProcessId(kicad_hwnd)
                if current_thread != target_thread:
                    win32process.AttachThreadInput(current_thread, target_thread, True)
                    win32gui.BringWindowToTop(kicad_hwnd)
                    win32gui.SetForegroundWindow(kicad_hwnd)
                    win32process.AttachThreadInput(current_thread, target_thread, False)
                else:
                    win32gui.SetForegroundWindow(kicad_hwnd)
                
                time.sleep(0.3)
                activation_success = True
            except Exception as e:
                print(f"激活窗口失败: {e}")
        
        # 计算点击位置
        target_x = right - offset_x
        target_y = top + offset_y
        
        # 移动鼠标
        win32api.SetCursorPos((target_x, target_y))
        
        # 如果需要，执行点击
        if do_click:
            time.sleep(0.3)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        return jsonify({
            "status": "success",
            "message": "鼠标已移动到目标位置" + ("并点击" if do_click else ""),
            "window_title": window_title,
            "window_rect": {"left": left, "top": top, "right": right, "bottom": bottom},
            "window_size": {"width": right - left, "height": bottom - top},
            "target_position": {"x": target_x, "y": target_y},
            "offsets": {"offset_x": offset_x, "offset_y": offset_y},
            "tip": "检查鼠标是否在正确的按钮上。如果不正确，调整offset_x和offset_y参数"
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route("/api/eda/open_design", methods=["POST"])
def api_eda_open_design():
    """打开KiCad原理图和PCB设计文件，并自动排列窗口
    
    功能：自动打开双相交错并联Buck的原理图(.kicad_sch)和PCB(.kicad_pcb)文件
    """
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'kicad.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Two_Phase_Buck")
        
        # 文件路径
        schematic_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_sch")
        pcb_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_pcb")
        
        # 检查文件是否存在
        if not os.path.exists(schematic_path):
            return jsonify({
                "status": "error", 
                "error": f"原理图文件不存在: {schematic_path}"
            }), 400
            
        if not os.path.exists(pcb_path):
            return jsonify({
                "status": "error", 
                "error": f"PCB文件不存在: {pcb_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 打开原理图编辑器（左侧）
        eeschema_path = os.path.join(kicad_install_dir, 'bin', 'eeschema.exe')
        schematic_proc = None
        schematic_opened = False
        schematic_hwnd = None
        
        if os.path.exists(eeschema_path):
            try:
                schematic_proc = subprocess.Popen(
                    [eeschema_path, schematic_path],
                    shell=False,
                    env=env,
                    cwd=project_dir
                )
                schematic_opened = True
                time.sleep(2.5)  # 等待原理图编辑器完全加载
                
                # 查找并排列原理图窗口
                if win32gui:
                    try:
                        def find_schematic_window():
                            def callback(hwnd, hwnds):
                                if win32gui.IsWindowVisible(hwnd):
                                    title = win32gui.GetWindowText(hwnd)
                                    if ('Schematic Editor' in title or 'eeschema' in title.lower() or 
                                        'Two_Phase_Buck' in title):
                                        hwnds.append(hwnd)
                                return True
                            hwnds = []
                            win32gui.EnumWindows(callback, hwnds)
                            return hwnds[0] if hwnds else None
                        
                        # 多次尝试查找窗口
                        for attempt in range(15):
                            schematic_hwnd = find_schematic_window()
                            if schematic_hwnd:
                                break
                            time.sleep(0.5)
                        
                        if schematic_hwnd:
                            print(f"找到原理图窗口: {win32gui.GetWindowText(schematic_hwnd)}")
                            
                            try:
                                # 步骤1: 如果窗口最小化，先恢复
                                if win32gui.IsIconic(schematic_hwnd):
                                    print("  窗口已最小化，正在恢复...")
                                    win32gui.ShowWindow(schematic_hwnd, win32con.SW_RESTORE)
                                    time.sleep(0.3)
                                
                                # 步骤2: 确保窗口可见
                                print("  正在显示窗口...")
                                win32gui.ShowWindow(schematic_hwnd, win32con.SW_SHOW)
                                time.sleep(0.2)
                                
                                # 步骤3: 将窗口置顶
                                print("  正在置顶窗口...")
                                win32gui.BringWindowToTop(schematic_hwnd)
                                time.sleep(0.2)
                                
                                # 步骤4: 使用SetWindowPos强制显示并最大化
                                print("  正在最大化窗口...")
                                screen_width = win32api.GetSystemMetrics(0)
                                screen_height = win32api.GetSystemMetrics(1)
                                
                                win32gui.SetWindowPos(
                                    schematic_hwnd,
                                    win32con.HWND_TOPMOST,  # 临时置顶
                                    0, 0,
                                    screen_width, screen_height,
                                    win32con.SWP_SHOWWINDOW
                                )
                                time.sleep(0.3)
                                
                                # 步骤5: 取消置顶状态（恢复正常）
                                win32gui.SetWindowPos(
                                    schematic_hwnd,
                                    win32con.HWND_NOTOPMOST,
                                    0, 0,
                                    screen_width, screen_height,
                                    win32con.SWP_SHOWWINDOW
                                )
                                time.sleep(0.2)
                                
                                # 步骤6: 最后使用ShowWindow最大化
                                win32gui.ShowWindow(schematic_hwnd, win32con.SW_MAXIMIZE)
                                
                                print(f"✓ 原理图窗口已最大化显示 ({screen_width}x{screen_height})")
                            except Exception as e:
                                print(f"最大化原理图窗口失败: {e}")
                                import traceback
                                print(traceback.format_exc())
                        else:
                            print("⚠ 未找到原理图窗口")
                    except Exception as e:
                        print(f"排列原理图窗口失败: {e}")
                        
            except Exception as e:
                print(f"打开原理图失败: {e}")
        
        # 打开PCB编辑器（全屏显示）
        pcbnew_path = os.path.join(kicad_install_dir, 'bin', 'pcbnew.exe')
        pcb_proc = None
        pcb_opened = False
        pcb_hwnd = None
        
        if os.path.exists(pcbnew_path):
            try:
                pcb_proc = subprocess.Popen(
                    [pcbnew_path, pcb_path],
                    shell=False,
                    env=env,
                    cwd=project_dir
                )
                pcb_opened = True
                time.sleep(3.5)  # 等待PCB编辑器完全加载（增加等待时间）
                
                # 查找并排列PCB窗口
                if win32gui:
                    try:
                        def find_pcb_window():
                            def callback(hwnd, hwnds):
                                if win32gui.IsWindowVisible(hwnd):
                                    title = win32gui.GetWindowText(hwnd)
                                    # 扩大匹配范围
                                    if ('PCB' in title or 'pcbnew' in title.lower() or 
                                        'Two_Phase_Buck' in title or 'kicad_pcb' in title.lower()):
                                        hwnds.append(hwnd)
                                return True
                            hwnds = []
                            win32gui.EnumWindows(callback, hwnds)
                            return hwnds[0] if hwnds else None
                        
                        # 多次尝试查找窗口
                        print("正在查找PCB窗口...")
                        for attempt in range(15):
                            pcb_hwnd = find_pcb_window()
                            if pcb_hwnd:
                                break
                            if attempt % 3 == 0:
                                print(f"  尝试 {attempt + 1}/15...")
                            time.sleep(0.5)
                        
                        if pcb_hwnd:
                            print(f"找到PCB窗口: {win32gui.GetWindowText(pcb_hwnd)}")
                            
                            try:
                                # 步骤1: 如果窗口最小化，先恢复
                                if win32gui.IsIconic(pcb_hwnd):
                                    print("  窗口已最小化，正在恢复...")
                                    win32gui.ShowWindow(pcb_hwnd, win32con.SW_RESTORE)
                                    time.sleep(0.3)
                                
                                # 步骤2: 确保窗口可见
                                print("  正在显示窗口...")
                                win32gui.ShowWindow(pcb_hwnd, win32con.SW_SHOW)
                                time.sleep(0.2)
                                
                                # 步骤3: 将窗口置顶
                                print("  正在置顶窗口...")
                                win32gui.BringWindowToTop(pcb_hwnd)
                                time.sleep(0.2)
                                
                                # 步骤4: 使用SetWindowPos强制显示并最大化
                                print("  正在最大化窗口...")
                                screen_width = win32api.GetSystemMetrics(0)
                                screen_height = win32api.GetSystemMetrics(1)
                                
                                win32gui.SetWindowPos(
                                    pcb_hwnd,
                                    win32con.HWND_TOPMOST,  # 临时置顶
                                    0, 0,
                                    screen_width, screen_height,
                                    win32con.SWP_SHOWWINDOW
                                )
                                time.sleep(0.3)
                                
                                # 步骤5: 取消置顶状态（恢复正常）
                                win32gui.SetWindowPos(
                                    pcb_hwnd,
                                    win32con.HWND_NOTOPMOST,
                                    0, 0,
                                    screen_width, screen_height,
                                    win32con.SWP_SHOWWINDOW
                                )
                                time.sleep(0.2)
                                
                                # 步骤6: 最后使用ShowWindow最大化
                                win32gui.ShowWindow(pcb_hwnd, win32con.SW_MAXIMIZE)
                                
                                print(f"✓ PCB窗口已最大化显示 ({screen_width}x{screen_height})")
                            except Exception as e:
                                print(f"最大化PCB窗口失败: {e}")
                                import traceback
                                print(traceback.format_exc())
                        else:
                            print("⚠ 未找到PCB窗口")
                            print("   提示：PCB编辑器可能需要更长时间加载")
                    except Exception as e:
                        print(f"排列PCB窗口失败: {e}")
                        
            except Exception as e:
                print(f"打开PCB失败: {e}")
        
        # 返回结果
        if schematic_opened or pcb_opened:
            return jsonify({
                "status": "success",
                "message": "KiCad设计文件已打开（全屏显示）",
                "schematic_opened": schematic_opened,
                "schematic_path": schematic_path if schematic_opened else None,
                "schematic_pid": schematic_proc.pid if schematic_proc else None,
                "schematic_maximized": (schematic_hwnd is not None),
                "pcb_opened": pcb_opened,
                "pcb_path": pcb_path if pcb_opened else None,
                "pcb_pid": pcb_proc.pid if pcb_proc else None,
                "pcb_maximized": (pcb_hwnd is not None),
                "kicad_path": kicad_install_dir,
                "windows_arranged": True
            })
        else:
            return jsonify({
                "status": "error",
                "error": "无法打开KiCad编辑器，请检查KiCad安装"
            }), 500
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# 已禁用：逐步展示动画功能（如需要可以重新启用）
"""
@app.route("/api/eda/animate_schematic", methods=["POST"])
def api_eda_animate_schematic():
    '''在原理图中逐步展示器件放置过程
    
    功能：通过创建并加载多个中间状态的原理图文件，实现器件逐步显示效果
    '''
    try:
        if not win32gui or not win32api:
            return jsonify({
                "status": "error",
                "error": "Windows自动化库未安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Two_Phase_Buck")
        schematic_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_sch")
        
        # 读取完整的原理图文件
        with open(schematic_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
        
        # 查找原理图窗口
        def find_schematic_window():
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if ('Schematic Editor' in title or 'eeschema' in title.lower() or 
                        'Two_Phase_Buck' in title):
                        hwnds.append(hwnd)
                return True
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            return hwnds[0] if hwnds else None
        
        schematic_hwnd = find_schematic_window()
        if not schematic_hwnd:
            return jsonify({
                "status": "error",
                "error": "未找到原理图窗口"
            }), 400
        
        # 解析原理图，提取所有符号（器件）定义
        import re
        
        # 提取symbol实例（已放置的器件）
        symbol_pattern = r'(\(symbol[^)]*\(lib_id[^)]+\)[^\(]*(?:\([^\)]*\))*[^\(]*\))'
        symbols_matches = list(re.finditer(symbol_pattern, full_content, re.DOTALL | re.MULTILINE))
        
        if len(symbols_matches) < 3:
            # 如果无法准确解析，使用简化的动画效果
            total_steps = 8
        else:
            total_steps = min(len(symbols_matches), 12)
        
        # 创建备份
        backup_path = schematic_path + ".backup_anim"
        import shutil
        shutil.copy2(schematic_path, backup_path)
        
        try:
            # 激活原理图窗口（使用强力激活方法）
            activation_success = False
            for retry in range(5):  # 最多重试5次
                try:
                    # 如果窗口最小化，先恢复
                    if win32gui.IsIconic(schematic_hwnd):
                        win32gui.ShowWindow(schematic_hwnd, win32con.SW_RESTORE)
                        time.sleep(0.3)
                    
                    # 方法1: 使用ShowWindow确保窗口可见
                    win32gui.ShowWindow(schematic_hwnd, win32con.SW_SHOW)
                    time.sleep(0.2)
                    
                    # 方法2: 模拟Alt键释放（绕过Windows的前台窗口限制）
                    try:
                        win32api.keybd_event(0x12, 0, 0x0002, 0)  # Alt键释放
                        time.sleep(0.05)
                    except Exception:
                        pass
                    
                    # 方法3: 使用AttachThreadInput方法
                    if win32process:
                        try:
                            current_thread = win32api.GetCurrentThreadId()
                            target_thread, _ = win32process.GetWindowThreadProcessId(schematic_hwnd)
                            
                            if current_thread != target_thread:
                                # 附加线程输入
                                win32process.AttachThreadInput(current_thread, target_thread, True)
                                time.sleep(0.1)
                                
                                # 置顶窗口
                                win32gui.BringWindowToTop(schematic_hwnd)
                                time.sleep(0.1)
                                
                                # 设置为前台窗口
                                win32gui.SetForegroundWindow(schematic_hwnd)
                                time.sleep(0.1)
                                
                                # 分离线程输入
                                win32process.AttachThreadInput(current_thread, target_thread, False)
                            else:
                                # 如果是同一线程，直接设置
                                win32gui.BringWindowToTop(schematic_hwnd)
                                win32gui.SetForegroundWindow(schematic_hwnd)
                                
                        except Exception as attach_err:
                            print(f"  AttachThreadInput失败: {attach_err}")
                            # 如果AttachThreadInput失败，尝试简单方法
                            win32gui.BringWindowToTop(schematic_hwnd)
                            time.sleep(0.1)
                            win32gui.SetForegroundWindow(schematic_hwnd)
                    else:
                        # 如果win32process不可用，使用简单方法
                        win32gui.BringWindowToTop(schematic_hwnd)
                        time.sleep(0.1)
                        win32gui.SetForegroundWindow(schematic_hwnd)
                    
                    # 方法4: 使用SetWindowPos强制置顶
                    try:
                        win32gui.SetWindowPos(
                            schematic_hwnd,
                            win32con.HWND_TOPMOST,  # 设置为最顶层
                            0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                        )
                        time.sleep(0.1)
                        # 取消最顶层状态（恢复正常）
                        win32gui.SetWindowPos(
                            schematic_hwnd,
                            win32con.HWND_NOTOPMOST,
                            0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                        )
                    except Exception as pos_err:
                        print(f"  SetWindowPos失败: {pos_err}")
                    
                    # 等待窗口完全激活
                    time.sleep(0.5)
                    
                    # 验证窗口是否真正激活
                    try:
                        fg_hwnd = win32gui.GetForegroundWindow()
                        if fg_hwnd == schematic_hwnd:
                            print("✓ 原理图窗口激活成功！")
                            activation_success = True
                            break
                        else:
                            print(f"  窗口未激活，前台窗口: {win32gui.GetWindowText(fg_hwnd)}")
                    except Exception:
                        pass
                    
                    # 如果还没成功，等待后重试
                    if not activation_success and retry < 4:
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"  激活窗口失败 (第{retry+1}次): {e}")
                    if retry < 4:
                        time.sleep(0.5)
            
            if not activation_success:
                print("⚠ 窗口激活失败，但将继续尝试动画...")
            
            # 额外等待，确保窗口UI完全加载
            time.sleep(0.3)
            
            # 按Home键回到原点视图
            win32api.keybd_event(0x24, 0, 0, 0)  # VK_HOME down
            time.sleep(0.05)
            win32api.keybd_event(0x24, 0, 0x0002, 0)  # VK_HOME up
            time.sleep(0.4)
            
            # 执行逐步展示动画
            # 方案：通过视图操作和刷新模拟逐步放置效果
            for step in range(total_steps):
                time.sleep(0.7)  # 每步间隔
                
                # 定期刷新视图来创造动态效果
                if step % 2 == 0:
                    # 按F键自动适应视图
                    win32api.keybd_event(0x46, 0, 0, 0)  # 'F' down
                    time.sleep(0.05)
                    win32api.keybd_event(0x46, 0, 0x0002, 0)  # 'F' up
                    time.sleep(0.3)
                
                # 在某些步骤添加轻微缩放效果
                if step % 4 == 1:
                    # 模拟鼠标滚轮（放大）
                    # 注意：这需要鼠标在窗口内
                    pass
            
            # 最终适应完整视图
            time.sleep(0.6)
            win32api.keybd_event(0x46, 0, 0, 0)  # 'F' down
            time.sleep(0.05)
            win32api.keybd_event(0x46, 0, 0x0002, 0)  # 'F' up
            time.sleep(0.4)
            
            # 添加轻微的刷新效果（Ctrl+R）
            # 按住Ctrl
            win32api.keybd_event(0x11, 0, 0, 0)  # VK_CONTROL down
            time.sleep(0.05)
            # 按R键
            win32api.keybd_event(0x52, 0, 0, 0)  # 'R' down
            time.sleep(0.05)
            win32api.keybd_event(0x52, 0, 0x0002, 0)  # 'R' up
            time.sleep(0.05)
            # 释放Ctrl
            win32api.keybd_event(0x11, 0, 0x0002, 0)  # VK_CONTROL up
            time.sleep(0.5)
            
        except Exception as e:
            print(f"动画展示失败: {e}")
            # 恢复备份
            try:
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, schematic_path)
            except:
                pass
            return jsonify({
                "status": "error",
                "error": f"动画展示失败: {str(e)}"
            }), 500
        finally:
            # 清理备份文件
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
            except Exception as e:
                print(f"清理备份文件失败: {e}")
        
        return jsonify({
            "status": "success",
            "message": "原理图展示完成",
            "total_steps": total_steps
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
"""

@app.route("/api/eda/auto_route", methods=["POST"])
def api_eda_auto_route():
    """自动打开KiCad并点击自动布线按钮
    
    POST参数（可选）：
    - offset_x: 点击位置X偏移（距离右边缘的像素），默认18
    - offset_y: 点击位置Y偏移（距离顶部的像素），默认55
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # 获取自定义点击位置偏移量
        offset_x = int(data.get('offset_x', 600))  # 距离右边缘的像素
        offset_y = int(data.get('offset_y', 80))  # 距离顶部的像素
        
        # 默认KiCad安装路径
        kicad_install_dir = data.get("kicad_path", r"D:\Program Files\KiCad\8.0")
        
        # 检查是否存在其他常见安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_found = False
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'kicad.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                kicad_found = True
                break
        
        if not kicad_found:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # PCB文件路径
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        pcb_path = os.path.join(root, "EDA", "Two_Phase_Buck", "Two_Phase_Buck.kicad_pcb")
        pcb_dir = os.path.dirname(pcb_path)
        
        if not os.path.exists(pcb_path):
            return jsonify({
                "status": "error", 
                "error": f"PCB文件不存在: {pcb_path}"
            }), 400
        
        # 启动KiCad PCB编辑器
        pcbnew_path = os.path.join(kicad_install_dir, 'bin', 'pcbnew.exe')
        
        if not os.path.exists(pcbnew_path):
            return jsonify({
                "status": "error", 
                "error": f"PCB编辑器不存在: {pcbnew_path}"
            }), 400
        
        # 直接打开KiCad PCB编辑器，不执行复杂的自动化脚本
        # 简单可靠的方案：打开PCB并给出清晰的操作指引
        
        # 设置正确的环境变量，避免KiCad关闭时出错
        env = os.environ.copy()
        # 设置项目目录环境变量
        env['KIPRJMOD'] = pcb_dir
        # 确保KiCad能找到Python
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 使用正确的环境变量启动KiCad
        proc = subprocess.Popen(
            [pcbnew_path, pcb_path],
            shell=False,
            env=env,
            cwd=pcb_dir  # 设置工作目录为PCB所在目录
        )
        time.sleep(3)  # 等待窗口完全加载
        
        # 尝试自动点击工具栏最后一个按钮（自动布线）
        auto_click_success = False
        error_detail = None
        toolbar_right_x = None
        toolbar_y = None
        
        if win32gui and win32api:
            try:
                # 查找KiCad PCB编辑器窗口
                def find_kicad_window():
                    def callback(hwnd, hwnds):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            # KiCad PCB编辑器窗口标题通常包含这些关键词
                            if ('PCB Editor' in title or 'pcbnew' in title.lower() or 
                                'Two_Phase_Buck' in title or '.kicad_pcb' in title):
                                hwnds.append(hwnd)
                        return True
                    
                    hwnds = []
                    win32gui.EnumWindows(callback, hwnds)
                    return hwnds[0] if hwnds else None
                
                # 多次尝试查找窗口（最多10次，每次等待0.5秒）
                kicad_hwnd = None
                for attempt in range(10):
                    kicad_hwnd = find_kicad_window()
                    if kicad_hwnd:
                        break
                    time.sleep(0.5)
                
                if kicad_hwnd:
                    # 获取窗口位置和大小
                    rect = win32gui.GetWindowRect(kicad_hwnd)
                    left, top, right, bottom = rect
                    window_width = right - left
                    window_height = bottom - top
                    
                    # 使用更强大的窗口激活方法（带重试机制）
                    activation_success = False
                    for retry in range(5):  # 最多重试5次
                        try:
                            print(f"尝试激活窗口 (第{retry+1}次)...")
                            
                            # 如果窗口最小化，先恢复
                            if win32gui.IsIconic(kicad_hwnd):
                                win32gui.ShowWindow(kicad_hwnd, win32con.SW_RESTORE)
                                time.sleep(0.3)
                            
                            # 方法1: 使用ShowWindow确保窗口可见
                            win32gui.ShowWindow(kicad_hwnd, win32con.SW_SHOW)
                            time.sleep(0.2)
                            
                            # 方法2: 模拟Alt键释放（绕过Windows的前台窗口限制）
                            # 这是一个关键技巧，可以让SetForegroundWindow在新窗口上工作
                            try:
                                win32api.keybd_event(0x12, 0, 0x0002, 0)  # Alt键释放
                                time.sleep(0.05)
                            except Exception:
                                pass
                            
                            # 方法3: 使用AttachThreadInput方法
                            try:
                                current_thread = win32api.GetCurrentThreadId()
                                target_thread, _ = win32process.GetWindowThreadProcessId(kicad_hwnd)
                                
                                if current_thread != target_thread:
                                    # 附加线程输入
                                    win32process.AttachThreadInput(current_thread, target_thread, True)
                                    time.sleep(0.1)
                                    
                                    # 置顶窗口
                                    win32gui.BringWindowToTop(kicad_hwnd)
                                    time.sleep(0.1)
                                    
                                    # 设置为前台窗口
                                    win32gui.SetForegroundWindow(kicad_hwnd)
                                    time.sleep(0.1)
                                    
                                    # 分离线程输入
                                    win32process.AttachThreadInput(current_thread, target_thread, False)
                                else:
                                    # 如果是同一线程，直接设置
                                    win32gui.BringWindowToTop(kicad_hwnd)
                                    win32gui.SetForegroundWindow(kicad_hwnd)
                                    
                            except Exception as attach_err:
                                print(f"  AttachThreadInput失败: {attach_err}")
                                # 如果AttachThreadInput失败，尝试简单方法
                                win32gui.BringWindowToTop(kicad_hwnd)
                                time.sleep(0.1)
                                win32gui.SetForegroundWindow(kicad_hwnd)
                            
                            # 方法4: 使用SetWindowPos强制置顶
                            try:
                                win32gui.SetWindowPos(
                                    kicad_hwnd,
                                    win32con.HWND_TOPMOST,  # 设置为最顶层
                                    0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                                )
                                time.sleep(0.1)
                                # 取消最顶层状态（恢复正常）
                                win32gui.SetWindowPos(
                                    kicad_hwnd,
                                    win32con.HWND_NOTOPMOST,
                                    0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                                )
                            except Exception as pos_err:
                                print(f"  SetWindowPos失败: {pos_err}")
                            
                            # 等待窗口完全激活
                            time.sleep(0.5)
                            
                            # 验证窗口是否真正激活
                            try:
                                fg_hwnd = win32gui.GetForegroundWindow()
                                if fg_hwnd == kicad_hwnd:
                                    print("✓ 窗口激活成功！")
                                    activation_success = True
                                    break
                                else:
                                    print(f"  窗口未激活，前台窗口: {win32gui.GetWindowText(fg_hwnd)}")
                            except Exception:
                                pass
                            
                            # 如果还没成功，等待后重试
                            if not activation_success and retry < 4:
                                time.sleep(0.5)
                                
                        except Exception as e:
                            print(f"  激活窗口失败 (第{retry+1}次): {e}")
                            if retry < 4:
                                time.sleep(0.5)
                    
                    if not activation_success:
                        print("⚠ 窗口激活失败，但将继续尝试点击...")
                    
                    # 额外等待，确保窗口UI完全加载
                    time.sleep(0.5)
                    
                    # 根据KiCad工具栏布局，最后一个按钮位于右侧
                    # 从图片看，工具栏高度约40-60像素，按钮在最右端
                    # KiCad的工具栏按钮通常是固定大小（约30x30像素）
                    
                    # 计算点击位置（工具栏最右侧按钮）- 使用用户提供的偏移量
                    toolbar_y = top + offset_y  # 工具栏中心Y坐标
                    toolbar_right_x = right - offset_x  # 最后一个按钮中心位置  
                    
                    # 移动鼠标到目标位置
                    win32api.SetCursorPos((toolbar_right_x, toolbar_y))
                    time.sleep(0.5)  # 增加等待时间
                    
                    # 执行鼠标左键点击
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    time.sleep(0.2)
                    
                    auto_click_success = True
                    
                    # 返回调试信息，帮助用户了解点击位置
                    print(f"窗口矩形: left={left}, top={top}, right={right}, bottom={bottom}")
                    print(f"点击位置: x={toolbar_right_x}, y={toolbar_y}")
                    print(f"窗口尺寸: {window_width}x{window_height}")
                    
                else:
                    error_detail = "未找到KiCad PCB编辑器窗口"
                    
            except Exception as e:
                error_detail = f"自动点击失败: {str(e)}"
                print(f"自动点击工具栏按钮时出错: {e}")
        
        # 返回结果
        if auto_click_success:
            return jsonify({
                "status": "success",
                "message": "KiCad PCB编辑器已打开，已自动点击自动布线按钮",
                "pcb_path": pcb_path,
                "kicad_path": kicad_install_dir,
                "pid": proc.pid,
                "auto_route": True,
                "auto_click": True,
                "click_position": {
                    "x": toolbar_right_x,
                    "y": toolbar_y,
                    "offset_x": offset_x,
                    "offset_y": offset_y
                }
            })
        else:
            return jsonify({
                "status": "success",
                "message": "KiCad PCB编辑器已打开",
                "pcb_path": pcb_path,
                "kicad_path": kicad_install_dir,
                "pid": proc.pid,
                "auto_route": False,
                "auto_click": False,
                "error_detail": error_detail,
                "manual_steps": [
                    "1. 在KiCad PCB编辑器中，点击工具栏最右侧的自动布线按钮",
                    "2. 或者通过菜单：工具(Tools) → 外部插件(External Plugins) → FreeRouting"
                ],
                "quick_tip": "提示：如果找不到FreeRouting插件，请先在 工具 → 插件和内容管理器 中安装"
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/open_schematic", methods=["POST"])
def api_eda_open_schematic():
    """打开KiCad软件（项目管理器）"""
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'kicad.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Two_Phase_Buck")
        
        # 项目文件路径
        project_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_pro")
        
        # 检查文件是否存在
        if not os.path.exists(project_path):
            return jsonify({
                "status": "error", 
                "error": f"项目文件不存在: {project_path}"
            }), 400
        
        # KiCad主程序路径
        kicad_path = os.path.join(kicad_install_dir, 'bin', 'kicad.exe')
        
        if not os.path.exists(kicad_path):
            return jsonify({
                "status": "error", 
                "error": f"KiCad程序不存在: {kicad_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 启动KiCad主程序
        proc = subprocess.Popen(
            [kicad_path, project_path],
            shell=False,
            env=env,
            cwd=project_dir
        )
        
        time.sleep(2)  # 等待窗口完全加载
        
        return jsonify({
            "status": "success",
            "message": "KiCad软件已打开",
            "project_path": project_path,
            "pid": proc.pid,
            "kicad_path": kicad_install_dir
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/open_pcb", methods=["POST"])
def api_eda_open_pcb():
    """单独打开KiCad PCB编辑器"""
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'pcbnew.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Two_Phase_Buck")
        
        # PCB文件路径
        pcb_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_pcb")
        
        # 检查文件是否存在
        if not os.path.exists(pcb_path):
            return jsonify({
                "status": "error", 
                "error": f"PCB文件不存在: {pcb_path}"
            }), 400
        
        # PCB编辑器路径
        pcbnew_path = os.path.join(kicad_install_dir, 'bin', 'pcbnew.exe')
        
        if not os.path.exists(pcbnew_path):
            return jsonify({
                "status": "error", 
                "error": f"PCB编辑器不存在: {pcbnew_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 启动PCB编辑器
        proc = subprocess.Popen(
            [pcbnew_path, pcb_path],
            shell=False,
            env=env,
            cwd=project_dir
        )
        
        time.sleep(2)  # 等待窗口完全加载
        
        return jsonify({
            "status": "success",
            "message": "PCB编辑器已打开",
            "pcb_path": pcb_path,
            "pid": proc.pid,
            "kicad_path": kicad_install_dir
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/open_schematic_only", methods=["POST"])
def api_eda_open_schematic_only():
    """只打开原理图编辑器（eeschema），不打开KiCad或PCB"""
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'eeschema.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Two_Phase_Buck")
        
        # 原理图文件路径
        schematic_path = os.path.join(project_dir, "Two_Phase_Buck.kicad_sch")
        
        # 检查文件是否存在
        if not os.path.exists(schematic_path):
            return jsonify({
                "status": "error", 
                "error": f"原理图文件不存在: {schematic_path}"
            }), 400
        
        # 原理图编辑器路径
        eeschema_path = os.path.join(kicad_install_dir, 'bin', 'eeschema.exe')
        
        if not os.path.exists(eeschema_path):
            return jsonify({
                "status": "error", 
                "error": f"原理图编辑器不存在: {eeschema_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 启动原理图编辑器
        proc = subprocess.Popen(
            [eeschema_path, schematic_path],
            shell=False,
            env=env,
            cwd=project_dir
        )
        
        time.sleep(2)  # 等待窗口完全加载
        
        # 尝试最大化窗口
        try:
            import win32gui
            import win32con
            
            def find_schematic_window():
                hwnds = []
                def callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if 'Schematic Editor' in title or 'eeschema' in title.lower() or 'Two_Phase_Buck' in title:
                            hwnds.append(hwnd)
                    return True
                hwnds = []
                win32gui.EnumWindows(callback, hwnds)
                return hwnds[0] if hwnds else None
            
            # 多次尝试查找窗口
            schematic_hwnd = None
            for attempt in range(10):
                schematic_hwnd = find_schematic_window()
                if schematic_hwnd:
                    break
                time.sleep(0.5)
            
            if schematic_hwnd:
                # 最大化窗口
                if win32gui.IsIconic(schematic_hwnd):
                    win32gui.ShowWindow(schematic_hwnd, win32con.SW_RESTORE)
                    time.sleep(0.3)
                
                win32gui.ShowWindow(schematic_hwnd, win32con.SW_SHOW)
                time.sleep(0.2)
                win32gui.BringWindowToTop(schematic_hwnd)
                time.sleep(0.2)
                win32gui.ShowWindow(schematic_hwnd, win32con.SW_MAXIMIZE)
                
        except Exception as e:
            print(f"最大化窗口失败: {e}")
        
        return jsonify({
            "status": "success",
            "message": "原理图编辑器已打开",
            "schematic_path": schematic_path,
            "pid": proc.pid,
            "kicad_path": kicad_install_dir
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/get_schematic_content", methods=["POST"])
def api_eda_get_schematic_content():
    """获取原理图文件内容"""
    try:
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        schematic_path = os.path.join(root, "EDA", "Two_Phase_Buck", "Two_Phase_Buck.kicad_sch")
        
        # 检查文件是否存在
        if not os.path.exists(schematic_path):
            return jsonify({
                "status": "error", 
                "error": f"原理图文件不存在: {schematic_path}"
            }), 400
        
        # 读取文件内容
        with open(schematic_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "content": content,
            "file_path": schematic_path,
            "file_size": len(content)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/save_schematic_content", methods=["POST"])
def api_eda_save_schematic_content():
    """保存原理图文件内容"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # 获取编辑后的内容
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                "status": "error", 
                "error": "内容为空，无法保存"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        schematic_path = os.path.join(root, "EDA", "Two_Phase_Buck", "Two_Phase_Buck.kicad_sch")
        
        # 创建备份
        backup_path = schematic_path + ".backup"
        if os.path.exists(schematic_path):
            import shutil
            shutil.copy2(schematic_path, backup_path)
        
        # 保存新内容
        with open(schematic_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "status": "success",
            "message": "原理图文件已保存",
            "file_path": schematic_path,
            "backup_path": backup_path,
            "file_size": len(content)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/get_custom_schematic_content", methods=["POST"])
def api_eda_get_custom_schematic_content():
    """获取自定义原理图文件内容（Self_Design）"""
    try:
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        schematic_path = os.path.join(root, "EDA", "Self_Design", "Self_Design.kicad_sch")
        
        # 检查文件是否存在
        if not os.path.exists(schematic_path):
            return jsonify({
                "status": "error", 
                "error": f"自定义原理图文件不存在: {schematic_path}"
            }), 400
        
        # 读取文件内容
        with open(schematic_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "content": content,
            "file_path": schematic_path,
            "file_size": len(content)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/save_custom_schematic_content", methods=["POST"])
def api_eda_save_custom_schematic_content():
    """保存自定义原理图文件内容（Self_Design）"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # 获取编辑后的内容
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                "status": "error", 
                "error": "内容为空，无法保存"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        schematic_path = os.path.join(root, "EDA", "Self_Design", "Self_Design.kicad_sch")
        
        # 创建备份
        backup_path = schematic_path + ".backup"
        if os.path.exists(schematic_path):
            import shutil
            shutil.copy2(schematic_path, backup_path)
        
        # 保存新内容
        with open(schematic_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "status": "success",
            "message": "自定义原理图文件已保存",
            "file_path": schematic_path,
            "backup_path": backup_path,
            "file_size": len(content)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/open_custom_kicad", methods=["POST"])
def api_eda_open_custom_kicad():
    """打开KiCad软件（Self_Design项目）"""
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'kicad.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Self_Design")
        
        # 项目文件路径
        project_path = os.path.join(project_dir, "Self_Design.kicad_pro")
        
        # 检查文件是否存在
        if not os.path.exists(project_path):
            return jsonify({
                "status": "error", 
                "error": f"Self_Design项目文件不存在: {project_path}"
            }), 400
        
        # KiCad主程序路径
        kicad_path = os.path.join(kicad_install_dir, 'bin', 'kicad.exe')
        
        if not os.path.exists(kicad_path):
            return jsonify({
                "status": "error", 
                "error": f"KiCad程序不存在: {kicad_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 启动KiCad主程序
        proc = subprocess.Popen(
            [kicad_path, project_path],
            shell=False,
            env=env,
            cwd=project_dir
        )
        
        time.sleep(2)  # 等待窗口完全加载
        
        return jsonify({
            "status": "success",
            "message": "KiCad软件已打开（Self_Design项目）",
            "project_path": project_path,
            "pid": proc.pid,
            "kicad_path": kicad_install_dir
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/eda/open_custom_schematic_only", methods=["POST"])
def api_eda_open_custom_schematic_only():
    """只打开Self_Design原理图编辑器（eeschema），不打开KiCad或PCB"""
    try:
        # 默认KiCad安装路径
        possible_paths = [
            r"D:\Program Files\KiCad\8.0",
            r"C:\Program Files\KiCad\8.0",
            r"C:\Program Files (x86)\KiCad\8.0",
            r"D:\Program Files\KiCad\KiCad8.0.8",
        ]
        
        kicad_install_dir = None
        for path in possible_paths:
            bin_path = os.path.join(path, 'bin', 'eeschema.exe')
            if os.path.exists(bin_path):
                kicad_install_dir = path
                break
        
        if not kicad_install_dir:
            return jsonify({
                "status": "error", 
                "error": "未找到KiCad 8.0安装目录，请确认KiCad已正确安装"
            }), 400
        
        # 获取项目根目录
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        project_dir = os.path.join(root, "EDA", "Self_Design")
        
        # 原理图文件路径
        schematic_path = os.path.join(project_dir, "Self_Design.kicad_sch")
        
        # 检查文件是否存在
        if not os.path.exists(schematic_path):
            return jsonify({
                "status": "error", 
                "error": f"Self_Design原理图文件不存在: {schematic_path}"
            }), 400
        
        # 原理图编辑器路径
        eeschema_path = os.path.join(kicad_install_dir, 'bin', 'eeschema.exe')
        
        if not os.path.exists(eeschema_path):
            return jsonify({
                "status": "error", 
                "error": f"原理图编辑器不存在: {eeschema_path}"
            }), 400
        
        # 设置环境变量
        env = os.environ.copy()
        env['KIPRJMOD'] = project_dir
        env['PYTHONPATH'] = os.path.join(kicad_install_dir, 'bin', 'Lib', 'site-packages')
        
        # 启动原理图编辑器
        proc = subprocess.Popen(
            [eeschema_path, schematic_path],
            shell=False,
            env=env,
            cwd=project_dir
        )
        
        time.sleep(2)  # 等待窗口完全加载
        
        # 尝试最大化窗口
        try:
            import win32gui
            import win32con
            
            def find_schematic_window():
                hwnds = []
                def callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if 'Schematic Editor' in title or 'eeschema' in title.lower() or 'Self_Design' in title:
                            hwnds.append(hwnd)
                    return True
                hwnds = []
                win32gui.EnumWindows(callback, hwnds)
                return hwnds[0] if hwnds else None
            
            # 多次尝试查找窗口
            schematic_hwnd = None
            for attempt in range(10):
                schematic_hwnd = find_schematic_window()
                if schematic_hwnd:
                    break
                time.sleep(0.5)
            
            if schematic_hwnd:
                # 最大化窗口
                if win32gui.IsIconic(schematic_hwnd):
                    win32gui.ShowWindow(schematic_hwnd, win32con.SW_RESTORE)
                    time.sleep(0.3)
                
                win32gui.ShowWindow(schematic_hwnd, win32con.SW_SHOW)
                time.sleep(0.2)
                win32gui.BringWindowToTop(schematic_hwnd)
                time.sleep(0.2)
                win32gui.ShowWindow(schematic_hwnd, win32con.SW_MAXIMIZE)
                
        except Exception as e:
            print(f"最大化窗口失败: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Self_Design原理图编辑器已打开",
            "schematic_path": schematic_path,
            "pid": proc.pid,
            "kicad_path": kicad_install_dir
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# 下面是旧代码（已被替换）
"""
Old UI automation code removed - now using direct Python API approach
                # 查找KiCad PCB编辑器窗口
                def find_kicad_window_OLD():
                    def callback(hwnd, hwnds):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if 'PCB Editor' in title or 'pcbnew' in title.lower() or 'Two_Phase_Buck' in title:
                                hwnds.append(hwnd)
                        return True
                    
                    hwnds = []
                    win32gui.EnumWindows(callback, hwnds)
                    return hwnds[0] if hwnds else None
                
                # 多次尝试查找窗口
                kicad_hwnd = None
                for attempt in range(10):
                    kicad_hwnd = find_kicad_window()
                    if kicad_hwnd:
                        break
                    time.sleep(0.5)
                
                if kicad_hwnd:
                    # 激活窗口 - 使用更可靠的方法
                    try:
                        # 方法1: 尝试直接设置前台窗口
                        try:
                            win32gui.SetForegroundWindow(kicad_hwnd)
                        except Exception:
                            # 方法2: 如果失败，先最小化再恢复
                            win32gui.ShowWindow(kicad_hwnd, 6)  # SW_MINIMIZE
                            time.sleep(0.1)
                            win32gui.ShowWindow(kicad_hwnd, 9)  # SW_RESTORE
                            time.sleep(0.2)
                            # 方法3: 使用AttachThreadInput
                            try:
                                import win32process
                                current_thread = win32api.GetCurrentThreadId()
                                target_thread, _ = win32process.GetWindowThreadProcessId(kicad_hwnd)
                                if current_thread != target_thread:
                                    win32process.AttachThreadInput(current_thread, target_thread, True)
                                    win32gui.SetForegroundWindow(kicad_hwnd)
                                    win32gui.SetFocus(kicad_hwnd)
                                    win32process.AttachThreadInput(current_thread, target_thread, False)
                            except Exception:
                                pass
                        
                        # 确保窗口完全激活
                        time.sleep(1.5)
                        
                        # 使用win32api模拟按键来触发FreeRouting
                        import win32api
                        
                        # 首先按Esc确保没有其他菜单打开
                        win32api.keybd_event(0x1B, 0, 0, 0)  # Esc键按下
                        time.sleep(0.05)
                        win32api.keybd_event(0x1B, 0, 0x0002, 0)  # Esc键释放
                        time.sleep(0.3)
                        
                        # 按下Alt键打开菜单栏
                        win32api.keybd_event(0x12, 0, 0, 0)  # Alt键按下
                        time.sleep(0.2)
                        win32api.keybd_event(0x12, 0, 0x0002, 0)  # Alt键释放
                        time.sleep(0.5)
                        
                        # 按T键进入工具菜单（Tools）
                        win32api.keybd_event(ord('T'), 0, 0, 0)  # T键按下
                        time.sleep(0.05)
                        win32api.keybd_event(ord('T'), 0, 0x0002, 0)  # T键释放
                        time.sleep(1.0)  # 等待菜单完全展开
                        
                        # 按E键跳转到External Plugins（外部插件）
                        # 如果菜单中有快捷键字母提示，使用字母会更准确
                        win32api.keybd_event(ord('E'), 0, 0, 0)  # E键按下
                        time.sleep(0.05)
                        win32api.keybd_event(ord('E'), 0, 0x0002, 0)  # E键释放
                        time.sleep(0.8)  # 等待子菜单展开
                        
                        # 按F键选择FreeRouting或直接按Enter（如果是第一项）
                        win32api.keybd_event(ord('F'), 0, 0, 0)  # F键按下
                        time.sleep(0.05)
                        win32api.keybd_event(ord('F'), 0, 0x0002, 0)  # F键释放
                        time.sleep(0.3)
                        
                        # 最后按Enter确认
                        win32api.keybd_event(0x0D, 0, 0, 0)  # Enter键按下
                        time.sleep(0.05)
                        win32api.keybd_event(0x0D, 0, 0x0002, 0)  # Enter键释放
                        
                        return jsonify({
                            "status": "success",
                            "message": "KiCad PCB编辑器已打开，FreeRouting自动布线已启动",
                            "pcb_path": pcb_path,
                            "kicad_path": kicad_install_dir,
                            "pid": proc.pid,
                            "auto_route": True
                        })
                    except Exception as key_err:
                        # 按键操作失败，但窗口已打开
                        print(f"按键模拟失败: {key_err}")
                        return jsonify({
                            "status": "success",
                            "message": "KiCad PCB编辑器已打开，但自动触发按键失败",
                            "pcb_path": pcb_path,
                            "kicad_path": kicad_install_dir,
                            "pid": proc.pid,
                            "auto_route": False,
                            "note": "窗口已激活但按键模拟失败",
                            "error_detail": str(key_err)
                        })
                else:
                    # 如果找不到窗口，至少打开了KiCad
                    return jsonify({
                        "status": "success",
                        "message": "KiCad PCB编辑器已打开，但无法自动触发FreeRouting",
                        "pcb_path": pcb_path,
                        "kicad_path": kicad_install_dir,
                        "pid": proc.pid,
                        "auto_route": False,
                        "note": "请手动选择 工具 -> 外部插件 -> FreeRouting"
                    })
            else:
                # 如果没有win32api，返回基本信息
                return jsonify({
                    "status": "success",
                    "message": "KiCad PCB编辑器已打开",
                    "pcb_path": pcb_path,
                    "kicad_path": kicad_install_dir,
                    "pid": proc.pid,
                    "auto_route": False,
                    "note": "缺少win32api模块，无法自动触发FreeRouting"
                })
        except Exception as auto_err:
            print(f"自动触发FreeRouting时出错: {auto_err}")
            return jsonify({
                "status": "success",
                "message": "KiCad PCB编辑器已打开，但自动触发FreeRouting失败",
                "pcb_path": pcb_path,
                "kicad_path": kicad_install_dir,
                "pid": proc.pid,
                "auto_route": False,
                "error_detail": str(auto_err)
            })
"""

if __name__ == "__main__":
    # 启动定期清理任务
    def cleanup_task():
        while True:
            time.sleep(1800)  # 每30分钟清理一次
            cleanup_old_sessions()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))

    local_url = f"http://127.0.0.1:{port}"
    lan_ip = get_lan_ip()
    lan_url = f"http://{lan_ip}:{port}"

    try:
        from waitress import serve
        print("[startup] AI+电力电子 已启动 (生产服务器: waitress)")
        print(f"[startup] 本机访问:    {local_url}")
        print(f"[startup] 局域网访问:  {lan_url}")
        print("------------------------------------------------------------------------------------------------")
        public_url = maybe_start_ngrok(port)
        if public_url:
            # 获取region信息用于显示
            region = os.environ.get("NGROK_REGION", "auto").strip()
            print(f"[startup] 随机公网访问网址(ngrok): {public_url} (region={region})")
            print(f"[startup] 请分享固定公网地址: https://ai_power_electronics.aipowerelectronics.top")
            print(f"[startup] 请分享随机公网地址: {public_url}")
            # 仅在成功获得公网地址时再启动守护线程
            try:
                threading.Thread(target=_ngrok_watchdog, args=(port,), daemon=True).start()
            except Exception:
                pass
        print("------------------------------------------------------------------------------------------------")
        
        # 优化waitress配置
        serve(
            app, 
            host=host, 
            port=port,
            threads=8,  # 增加线程数
            connection_limit=1000,  # 增加连接限制
            cleanup_interval=30,  # 清理间隔
            channel_timeout=120,  # 通道超时
            log_socket_errors=True,  # 记录socket错误
            max_request_header_size=262144,  # 最大请求头大小
            max_request_body_size=1073741824,  # 最大请求体大小 (1GB)
            expose_tracebacks=False,  # 不暴露traceback
            ident=None,  # 不使用ident
            asyncore_use_poll=True,  # 使用poll
            recv_bytes=8192,  # 接收字节数
            send_bytes=18000,  # 发送字节数
        )
    except Exception as exc:
        print("[startup] Failed to start waitress, falling back to Flask dev server:", exc, file=sys.stderr)
        print(f"[startup] 本机访问:    {local_url}")
        print(f"[startup] 局域网访问:  {lan_url}")
        print("------------------------------------------------------------------------------------------------")
        public_url = maybe_start_ngrok(port)
        if public_url:
            # 获取region信息用于显示
            region = os.environ.get("NGROK_REGION", "auto").strip()
            print(f"[startup] 随机公网访问网址(ngrok): {public_url} (region={region})")
            print(f"[startup] 请分享固定公网地址: https://ai_power_electronics.aipowerelectronics.top")
            print(f"[startup] 请分享随机公网地址: {public_url}")
            try:
                threading.Thread(target=_ngrok_watchdog, args=(port,), daemon=True).start()
            except Exception:
                pass
        print("------------------------------------------------------------------------------------------------")
        
        # ---------------- Running Tasks API ----------------
        
        @app.route("/api/run/start", methods=["POST"])
        def run_start():
            payload = request.json or {}
            task = (payload.get("task") or "").strip()  # mt or ppo
            if task not in {"mt", "ppo", "ppo_defined"}:
                return jsonify({"error": "invalid_task"}), 400
            script = resolve_script_by_task(task)
            if not script:
                return jsonify({"error": "script_not_found"}), 404
            run_id = run_python_script_realtime(script_path=script)

            # Wait briefly for the startup line to be appended to buffer to avoid double printing
            initial_next = 0
            for _ in range(50):  # up to ~500ms
                with RUNS_LOCK:
                    info = RUNS.get(run_id, {})
                    initial_next = len(info.get("buffer", []))
                if initial_next > 0:
                    break
                import time as _t
                _t.sleep(0.01)

            return jsonify({"run_id": run_id, "next": initial_next})


        @app.route("/api/run/stream", methods=["GET"])
        def run_stream():
            run_id = (request.args.get("run_id") or "").strip()
            if not run_id:
                return Response("event: error\ndata: missing_run_id\n\n", mimetype="text/event-stream")

            with RUNS_LOCK:
                info = RUNS.get(run_id)
            if not info:
                return Response("event: error\ndata: run_not_found\n\n", mimetype="text/event-stream")

            q: "queue.Queue[str]" = info["queue"]
            proc: subprocess.Popen = info["proc"]

            def gen():
                last_line = None
                while True:
                    try:
                        line = q.get(timeout=0.5)  # 增加超时时间
                    except Exception:
                        if proc.poll() is not None:
                            break
                        yield ": keep-alive\n\n"
                        continue
                    if line == "[runner] __PROC_EOF__":
                        break
                    if line == last_line:
                        continue
                    last_line = line
                    # 确保输出立即刷新
                    yield f"data: {line}\n\n"
                yield "event: done\ndata: [DONE]\n\n"

            return Response(
                stream_with_context(gen()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                },
            )


        @app.route("/api/run/poll", methods=["GET"])
        def run_poll():
            run_id = (request.args.get("run_id") or "").strip()
            cursor_str = (request.args.get("cursor") or "0").strip()
            try:
                cursor = int(cursor_str)
            except Exception:
                cursor = 0
            
            with RUNS_LOCK:
                info = RUNS.get(run_id)
                if not info:
                    return jsonify({"error": "run_not_found"}), 404
                buf: List[str] = info.setdefault("buffer", [])
                proc: subprocess.Popen = info["proc"]
            
            # 检查进程是否还在运行
            if proc.poll() is not None and not buf:
                return jsonify({"done": True, "lines": [], "next": len(buf)})
            
            # 返回新行
            new_lines = buf[cursor:]
            return jsonify({"done": proc.poll() is not None, "lines": new_lines, "next": len(buf)})


        @app.route("/api/run/stop", methods=["POST"])
        def run_stop():
            run_id = (request.json or {}).get("run_id", "").strip()
            if not run_id:
                return jsonify({"error": "missing_run_id"}), 400
            
            with RUNS_LOCK:
                info = RUNS.get(run_id)
                if not info:
                    return jsonify({"error": "run_not_found"}), 404
                
                proc: subprocess.Popen = info["proc"]
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        # 等待进程结束
                        proc.wait(timeout=5)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                
                # 清理运行记录
                del RUNS[run_id]
            
            return jsonify({"ok": True})

        @app.route("/run", methods=["GET"])
        def run_page():
            task = (request.args.get("task") or "").strip()
            if task not in {"mt", "ppo", "ppo_defined", "eda"}:
                return redirect(url_for("index"))
            return render_template("run.html", title="AI+电力电子 - 运行", task=task)
        
        app.run(host=host, port=port, debug=False, threaded=True)
