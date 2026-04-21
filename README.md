# ComfyUI API Wrapper Service

## 项目简介
本项目提供一个轻量级的 **Python Flask**（或 FastAPI） HTTP API，帮助上层视频助手直接调用 **ComfyUI** 工作流，而不需要手动编辑完整的 workflow JSON。 

- 读取预定义的 workflow JSON（只读 ComfyUI 资源）
- 接收请求体中的 **input 参数**（prompt、duration、fps 等）
- 在内存中根据节点名称/ID 动态修改对应节点属性
- 将完整的 workflow JSON 通过 ComfyUI 原始 API (`/prompt`) 发送，触发生成

## 目录结构
```
comfyui_api_service/
├─ app.py                # 主服务入口（Flask）
├─ config.json           # ComfyUI 主机 & 端口配置
├─ workflow_template.json# 示例工作流模板（只读）
├─ requirements.txt      # 依赖列表
├─ .gitignore            # 过滤日志、临时文件
└─ README.md
```

## 使用方式
```bash
# 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 运行服务（默认 0.0.0.0:5000）
python app.py
```

## API 接口
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/run` | 读取 workflow 模板，按请求体中的 `modifications` 动态更新节点字段并调用 ComfyUI。

### 请求示例
```json
{
  "workflow": "workflow_template.json",   // 模板文件名（相对 service 根目录）
  "modifications": [
    {"node": "PromptNode", "field": "prompt", "value": "sunset over mountains"},
    {"node": "VideoSettings", "field": "duration", "value": 10},
    {"node": "VideoSettings", "field": "fps", "value": 30}
  ]
}
```

## 注意事项
- **不修改 ComfyUI 源码**，仅读取 workflow JSON 并在内存中拼装后发送。
- 若同一次请求多次调用，请求体中 `modifications` 只影响当前内存实例，不会写回磁盘。
- 需要在 `config.json` 中配置 ComfyUI 的地址（如 `http://127.0.0.1:8188`）。

---
*通过本项目，你的视频助手 Agent 能以 RESTful 方式直接控制 ComfyUI 工作流，提升可用性与自动化程度。*