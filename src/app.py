#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ComfyUI API Wrapper - 每个工作流单独处理逻辑（硬编码节点 ID）
"""

import json
from pathlib import Path
from typing import Dict, Any

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------- 配置 ----------
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

COMFYUI_URL = cfg.get("comfyui_url", "http://127.0.0.1:8188")
SERVICE_PORT = cfg.get("service_port", 5000)
WORKFLOW_DIR = Path(cfg.get("workflow_dir", "./"))
WORKFLOW_SOURCE_DIR = Path(cfg.get("workflow_source_dir", ""))

# ---------- 工具函数 ----------
def load_workflow(filename: str) -> Dict:
    """加载工作流 JSON"""
    local = WORKFLOW_DIR / filename
    if local.is_file():
        with open(local, "r", encoding="utf-8") as f:
            return json.load(f)
    external = WORKFLOW_SOURCE_DIR / filename
    if external.is_file():
        with open(external, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"Workflow not found: {filename}")

def submit_to_comfyui(workflow: Dict) -> Dict:
    """提交到 ComfyUI /prompt"""
    endpoint = f"{COMFYUI_URL.rstrip('/')}/prompt"
    try:
        resp = requests.post(
            endpoint,
            json=workflow,
            headers={"Content-Type": "application/json"},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def set_node_input(workflow: Dict, node_id, field: str, value):
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            inputs = node.get("inputs", {})
            if isinstance(inputs, dict):
                inputs[field] = value
            return

def set_node_output(workflow: Dict, node_id, field: str, value):
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            outputs = node.get("outputs", {})
            if isinstance(outputs, dict):
                outputs[field] = value
            return

# ---------------------------------------------------------------------------
# API 1: 文生视频 /api/text_to_video
# 工作流: AIGC 蛮子 LTX2.3 文生视频FP8.json
# 关键节点: CLIPTextEncode 正向 (254), 负向 (281), EmptyLTXVLatentVideo (250)
# ---------------------------------------------------------------------------
@app.route("/api/text_to_video", methods=["POST"])
def text_to_video():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 文生视频FP8.json")
        if "prompt" in data:
            set_node_input(wf, 254, "text", data["prompt"])
        if "negative_prompt" in data:
            set_node_input(wf, 281, "text", data["negative_prompt"])
        if "width" in data:
            set_node_input(wf, 250, "width", data["width"])
        if "height" in data:
            set_node_input(wf, 250, "height", data["height"])
        if "frame_count" in data:
            set_node_input(wf, 250, "length", data["frame_count"])
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API 2: 图生视频 /api/image_to_video
# 工作流: AIGC 蛮子 LTX2.3 图生视频FP8 .json
# 关键节点: LoadImage (66), CLIPTextEncode 正向 (239), 负向 (266), EmptyLTXVLatentVideo (235)
# ---------------------------------------------------------------------------
@app.route("/api/image_to_video", methods=["POST"])
def image_to_video():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 图生视频FP8 .json")
        if "image" in data:
            set_node_input(wf, 66, "image", data["image"])
        if "prompt" in data:
            set_node_input(wf, 239, "text", data["prompt"])
        if "negative_prompt" in data:
            set_node_input(wf, 266, "text", data["negative_prompt"])
        if "frame_count" in data:
            set_node_input(wf, 235, "length", data["frame_count"])
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API 3: 数字人 /api/digital_human
# 工作流: AIGC 蛮子 LTX2.3 数字人工作流FP8.json
# 关键节点: LoadImage (66), CLIPTextEncode 正向 (239), 负向 (266), EmptyLTXVLatentVideo (235)
# ---------------------------------------------------------------------------
@app.route("/api/digital_human", methods=["POST"])
def digital_human():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 数字人工作流FP8.json")
        if "reference_image" in data:
            set_node_input(wf, 66, "image", data["reference_image"])
        if "prompt" in data:
            set_node_input(wf, 239, "text", data["prompt"])
        if "negative_prompt" in data:
            set_node_input(wf, 266, "text", data["negative_prompt"])
        if "frame_count" in data:
            set_node_input(wf, 235, "length", data["frame_count"])
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API 4: 图像反推动作迁移 /api/image_to_action
# 工作流: AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json
# 关键节点: SDPoseKeypointExtractor (360), CLIPTextEncode (266) – 示例占位
# ---------------------------------------------------------------------------
@app.route("/api/image_to_action", methods=["POST"])
def image_to_action():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json")
        if "source_image" in data:
            set_node_input(wf, 360, "image", data["source_image"])
        if "prompt" in data:
            set_node_input(wf, 266, "text", data["prompt"])
        if "strength" in data:
            set_node_input(wf, 360, "strength", data["strength"])  # 示例字段
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API 5: 首尾帧图生视频 /api/head_tail_video
# 工作流: AIGC 蛮子 LTX2.3 首尾帧图生视频FP8.json
# 关键节点: LoadImage (66) 起始帧, LoadImage (198) 结束帧, CLIPTextEncode (7) 提示, EmptyLTXVLatentVideo (21) 帧数
# ---------------------------------------------------------------------------
@app.route("/api/head_tail_video", methods=["POST"])
def head_tail_video():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 首尾帧图生视频FP8.json")
        if "first_frame" in data:
            set_node_input(wf, 66, "image", data["first_frame"])
        if "last_frame" in data:
            set_node_input(wf, 198, "image", data["last_frame"])
        if "prompt" in data:
            set_node_input(wf, 7, "text", data["prompt"])
        if "frame_count" in data:
            set_node_input(wf, 21, "length", data["frame_count"])
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# API 6: 动作迁移 /api/action_migration
# 工作流: AIGC 蛮子 LTX2.3 动作迁移.json
# 关键节点: LoadImage (339) 源视频, LoadImage (339?) 目标角色, CLIPTextEncode (266) 提示 – 仅示例占位
# ---------------------------------------------------------------------------
@app.route("/api/action_migration", methods=["POST"])
def action_migration():
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 动作迁移.json")
        if "source_video" in data:
            set_node_input(wf, 339, "video", data["source_video"])  # 示例字段
        if "target_character" in data:
            set_node_input(wf, 341, "image", data["target_character"])  # 示例字段
        if "prompt" in data:
            set_node_input(wf, 266, "text", data["prompt"])
        return jsonify(submit_to_comfyui(wf))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=False)
