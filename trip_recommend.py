import pandas as pd
import re

def get_function_fields(trip_df, model_col="型号"):
    # 获取所有功能字段，排除“型号”“备注”等
    exclude_cols = [model_col, "备注", "额定电流"]
    func_fields = [col for col in trip_df.columns if col not in exclude_cols]
    return func_fields

def normalize_need_dict(llm_need, func_fields):
    # 只保留表头有的功能字段，且保证都是bool类型
    return {k: bool(llm_need.get(k, False)) for k in func_fields}

def filter_trip_units_strict(trip_df, need, model_col="型号"):
    """
    严格按需求过滤
    """
    df = trip_df.copy()
    for col, required in need.items():
        if required and col in df.columns:
            df = df[df[col].astype(str).str.upper().isin(['Y', 'TRUE', '是', '1'])]
    return df

def select_minimal_trip_model_strict(filtered_df, model_col="型号"):
    """
    选功能最少（Y最少）的型号，如相同按型号升序
    """
    if filtered_df.empty:
        return None, None
    # 功能字段
    func_cols = [c for c in filtered_df.columns if c not in [model_col, "备注", "额定电流"]]
    filtered_df = filtered_df.copy()
    filtered_df['功能数量'] = filtered_df[func_cols].apply(
        lambda x: sum(1 for v in x if str(v).upper() in ['Y', 'TRUE', '是', '1']), axis=1
    )
    filtered_df = filtered_df.sort_values(by=['功能数量', model_col])
    row = filtered_df.iloc[0]
    return row[model_col], row.to_dict()

def load_trip_df_with_transpose(excel_file):
    """
    excel_file: 上传的Excel file-like对象
    返回: 标准化（型号为行，功能为列，型号列名为'型号'）的DataFrame
    """
    # 读取原始横表
    raw_df = pd.read_excel(excel_file, header=None)
    # 第一行：型号名（从第2列开始），第一列：功能名（从第2行开始）
    feature_names = raw_df.iloc[1:, 0].tolist()
    model_names = raw_df.iloc[0, 1:].tolist()
    # 提取功能-型号矩阵
    data_matrix = raw_df.iloc[1:, 1:]
    data_matrix.index = feature_names
    data_matrix.columns = model_names
    # 转置：型号为行，功能为列
    trip_df = data_matrix.T.reset_index()
    trip_df.rename(columns={"index": "型号"}, inplace=True)
    return trip_df

def extract_trip_info_from_output(output, func_fields):
    """
    从LLM输出的伪JSON字符串中提取字典，支持每行有逗号、缺失大括号等情况。
    只返回func_fields里定义的字段。
    """
    output = output.strip()
    # 去掉 ```json 或 ``` 前缀
    output = re.sub(r"^```[a-zA-Z]*\s*", "", output)
    output = re.sub(r"\s*```$", "", output)
    # 提取大括号内内容（如果有）
    m = re.search(r"\{(.*)\}", output, re.DOTALL)
    if m:
        content = m.group(1)
    else:
        content = output
    # 正则找所有 key-value
    kv_pairs = re.findall(r'"([^"]+)"\s*:\s*(true|false)', content)
    # 只保留 func_fields 中的 key，严格按顺序
    func_set = set(f.strip() for f in func_fields)
    result = {k.strip(): (v == 'true') for k, v in kv_pairs if k.strip() in func_set}
    normalized = {}
    for k in func_fields:
        normalized[k] = result.get(k.strip(), False)
    return normalized
