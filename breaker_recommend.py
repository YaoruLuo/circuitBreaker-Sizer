import ast
import re

import ast
import re

CORE_KEYS = ["额定电流", "极数", "分断能力", "安装类型", "安装方向"]

def extract_breaker_info_from_output(text):
    candidates = re.findall(r'\{[\s\S]*?\}', text)
    for c in candidates:
        try:
            d = ast.literal_eval(c)
            if isinstance(d, dict):
                # 兼容嵌套字典
                if len(d) == 1 and isinstance(list(d.values())[0], dict):
                    d = list(d.values())[0]
                # 取出原始字段
                filtered = {k: d.get(k, None) for k in CORE_KEYS}
                # 组合安装方式
                install_type = filtered.pop("安装类型", None)
                install_dir = filtered.pop("安装方向", None)
                if install_type and install_dir:
                    install = f"{install_type}{install_dir}安装"
                elif install_type:
                    install = f"{install_type}安装"
                elif install_dir:
                    install = f"{install_dir}安装"
                else:
                    install = None

                # 构造返回，None的自动省略
                result = {}
                for k in ["额定电流", "极数", "分断能力"]:
                    if filtered.get(k) is not None:
                        result[k] = filtered[k]
                if install is not None:
                    result["安装方式"] = install

                if result:  # 至少有一个字段有效
                    return result
        except Exception:
            continue
    return {"解析失败": "未找到标准Python字典", "原始内容": text}


