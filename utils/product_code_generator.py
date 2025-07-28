import re

def split_value_unit(val):
    if isinstance(val, (int, float)):
        return val, None
    if isinstance(val, str):
        match = re.match(r"^\s*(\d+\.?\d*)\s*([a-zA-Z\u4e00-\u9fa5]+)?\s*$", val)
        if match:
            value = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
            unit = match.group(2)
            return value, unit
    return val, None

def get_all_frame_levels(current):
    levels = []
    if 630 <= current <= 2500:
        levels.append(1)
    if 2000 <= current <= 4000:
        levels.append(2)
    if 4000 <= current <= 6300:
        levels.append(3)
    return levels

def get_pole_candidates(pole, unit=None):
    """极数可能为None时，返回全部常规极数"""
    poles = []
    if pole is None:
        # 通常只考虑3P/4P，如有2P/1P可自行扩展
        poles = ["3P", "4P"]
    else:
        # 兼容数字和"3P"
        if isinstance(pole, str) and pole.upper().endswith("P"):
            poles = [pole.upper()]
        else:
            poles = [f"{int(pole)}P"]
    return poles

def normalize_mount_str_expand(mount):
    """
    输入如 '水平安装'、'垂直安装'、'抽屉式安装'、'固定式安装'，自动扩展为所有可行组合
    返回标准list: ["抽屉式水平安装", ...]
    """
    if not isinstance(mount, str) or not mount.strip():
        # 为空/None时返回全部四种
        return ["抽屉式水平安装", "抽屉式垂直安装", "固定式水平安装", "固定式垂直安装"]
    m = mount.replace(" ", "")
    # 完全标准的直接返回
    standard = ["抽屉式水平安装", "抽屉式垂直安装", "固定式水平安装", "固定式垂直安装"]
    if m in standard:
        return [m]
    # 只说了水平/垂直
    if "水平" in m and "垂直" not in m:
        return ["抽屉式水平安装", "固定式水平安装"]
    if "垂直" in m and "水平" not in m:
        return ["抽屉式垂直安装", "固定式垂直安装"]
    # 只说了抽屉/固定
    if "抽屉" in m and "固定" not in m:
        return ["抽屉式水平安装", "抽屉式垂直安装"]
    if "固定" in m and "抽屉" not in m:
        return ["固定式水平安装", "固定式垂直安装"]
    # 其它兜底返回全部
    return ["抽屉式水平安装", "抽屉式垂直安装", "固定式水平安装", "固定式垂直安装"]

# 对应修改 get_mount_codes，接受 list 传入
def get_mount_codes(mounts):
    """mounts: list of标准名称，返回所有标准代码"""
    standard_map = {
        "抽屉式水平安装": "D",
        "抽屉式垂直安装": "DV",
        "固定式水平安装": "F",
        "固定式垂直安装": "FV",
    }
    if not isinstance(mounts, list):
        mounts = [mounts]
    codes = [standard_map[m] for m in mounts if m in standard_map]
    # 兜底：如果没有任何合法项，返回所有
    return codes if codes else list(standard_map.values())


CURRENT_TABLE = {
    1: [630, 800, 1000, 1250, 1600, 2000, 2500],
    2: [2000, 2500, 3200, 4000],
    3: [4000, 5000, 6300],
}

def get_part_number(level, current):
    currents = CURRENT_TABLE.get(level, [])
    for c in currents:
        if current <= c:
            return c
    if currents:
        return currents[-1]
    return None

def get_breaking_options(level, min_breaking=None):
    """如min_breaking为None，则返回所有标准分断能力"""
    table = {
        1: [('N', 55), ('S', 66), ('M', 85)],
        2: [('S', 66), ('M', 85), ('H', 100), ('C', 130)],
        3: [('H', 100), ('C', 150), ('C', 130)],
    }
    options = table.get(level, [])
    if min_breaking is None:
        return options
    return [(code, value) for code, value in options if value >= min_breaking]

def select_all_breaker_models(params: dict):
    current, _ = split_value_unit(params.get("额定电流"))
    pole, pole_unit = split_value_unit(params.get("极数"))
    # mount = params.get("安装方式", None)
    min_breaking, _ = split_value_unit(params.get("分断能力"))
    trip = params.get("推荐脱扣器")

    if current is None:
        return ["关键信息缺失：额定电流必须指定"]

    levels = get_all_frame_levels(current)
    if not levels:
        return [f"额定电流{current}A不在支持范围"]

    pole_candidates = get_pole_candidates(pole, pole_unit)
    mount_list = normalize_mount_str_expand(params.get("安装方式"))
    mount_codes = get_mount_codes(mount_list)
    results = []

    prefix = "3WA1"

    for frame_level in levels:
        part_number = get_part_number(frame_level, current)
        breaking_options = get_breaking_options(frame_level, min_breaking if min_breaking is not None else None)
        for breaking_code, breaking_value in breaking_options:
            for mount_code in mount_codes:
                # --- 排除不支持的组合 ---
                # 1. 抽屉式水平端D的物理限制
                if (mount_code == "D" and
                        ((frame_level == 1 and part_number == 2500) or
                         (frame_level == 2 and part_number == 4000) or
                         (frame_level == 3 and part_number == 6300))):
                    continue
                # 2. 固定式水平端F的物理限制
                if (mount_code == "F" and
                        ((frame_level == 2 and part_number == 4000) or
                         (frame_level == 3 and part_number == 6300))):
                    continue
                for pole_str in pole_candidates:
                    model = f"{prefix}{frame_level}{breaking_code}{part_number} {trip} {mount_code}/{pole_str}"
                    results.append(model)
    return results if results else ["无满足条件的型号"]


# ========== 示例 ==========
if __name__ == "__main__":
    # 示例1：极数、分断能力均为None，自动枚举所有
    params_list = [
        {
            "额定电流": 2000,
            "极数": 3,
            "安装方式": "抽屉式水平安装",
            "分断能力": 66,
            "推荐脱扣器": "ETU600_LSI/电流测量可通讯"
        }
    ]
    for params in params_list:
        print("输入参数：", params)
        models = select_all_breaker_models(params)
        print("满足条件的型号：")
        for m in models:
            print(m)
        print("="*50)
