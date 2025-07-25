import re
import pandas as pd

def sn_to_pattern(sn):
    """
    序列号格式灵活提取，生成 3WA12H{In}{trip}D/4P + {attach}
    """
    s = sn.replace(" ", "").upper()  # 移除所有空格
    # 匹配主型号前缀、电流、trip（允许_、/、中文）、最后安装方式
    m = re.match(
        r'^(3WA1\d+[A-Z])'               # 1. prefix
        r'(\d+)'                         # 2. 电流
        r'([A-Z0-9_/\u4e00-\u9fa5]*)'    # 3. trip 支持_ / 中文
        r'(D[VF]?/[34]P|F[V]?/[34]P)',   # 4. 安装方式
        s
    )
    if m:
        prefix = m.group(1)
        mount = m.group(4)
        # 始终输出规定格式
        return f"{prefix}{{In}}{{trip}}{mount}+{{attach}}"
    return None


def collect_sn_detail_table(sn_list, product_df, sn_to_pattern_func):
    """
    根据sn_list和产品参数表，返回横向合并的大表和未找到的sn列表
    :param sn_list: list[str]，所有产品序列号
    :param product_df: pd.DataFrame，产品参数表，列名为pattern
    :param sn_to_pattern_func: callable，将sn转为pattern字符串
    :return: merged_df, not_found_list
    """
    detail_dfs = []
    not_found = []
    for sn in sn_list:
        main_pattern = sn_to_pattern_func(sn)
        if main_pattern and main_pattern in product_df.columns:
            detail_df = product_df[[main_pattern]].copy()
            detail_df.columns = [sn]  # 用sn本身做表头
            detail_dfs.append(detail_df)
        else:
            not_found.append(sn)
    if detail_dfs:
        merged_df = pd.concat(detail_dfs, axis=1)
        merged_df.reset_index(inplace=True)
        merged_df.rename(columns={'index': '技术参数'}, inplace=True)
        return merged_df, not_found
    else:
        return None, not_found

# ====== 示例 ======
if __name__ == "__main__":
    print(sn_to_pattern("3WA12H2500 ETU600_LSI/基础电力监测 D/4P"))
    # 输出 3WA12H{In}{trip}D/4P + {attach}

    print(sn_to_pattern("3WA12H2500 ETU600_LSI/电流测量 D/4P"))
    # 输出 3WA11M{In}{trip}D/3P + {attach}

    print(sn_to_pattern("3WA11N800 ETU30_D D/3P"))
    # 输出 3WA11N{In}{trip}D/3P + {attach}
