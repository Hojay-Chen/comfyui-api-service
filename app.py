#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""comfyui_api_service - 简易 Flask 包装，让上层 Agent 可直接调用工作流

功能概述：
- 读取本项目目录下的 workflow JSON（仅读取，未修改磁盘文件）
- 根据请求体中的 `modifications` 列表，在内存中修改对应节点的字段
- 将完整的 workflow JSON 通过 ComfyUI 原始 `/prompt` 接口提交，返回 ComfyUI 的响应

注意：
- 本项目不修改任何 ComfyUI 源码，只做 *读‑改‑发* 的桥接
- 多次请求之间的修改是互相独立的（每次重新读取模板）
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------- 加载全局配置 ----------
CONFIG_PATH = Path(__file__).parent / "config.json"
if not CONFIG_PATH.is_file():
    raise FileNotFoundError(f"Missing config.json at {CONFIG_PATH}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)
COMFYUI_URL = cfg.get("comfyui_url", "http://127.0.0.1:8188")
WORKFLOW_DIR = Path(cfg.get("workflow_dir", "./"))
# Path to the real user‑provided ComfyUI workflows (outside this repo)
WORKFLOW_SOURCE_DIR = Path(cfg.get("workflow_source_dir", ""))
if not WORKFLOW_SOURCE_DIR.is_dir():
    raise FileNotFoundError(f"Workflow source directory not found: {WORKFLOW_SOURCE_DIR}")

# ---------- 工具函数 ----------
def load_workflow(fname: str) -> Dict[str, Any]:
    """读取 workflow JSON（只读）
    先在本项目的 workflow_dir 查找，如未找到则在外部 workflow_source_dir 中查找"""
    # 1) 本地模板目录
    local_path = WORKFLOW_DIR / fname
    if local_path.is_file():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 2) 外部真实工作流目录
    external_path = WORKFLOW_SOURCE_DIR / fname
    if external_path.is_file():
        with open(external_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 都没有则报错
    raise FileNotFoundError(f"Workflow file not found in either {WORKFLOW_DIR} or {WORKFLOW_SOURCE_DIR}: {fname}")

def apply_modifications(workflow: Dict[str, Any], mods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """在内存中根据 mods 修改 workflow
    mods 示例：[{"node": "PromptNode", "field": "prompt", "value": "test"}, ...]
    """
    nodes = workflow.get("nodes", [])
    # 简单的基于 node id 匹配
    for mod in mods:
        node_id = mod.get("node")
        field = mod.get("field")
        value = mod.get("value")
        if not (node_id and field):
            continue
        for n in nodes:
            if n.get("id") == node_id:
                # 假设所有可修改字段都在 "outputs" 或 "inputs" 中
                if "outputs" in n and field in n["outputs"]:
                    n["outputs"][field] = value
                elif "inputs" in n and field in n["inputs"]:
                    n["inputs"][field] = value
                else:
                    # 若字段不存在则直接放入 outputs（宽容策略）
                    n.setdefault("outputs", {})[field] = value
                break
    return workflow

def submit_to_comfyui(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """调用 ComfyUI 的 `/prompt` 接口提交完整 workflow JSON"""
    endpoint = f"{COMFYUI_URL.rstrip('/')}/prompt"
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(endpoint, json=workflow, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ---------- API 路由 ----------
@app.route("/run", methods=["POST"])
def run_workflow():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    workflow_file = data.get("workflow", "workflow_template.json")
    modifications = data.get("modifications", [])

    try:
        wf = load_workflow(workflow_file)
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        return jsonify(result)
    except FileNotFoundError as fe:
        return jsonify({"error": str(fe)}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# ---------- 为每个工作流生成专属路由 ----------
def _slugify(name: str) -> str:
    # 简单将空格替换为下划线，去掉 .json 后缀
    return name.replace(' ', '_').replace('.json', '')

# 动态注册所有在 WORKFLOW_SOURCE_DIR 下的 .json 工作流
for wf_path in WORKFLOW_SOURCE_DIR.glob('*.json'):
    fname = wf_path.name
    route = f"/run/{_slugify(fname)}"
    def make_endpoint(file_name):
        def endpoint():
            data = request.get_json(force=True) or {}
            modifications = data.get('modifications', [])
            try:
                wf = load_workflow(file_name)
                wf_mod = apply_modifications(wf, modifications)
                res = submit_to_comfyui(wf_mod)
                return jsonify(res)
            except FileNotFoundError as fe:
                return jsonify({'error': str(fe)}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        endpoint.__name__ = f"run_{_slugify(file_name)}"
        return endpoint
    app.add_url_rule(route, view_func=make_endpoint(fname), methods=['POST'])

# ---------- 主入口 ----------
if __name__ == "__main__":
    # 允许外部访问（Docker / 远程调用）
    app.run(host="0.0.0.0", port=5000, debug=False)
