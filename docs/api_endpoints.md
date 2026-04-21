# ComfyUI API Wrapper – 接口清单（业务 API 名称）

> 所有接口均为 **POST**。请求体只需要 `modifications`（可选），不再需要提供工作流文件名。

## 已声明的业务 API（由 config.api_map 自动生成）

| 业务 API 名称 | 对应工作流文件（中文） | 访问路径 |
|---------------|------------------------|----------|
| `text_to_video`      | AIGC 蛮子 LTX2.3 文生视频FP8.json | `POST /api/text_to_video` |
| `image_to_action`    | AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json | `POST /api/image_to_action` |
| `image_to_video`     | AIGC 蛮子 LTX2.3 图生视频FP8 .json | `POST /api/image_to_video` |
| `digital_human`      | AIGC 蛮子 LTX2.3 数字人工作流FP8.json | `POST /api/digital_human` |
| `head_tail_video`    | AIGC 蛮子 LTX2.3 首尾帧图生视频FP8.json | `POST /api/head_tail_video` |
| `action_migration`   | AIGC 蛮子 LTX2.3 动作迁移.json | `POST /api/action_migration` |

## 通用请求体（可选 `modifications`）

```json
{
  "modifications": [
    {"node":"PromptNode","field":"prompt","value":"sunset over mountains"},
    {"node":"VideoSettings","field":"duration","value":12},
    {"node":"VideoSettings","field":"fps":30}
  ]
}
```

- **如果不需要修改任何字段**，只需发送空对象 `{}` 或省略 `modifications`。

## 示例调用（使用 `curl`）

```bash
curl -X POST http://127.0.0.1:5000/api/text_to_video \
     -H "Content-Type: application/json" \
     -d '{"modifications":[{"node":"PromptNode","field":"prompt","value":"sunset over mountains"}]}'
```

## 成功返回示例

```json
{
  "prompt_id": "e5a7b3c2-1234-5678-90ab-cdef12345678",
  "status": "queued"
}
```

## 错误返回示例

- **文件未找到（404）**

```json
{
  "error": "Workflow file not found in either ./ or Z:\\...\\AIGC蛮子工作流: unknown.json"
}
```

- **内部错误（500）**

```json
{
  "error": "KeyError: 'PromptNode' not found in workflow"
}
```

---

### 使用说明

1. **启动服务**（项目根目录）  
   ```bash
   python -m venv .venv
   .\\.venv\\Scripts\\activate
   pip install -r requirements.txt
   python -m src.app   # Flask 将在 config 中指定的端口监听
   ```

2. **调用任意工作流**：使用上表对应的 URL，发送 JSON（可带或不带 `modifications`）。  

3. **增删工作流**：只要把对应的 `.json` 文件放入或移出 `workflow_source_dir`，**重启服务**后路由会自动刷新，无需改代码。
