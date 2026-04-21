# -*- coding: utf-8 -*-
"""
工作流处理工具函数
"""
import json
from pathlib import Path
from typing import Dict, Any, List
import requests


CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_workflow(fname: str) -> Dict[str, Any]:
    """读取 workflow JSON（只读）"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    workflow_dir = Path(cfg.get("workflow_dir", "./"))
    workflow_source_dir = Path(cfg.get("workflow_source_dir", ""))
    
    # 先查占位目录
    local_path = workflow_dir / fname
    if local_path.is_file():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 再查外部真实目录
    external_path = workflow_source_dir / fname
    if external_path.is_file():
        with open(external_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Workflow file not found: {fname}")


def apply_modifications(workflow: Dict[str, Any], mods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """在内存中修改 workflow"""
    nodes = workflow.get("nodes", [])
    
    for mod in mods:
        node_id = mod.get("node")
        field = mod.get("field")
        value = mod.get("value")
        
        if not (node_id and field):
            continue
        
        for n in nodes:
            if n.get("id") == node_id:
                # 优先修改 outputs，其次 inputs
                if "outputs" in n and field in n["outputs"]:
                    n["outputs"][field] = value
                elif "inputs" in n and field in n["inputs"]:
                    n["inputs"][field] = value
                else:
                    n.setdefault("outputs", {})[field] = value
                break
    
    return workflow


def submit_to_comfyui(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """提交工作流到 ComfyUI /prompt"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    comfyui_url = cfg.get("comfyui_url", "http://127.0.0.1:8188")
    endpoint = f"{comfyui_url.rstrip('/')}/prompt"
    
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