import json, os, sys
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
            data = json.load(fp)
        nodes = data.get('nodes', [])
        print(f"=== {f} ===")
        print(f"Node count: {len(nodes)}")
        for i, node in enumerate(nodes[:10]):  # first 10 nodes
            nid = node.get('id')
            ntype = node.get('type')
            inputs = node.get('inputs', {})
            outputs = node.get('outputs', {})
            print(f"  [{i}] id={nid}, type={ntype}")
            if inputs:
                print(f"      inputs: {list(inputs.keys())}")
            if outputs:
                print(f"      outputs: {list(outputs.keys())}")
        if len(nodes) > 10:
            print(f"      ... and {len(nodes)-10} more nodes")
        print()
    except Exception as e:
        print(f"Error reading {f}: {e}")