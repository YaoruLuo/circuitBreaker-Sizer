import os
import yaml

def load_config(yaml_path=None):
    if yaml_path is None:
        # 自动适配同级目录
        base = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(base, "config.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg

# 全局变量
CFG = load_config()
LLM_CFG = CFG["llm"]
UI_CFG = CFG["ui"]
DATA_CFG = CFG["data"]
SESSION_CFG = CFG["session"]
LOG_CFG = CFG["log"]
