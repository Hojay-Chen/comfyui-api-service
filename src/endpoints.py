# -*- coding: utf-8 -*-
"""
每个工作流的独立 API 处理逻辑
每个函数对应一个具体的工作流，硬编码该工作流的节点修改逻辑
"""
from flask import request, jsonify
from typing import Dict, Any
from .workflow import load_workflow, apply_modifications, submit_to_comfyui


def handle_text_to_video() -> Dict[str, Any]:
    """
    文生视频 API
    POST /api/text_to_video
    
    请求体: {
        "prompt": "sunset over mountains",        # 正向提示词 (节点id需根据实际workflow确定)
        "negative_prompt": " blurry, low quality", # 负向提示词
        "width": 1024,
        "height": 576,
        "duration": 24,
        "fps": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        # 加载工作流
        wf = load_workflow("AIGC 蛮子 LTX2.3 文生视频FP8.json")
        
        # 该工作流的具体修改逻辑
        modifications = []
        
        # TODO: 需要根据实际workflow JSON确定正确的节点ID和字段名
        # 这里假设提示词节点id为 "1"，字段为 "text"
        if "prompt" in data:
            modifications.append({"node": "1", "field": "text", "value": data["prompt"]})
        
        if "negative_prompt" in data:
            modifications.append({"node": "2", "field": "text", "value": data["negative_prompt"]})
        
        # 分辨率设置 (假设节点id为 "3")
        if "width" in data:
            modifications.append({"node": "3", "field": "width", "value": data["width"]})
        if "height" in data:
            modifications.append({"node": "3", "field": "height", "value": data["height"]})
        
        # 时长和帧率 (假设节点id为 "4")
        if "duration" in data:
            modifications.append({"node": "4", "field": "duration", "value": data["duration"]})
        if "fps" in data:
            modifications.append({"node": "4", "field": "fps", "value": data["fps"]})
        
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_image_to_video() -> Dict[str, Any]:
    """
    图生视频 API
    POST /api/image_to_video
    
    请求体: {
        "image": "base64_encoded_image_or_path",  # 输入图片
        "prompt": "make it move",
        "strength": 0.7,
        "duration": 12
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        wf = load_workflow("AIGC 蛮子 LTX2.3 图生视频FP8 .json")
        
        modifications = []
        
        # 图片输入节点 (假设id为 "10")
        if "image" in data:
            modifications.append({"node": "10", "field": "image", "value": data["image"]})
        
        # 提示词节点 (假设id为 "11")
        if "prompt" in data:
            modifications.append({"node": "11", "field": "text", "value": data["prompt"]})
        
        # 强度参数 (假设id为 "12")
        if "strength" in data:
            modifications.append({"node": "12", "field": "strength", "value": data["strength"]})
        
        if "duration" in data:
            modifications.append({"node": "13", "field": "duration", "value": data["duration"]})
        
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_digital_human() -> Dict[str, Any]:
    """
    数字人 API
    POST /api/digital_human
    
    请求体: {
        "prompt": "talking head animation",
        "reference_image": "base64_or_path",
        "style": "anime",
        "duration": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        wf = load_workflow("AIGC 蛮子 LTX2.3 数字人工作流FP8.json")
        
        modifications = []
        
        if "prompt" in data:
            modifications.append({"node": "20", "field": "text", "value": data["prompt"]})
        
        if "reference_image" in data:
            modifications.append({"node": "21", "field": "image", "value": data["reference_image"]})
        
        if "style" in data:
            modifications.append({"node": "22", "field": "style", "value": data["style"]})
        
        if "duration" in data:
            modifications.append({"node": "23", "field": "duration", "value": data["duration"]})
        
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_image_to_action() -> Dict[str, Any]:
    """
    图像反推动作迁移 API
    POST /api/image_to_action
    
    请求体: {
        "source_image": "base64_or_path",      # 源图
        "target_pose": "base64_or_path",       # 目标姿势
        "strength": 0.8
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        wf = load_workflow("AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json")
        
        modifications = []
        
        if "source_image" in data:
            modifications.append({"node": "30", "field": "image", "value": data["source_image"]})
        
        if "target_pose" in data:
            modifications.append({"node": "31", "field": "image", "value": data["target_pose"]})
        
        if "strength" in data:
            modifications.append({"node": "32", "field": "strength", "value": data["strength"]})
        
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_head_tail_video() -> Dict[str, Any]:
    """
    首尾帧图生视频 API
    POST /api/head_tail_video
    
    请求体: {
        "first_frame": "base64_or_path",    # 起始帧
        "last_frame": "base64_or_path",     # 结束帧
        "prompt": "transition from frame1 to frame2",
        "duration": 24
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        wf = load_workflow("AIGC 蛮子 LTX2.3 首尾帧图生视频FP8.json")
        
        modifications = []
        
        if "first_frame" in data:
            modifications.append({"node": "40", "field": "image", "value": data["first_frame"]})
        
        if "last_frame" in data:
            modifications.append({"node": "41", "field": "image", "value": data["last_frame"]})
        
        if "prompt" in data:
            modifications.append({"node": "42", "field": "text", "value": data["prompt"]})
        
        if "duration" in data:
            modifications.append({"node": "43", "field": "duration", "value": data["duration"]})
        
        wf_modified = apply_modifications(wf, modifications)
        result = submit_to_comfyui(wf_modified)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_action_migration() -> Dict[str, Any]:
    """
    动作迁移 API
    POST /api/action_migration
    
    请求体: {
        "source_video": "base64_or_path",
        "target_character": "base64_or_path",
        "prompt": "apply action from source to target"
    }
    """
    try:
        data = request.get_json(force=True) or {}
        
        wf = load_workflow("AIGC 蛮子 LTX2.3 动作迁移.json")
        
        modifications = []
        
        if "source_video" in data:
            modifications.append({"node": "50