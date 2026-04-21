# ComfyUI 视频生成 API 服务

## 项目背景与定位

`comfyui_api_service` 是一个 **轻量级 Flask 微服务**，为上层业务（如 OpenClaw 机器人、自动化脚本、前端 UI）提供 **统一的、可直接调用的视频生成接口**。

- **底层**：ComfyUI 是一个强大的可视化工作流引擎，所有实际的图像/视频生成逻辑都封装在一组 JSON 工作流文件中。 
- **目的**：我们不希望每次调用都手动编辑、保存或重新加载这些工作流；而是希望通过一个 HTTP 接口把需要的参数（prompt、图片路径、分辨率、帧数等）直接注入到对应节点，触发一次性生成。
- **优势**：
  - **业务层解耦**：调用方只需发送 JSON 请求，不需要了解 ComfyUI 工作流的内部结构。 
  - **可配置**：所有路径、端口、工作流所在目录均在 `config.json` 中统一管理，迁移或更改时只改配置文件即可。 
  - **多工作流支持**：针对不同业务（文本生成视频、图片生成视频、数字人等）提供 **六条独立的 API**，每条 API 硬编码了对应工作流的关键节点 ID，确保参数注入准确。

## 目录结构
```
comfyui_api_service/
├─ src/                     # 主代码目录
│   └─ app.py               # Flask 入口，包含 6 条独立 API
├─ config.json              # ComfyUI 地址、工作流目录、服务端口等配置
├─ docs/
│   └─ api_endpoints.md     # 详细的 API 文档（请求字段、示例）
├─ requirements.txt         # Python 依赖
├─ .gitignore               # 忽略日志、临时文件
└─ README.md               # 本说明文档（正在阅读的文件）
```

## 配置说明 (`config.json`)
```json
{
  "comfyui_url": "http://127.0.0.1:8188",      // ComfyUI 服务器地址
  "workflow_dir": "./",                        // 若在本项目放置工作流副本的占位目录（默认空）
  "workflow_source_dir": "Z:\\openclaw-projects\\ComfyUI_modpack_V2\\ComfyUI\\user\\default\\workflows\\AIGC蛮子工作流",
  "service_port": 5000                         // Flask 监听端口，默认 5000
}
```
- **`workflow_source_dir`**：实际存放 ComfyUI 工作流 JSON 的目录。若以后迁移，只修改此路径即可，代码无需改动。
- **`workflow_dir`**：可选的本项目内部占位目录（默认 `./`），如果你想把工作流文件放进仓库，可把它们放在这里并将 `workflow_dir` 指向子目录。
- **`service_port`**：Flask 服务监听的端口。Agent、前端或其他服务只需要访问 `http://<host>:<service_port>` 即可。

## 快速启动
```bash
# 1. 克隆仓库（如果尚未克隆）
git clone https://github.com/Hojay-Chen/comfyui-api-service.git
cd comfyui-api-service

# 2. 创建并激活虚拟环境
python -m venv .venv
./.venv/Scripts/activate   # Windows
# 或 source .venv/bin/activate   # Linux/macOS

# 3. 安装依赖
pip install -r requirements.txt

# 4. 如有需要，修改 config.json 中的 workflow_source_dir / service_port

# 5. 启动服务
python -m src.app   # Flask 将在 config 中的 port 监听（默认 5000）
```
服务启动后，API 将可通过 `http://<host>:<port>/api/<name>` 访问。

## API 列表（详见 `docs/api_endpoints.md`）
| 方法 | 路径 | 功能 | 关键节点（示例 ID） |
|------|------|------|-------------------|
| `POST` | `/api/text_to_video` | 文本 → 视频 | 正向提示 254，负向提示 281，分辨率/帧数 250 |
| `POST` | `/api/image_to_video` | 图片 → 视频 | 输入图片 66，正向提示 239，负向提示 266，帧数 235 |
| `POST` | `/api/digital_human` | 数字人生成 | 参考图片 66，提示 239/266，帧数 235 |
| `POST` | `/api/image_to_action` | 图像反推动作迁移 | 姿势提取 360，提示 266 |
| `POST` | `/api/head_tail_video` | 首尾帧控制 | 起始帧 66，结束帧 198，提示 7，帧数 21 |
| `POST` | `/api/action_migration` | 动作迁移（角色） | 源视频 339，目标角色 341，提示 266 |

> **请求体示例**（`/api/text_to_video`）
```json
{
  "prompt": "sunset over mountains",
  "negative_prompt": "blurry",
  "width": 1024,
  "height": 576,
  "frame_count": 24
}
```
响应为 ComfyUI `/prompt` 接口原始返回 JSON，例如 `{"prompt_id":"...","status":"queued"}`。

## 扩展与维护
- **新增工作流**：在 `comfyui_api_service` 中添加对应的工作流文件（或放在外部目录），然后在 `src/app.py` 中新增一个 `@app.route` 处理函数，硬编码该工作流的关键节点 ID。
- **迁移工作流路径**：只需修改 `config.json` 中的 `workflow_source_dir`，不必改代码。
- **日志**：当前仅使用 `print` 输出请求日志，生产环境建议替换为 `logging` 并写入 `logs/`。
- **单元测试**：可在项目根目录创建 `tests/`，使用 `pytest` 调用 Flask 测试客户端验证各接口。

## 许可证
MIT © 2024‑2026 Hojay‑Chen

---
*本项目旨在为 OpenClaw 生态提供即插即用的视频生成能力，保持代码‑配置分离，便于后续迭代与维护。*