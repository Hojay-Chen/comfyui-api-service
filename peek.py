import os, json
workflow_dir = r"Z:\openclaw-projects\ComfyUI_modpack_V2\ComfyUI\user\default\workflows\AIGC蛮子工作流"
files = [
    "AIGC 蛮子 LTX2.3 文生视频FP8.json",
    "AIGC 蛮子 LTX2.3 图像反推动作迁移FP8版.json",
    "AIGC 蛮子 LTX2.3 图生视频FP8 .json",
    "AIGC 蛮子 LTX2.3 数字人工作流FP8.json",
    "AIGC 蛮子 LTX2.3 首尾帧图生视频FP8.json",
    "AIGC 蛮子 LTX2.3 动作迁移.json"
]
for f in files:
    path = os.path.join(workflow_dir, f)
    try:
        with open(path, 'r', encoding='utf-8') as fp:
            content = fp.read(500)
        print(f"=== {f} ===")
        print(repr(content))
        print()
    except Exception as e:
        print(f"Error: {e}")