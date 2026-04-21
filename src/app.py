#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ComfyUI API Wrapper - 每个工作流单独写处理逻辑
基于实际分析的 workflow JSON 结构，硬编码每个 API 的节点修改逻辑
"""

import json
from pathlib import Path
from typing import Dict, Any, List

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
    # 先查占位目录
    local = WORKFLOW_DIR / filename
    if local.is_file():
        with open(local, "r", encoding="utf-8") as f:
            return json.load(f)
    # 再查外部真实目录
    external = WORKFLOW_SOURCE_DIR / filename
    if external.is_file():
        with open(external, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"Workflow not found: {filename}")

def submit_to_comfyui(workflow: Dict) -> Dict:
    """提交到 ComfyUI"""
    endpoint = f"{COMFYUI_URL.rstrip('/')}/prompt"
    try:
        resp = requests.post(
            endpoint,
            json=workflow,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def set_node_input(workflow: Dict, node_id, field: str, value):
    """修改指定节点的 input 字段"""
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            inputs = node.get("inputs", {})
            if isinstance(inputs, dict):
                inputs[field] = value
            return

def set_node_output(workflow: Dict, node_id, field: str, value):
    """修改指定节点的 output 字段"""
    for node in workflow.get("nodes", []):
        if node.get("id") == node_id:
            outputs = node.get("outputs", {})
            if isinstance(outputs, dict):
                outputs[field] = value
            return

# ============================================================================
# API 1: 文生视频 /api/text_to_video
# 工作流: AIGC 蛮子 LTX2.3 文生视频FP8.json
# 关键节点分析:
#   - CLIPTextEncode 节点 254: 正向提示词
#   - CLIPTextEncode 节点 281: 负向提示词
#   - EmptyLTXVLatentVideo 节点 250: 分辨率、时长、帧数
# ============================================================================
@app.route("/api/text_to_video", methods=["POST"])
def handle_text_to_video():
    """
    文生视频 API
    请求体: {
        "prompt": "sunset over mountains",
        "negative_prompt": "blurry, low quality",
        "width": 1024,
        "height": 576,
        "frame_count": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 文生视频FP8.json")
        
        # 修改正向提示词 (节点 254)
        if "prompt" in data:
            set_node_input(wf, 254, "text", data["prompt"])
        
        # 修改负向提示词 (节点 281)
        if "negative_prompt" in data:
            set_node_input(wf, 281, "text", data["negative_prompt"])
        
        # 修改 EmptyLTXVLatentVideo 节点 250 的参数
        if "width" in data:
            set_node_input(wf, 250, "width", data["width"])
        if "height" in data:
            set_node_input(wf, 250, "height", data["height"])
        if "frame_count" in data:
            set_node_input(wf, 250, "length", data["frame_count"])
        
        result = submit_to_comfyui(wf)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API 2: 图生视频 /api/image_to_video
# 工作流: AIGC 蛮子 LTX2.3 图生视频FP8 .json
# 关键节点分析:
#   - LoadImage 节点 66: 输入图片
#   - CLIPTextEncode 节点 239: 正向提示词
#   - CLIPTextEncode 节点 266: 负向提示词
#   - EmptyLTXVLatentVideo 节点 235: 视频参数
# ============================================================================
@app.route("/api/image_to_video", methods=["POST"])
def handle_image_to_video():
    """
    图生视频 API
    请求体: {
        "image": "/path/to/image.png" 或 base64,
        "prompt": "make it move naturally",
        "negative_prompt": "distorted",
        "frame_count": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 图生视频FP8 .json")
        
        # 修改 LoadImage 节点 66 的图片路径
        if "image" in data:
            set_node_input(wf, 66, "image", data["image"])
        
        # 修改正向提示词 (节点 239)
        if "prompt" in data:
            set_node_input(wf, 239, "text", data["prompt"])
        
        # 修改负向提示词 (节点 266)
        if "negative_prompt" in data:
            set_node_input(wf, 266, "text", data["negative_prompt"])
        
        # 修改视频参数
        if "frame_count" in data:
            set_node_input(wf, 235, "length", data["frame_count"])
        
        result = submit_to_comfyui(wf)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API 3: 数字人 /api/digital_human
# 工作流: AIGC 蛮子 LTX2.3 数字人工作流FP8.json
# 关键节点分析:
#   - LoadImage 节点 66: 参考图片
#   - CLIPTextEncode 节点 239: 正向提示词
#   - CLIPTextEncode 节点 266: 负向提示词
# ============================================================================
@app.route("/api/digital_human", methods=["POST"])
def handle_digital_human():
    """
    数字人生成 API
    请求体: {
        "reference_image": "/path/to/face.png",
        "prompt": "talking head, realistic",
        "negative_prompt": "distorted face",
        "frame_count": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 数字人工作流FP8.json")
        
        # 修改 LoadImage 节点 66 的参考图片
        if "reference_image" in data:
            set_node_input(wf, 66, "image", data["reference_image"])
        
        # 修改正向提示词 (节点 239)
        if "prompt" in data:
            set_node_input(wf, 239, "text", data["prompt"])
        
        # 修改负向提示词 (节点 266)
        if "negative_prompt" in data:
            set_node_input(wf, 266, "text", data["negative_prompt"])
        
        # 修改视频长度
        if "frame_count" in data:
            set_node_input(wf, 235, "length", data["frame_count"])
        
        result = submit_to_comfyui(wf)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API 4: 图像反推动作迁移 /api/image_to_action
# 工作流: AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json
# 关键节点分析:
#   - SDPoseKeypointExtractor 节点 360: 姿势提取
#   - CLIPTextEncode 节点 266: 提示词
# ============================================================================
@app.route("/api/image_to_action", methods=["POST"])
def handle_image_to_action():
    """
    图像反推动作迁移 API
    请求体: {
        "source_image": "/path/to/person.png",
        "prompt": "extract pose and apply",
        "strength": 0.8
    }
    """
    try:
        data = request.get_json(force=True) or {}
        wf = load_workflow("AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json")
        
        # 这个工作流比较复杂，需要根据实际节点填写
        # SDPoseKeypointExtractor 节点 360
        if "source_image" in data:
            set_node_input(wf, 360, "image", data["source_image"])
        
