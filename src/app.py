#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ComfyUI API Wrapper – per‑workflow API endpoints with schema discovery"""

import json
from pathlib import Path
from typing import List, Dict, Any

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------- 加载全局配置 ----------
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
if not CONFIG_PATH.is_file():
    raise FileNotFoundError(f"Missing config.json at {CONFIG_PATH}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

COMFYUI_URL = cfg.get("comfyui_url", "http://127.0.0.1:8188")
SERVICE_PORT = cfg.get("service_port", 5000)

WORKFLOW_DIR = Path(cfg.get("workflow_dir", "./"))
WORKFLOW_SOURCE_DIR = Path(cfg.get("workflow_source_dir", ""))
if not WORKFLOW_SOURCE_DIR.is_dir():
    raise FileNotFoundError(f"Workflow source directory not found: {WORKFLOW_SOURCE_DIR}")

# ---------- 工具函数 ----------
def load_workflow(fname: str) -> Dict[str, Any]:
    """读取 workflow JSON（只读）\n    先在本项目的 workflow_dir 查找，如未找到则在外部 workflow_source_dir 中查找"""
    local_path = WORKFLOW_DIR / fname
    if local_path.is_file():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    external_path = WORKFLOW_SOURCE_DIR / fname
    if external_path.is_file():
        with open(external_path, "r", encoding="utf-8") as f:
            return json.load(f)

    raise FileNotFoundError(
        f"Workflow file not found in either {WORKFLOW_DIR} or {WORKFLOW_SOURCE_DIR}: {fname}"
    )

def apply_modifications(workflow: Dict[str, Any], mods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """在内存中根据 mods 动态修改 workflow（宽容策略）"""
    nodes = workflow.get("nodes", [])
    for mod in mods:
        node_id = mod.get("node")
        field   = mod.get("field")
        value   = mod.get("value")
        if not (node_id and field):
            continue
        for n in nodes:
            if n.get("id") == node_id:
                if "outputs" in n and field in n["outputs"]:
                    n["outputs"][field] = value
                elif "inputs" in n and field in n["inputs"]:
                    n["inputs"][field] = value
                else:
                    n.setdefault("outputs", {})[field] = value
                break
    return workflow

def submit_to_comfyui(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """POST 完整 workflow 到 ComfyUI /prompt，返回 JSON 响应"""
    endpoint = f"{COMFYUI_URL.rstrip('/')}/prompt"
    try:
        resp = requests.post(
            endpoint,
            json=workflow,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ---------- 为每个工作流生成专属路由 ----------
def _slugify(name: str) -> str:
    """把文件名转成 URL‑safe slug（去空格、去 .json、换成下划线）"""
    return name.replace(" ", "_").replace(".json", "")

def make_endpoint(file_name: str):
    """返回一个处理 /api/<slug> 请求的视图函数"""
    def endpoint():
        payload = request.get_json(force=True) or {}
        modifications = payload.get("modifications", [])
        try:
            wf = load_workflow(file_name)
            wf_mod = apply_modifications(wf, modifications)
            res = submit_to_comfyui(wf_mod)
            print(f"[CALL] {file_name} – mods: {modifications}")
            return jsonify(res)
        except FileNotFoundError as fe:
            return jsonify({"error": str(fe)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    endpoint.__name__ = f"run_{_slugify(file_name)}"
    return endpoint

def make_schema_endpoint(file_name: str):
    """返回一个处理 /api/<slug>/schema 请求的视图函数（返回节点信息）"""
    def endpoint():
        try:
            wf = load_workflow(file_name)
            nodes = wf.get("nodes", [])
            # 简化节点信息，便于前端查看
            simplified = []
            for n in nodes:
                simplified.append({
                    "id": n.get("id"),
                    "type": n.get("type"),
                    "inputs": list(n.get("inputs", {}).keys()),
                    "outputs": list(n.get("outputs", {}).keys()),
                })
            return jsonify(simplified)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    endpoint.__name__ = f"schema_{_slugify(file_name)}"
    return endpoint

# 注册所有工作流的路由
for wf_path in WORKFLOW_SOURCE_DIR.glob("*.json"):
    fname = wf_path.name
    base_route = f"/api/{_slugify(fname)}"
    schema_route = f"{base_route}/schema"

    app.add_url_rule(base_route, view_func=make_endpoint(fname), methods=["POST"])
    app.add_url_rule(schema_route, view_func=make_schema_endpoint(fname), methods=["GET"])

# ---------- 主入口 ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=False)