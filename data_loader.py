import json
import pandas as pd
import streamlit as st

@st.cache_data
def load_product_df(path: str) -> pd.DataFrame:
    """
    加载产品参数 Excel，默认使用第一列为索引。
    使用 Streamlit 缓存加快页面响应速度。
    """
    return pd.read_excel(path, header=0, index_col=0)


@st.cache_resource
def load_sn_order_map(path: str) -> dict:
    """
    加载订货号映射字典，来源为 JSON 文件。
    使用 Streamlit 缓存避免重复读取。
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载订货号映射失败: {e}")
        return {}
