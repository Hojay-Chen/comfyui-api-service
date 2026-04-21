# ComfyUI API Wrapper Service

## 项目简介
本项目提供一个 **Flask** HTTP 服务，针对每个 ComfyUI 工作流提供独立的 RESTful API。每个 API 都硬编码了对应工作流的关键节点 ID，避免使用统一的 `modifications` 方案，从而确保不同工作流的输入字段能准确映射到正确的节点。

## 目录结构
```
comfyui_api_service/
├─ src/
│   └─ app.py            # 主服务入口，包含所有独立的 API 处理函数
├─ config.json           # ComfyUI 地址、工作流目录、服务端口等配置
├─ docs/
│   └─ api_endpoints.md  # API 接口文档（说明请求字段、示例）
├─ requirements.txt      # Python 依赖
├─ .gitignore            # 忽略日志、临时文件等
└─ README.md            # 本说明文件
```

## 快速开始
```bash
# 1. 克隆仓库
git clone https://github.com/Hojay-Chen/comfyui-api-service.git
cd comfyui-api-service

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
./.venv/Scripts/activate  # Windows
# 或 source .venv/bin/activate 在类 Unix 系统上
pip install -r requirements.txt

# 3. 配置项目（编辑 config.json）
#    - comfyui_url: ComfyUI 服务器地址
#    - workflow_source_dir: 实际工作流所在目录
#    - service_port: Flask 监听端口（默认 5000）

# 4. 启动服务
python -m src.app   # Flask 将在 config 中的 port 上监听
```

## API 接口概览
| 方法 | 路径 | 功能描述 | 关键节点（示例 ID） |
|------|------|----------|-------------------|
| POST | `/api/text_to_video` | 文本生成视频 | 正向提示 254，负向提示 281，分辨率/帧数 250 |
| POST | `/api/image_to_video` | 图片生成视频 | 图片输入 66，正向提示 239，负向提示 266，帧数 235 |
| POST | `/api/digital_human` | 数字人生成 | 参考图片 66，提示 239/266，帧数 235 |
| POST | `/api/image_to_action` | 图像反推动作迁移 | 姿势提取 360，提示 266 |
| POST | `/api/head_tail_video` | 首尾帧图生视频 | 起始帧 66，结束帧 198，提示 7，帧数 21 |
| POST | `/api/action_migration` | 动作迁移 | 源视频 339，目标角色 341，提示 266 |

> **注**：节点 ID 基于当前工作流的实际分析，若工作流版本更改，只需在 `src/app.py` 中相应更新 ID 即可。

## 请求示例
```bash
# 文生视频
curl -X POST http://127.0.0.1:5000/api/text_to_video \
     -H "Content-Type: application/json" \
     -d '{"prompt":"sunset over mountains","negative_prompt":"blurry","width":1024,"height":576,"frame_count":24}'
```

其他接口的请求体请参考 `docs/api_endpoints.md` 中的详细说明。

## 常见问题
- **修改了工作流后需要重新启动服务吗？**
  - 是的，节点 ID 发生变化后需要重启服务以加载最新的 JSON。
- **如何查看每个工作流的节点结构？**
  - 项目提供了 `analyze_workflow.py`（已删除）供调试使用，或直接在本地打开对应的 JSON 文件。

## 许可证
MIT © 2024–2026 Hojay-Chen
