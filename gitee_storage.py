"""
Gitee 数据持久化层 (Data Persistence Layer)
=============================================
利用 Gitee API v5 将反馈/工单数据存储在仓库的 data/feedback/ 目录下。
支持：写入反馈、读取全部反馈、更新反馈状态、发布系统通知。

设计为可替换的数据层抽象：未来可无缝切换为 PostgreSQL / MongoDB / Supabase
等生产级数据库，只需替换本文件实现即可，上层业务逻辑零改动。
"""

import base64
import json
import requests
import streamlit as st
from datetime import datetime

GITEE_API_BASE = "https://gitee.com/api/v5"

# ---------------------------------------------------------------------------
# 配置读取
# ---------------------------------------------------------------------------

def get_config():
    """从 Streamlit Secrets 读取 Gitee 配置。本地开发时返回 None。"""
    try:
        return {
            "token": st.secrets["GITEE_TOKEN"],
            "repo":  st.secrets["GITEE_REPO"],
            "branch": st.secrets.get("GITEE_BRANCH", "main"),
        }
    except Exception:
        return None


def _owner_repo(repo_str):
    """将 'owner/repo' 拆分为 owner, repo。"""
    parts = repo_str.split("/")
    return parts[0], parts[1]


# ---------------------------------------------------------------------------
# 底层文件操作
# ---------------------------------------------------------------------------

def list_directory(path, config):
    """列出仓库指定目录下的文件列表。目录不存在时返回空列表。"""
    owner, repo = _owner_repo(config["repo"])
    url = f"{GITEE_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    params = {"access_token": config["token"], "ref": config["branch"]}
    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else [data]


def create_or_update_file(path, content_str, message, config):
    """创建或覆盖仓库中的文件。content_str 为明文，内部自动 Base64 编码。"""
    owner, repo = _owner_repo(config["repo"])
    url = f"{GITEE_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    sha = None
    try:
        existing = list_directory(path, config)
        if existing and len(existing) == 1 and existing[0].get("type") == "file":
            sha = existing[0].get("sha")
    except Exception:
        pass

    payload = {
        "access_token": config["token"],
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
        "message": message,
        "branch": config["branch"],
    }
    if sha:
        payload["sha"] = sha

    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def read_file_raw(path, config):
    """读取仓库中指定路径的单个文件。"""
    owner, repo = _owner_repo(config["repo"])
    url = f"{GITEE_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    params = {"access_token": config["token"], "ref": config["branch"]}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 反馈工单 (Feedback) CRUD
# ---------------------------------------------------------------------------

def save_feedback(feedback_data, config):
    """将一条反馈持久化到 Gitee 仓库的 data/feedback/ 目录。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = feedback_data.get("id", "unknown")[-6:]
    file_name = f"fb_{ts}_{suffix}.json"
    path = f"data/feedback/{file_name}"

    content = json.dumps(feedback_data, ensure_ascii=False, indent=2)
    msg = f"feedback: {feedback_data.get('type', '未知类型')} @ {feedback_data.get('page', '未知页面')}"
    return create_or_update_file(path, content, msg, config)


def load_all_feedbacks(config):
    """读取 data/feedback/ 目录下所有 .json 反馈文件，按时间倒序排列。"""
    try:
        files = list_directory("data/feedback", config)
    except Exception:
        return []

    feedbacks = []
    for f in files:
        if f.get("type") != "file" or not f.get("name", "").endswith(".json"):
            continue
        try:
            data = read_file_raw(f["path"], config)
            raw = base64.b64decode(data["content"]).decode("utf-8")
            item = json.loads(raw)
            item["_sha"] = data.get("sha")
            item["_path"] = f["path"]
            feedbacks.append(item)
        except Exception:
            continue

    feedbacks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return feedbacks


def update_feedback_status(path, sha, new_status, config):
    """更新指定反馈文件的状态字段。"""
    try:
        data = read_file_raw(path, config)
        raw = base64.b64decode(data["content"]).decode("utf-8")
        fb = json.loads(raw)
        fb["status"] = new_status
        fb["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_content = json.dumps(fb, ensure_ascii=False, indent=2)
        msg = f"update status: {new_status}"
        create_or_update_file(path, new_content, msg, config)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 系统通知 (Announcement) CRUD
# ---------------------------------------------------------------------------

def load_announcements(config):
    """读取 data/announcements.json 中的系统通知列表。"""
    try:
        data = read_file_raw("data/announcements.json", config)
        raw = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(raw)
    except Exception:
        return []


def save_announcements(announcements, config):
    """覆盖写入系统通知列表到 data/announcements.json。"""
    content = json.dumps(announcements, ensure_ascii=False, indent=2)
    return create_or_update_file("data/announcements.json", content, "update announcements", config)


def add_announcement(title, body, level, config):
    """追加一条系统通知。level 可选: info / warning / critical"""
    announcements = load_announcements(config)
    announcements.insert(0, {
        "id": f"ann_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": title,
        "body": body,
        "level": level,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_read": False,
    })
    announcements = announcements[:50]
    return save_announcements(announcements, config)
