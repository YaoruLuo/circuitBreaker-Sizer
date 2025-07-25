from config.config import LLM_CFG, SESSION_CFG, LOG_CFG
from utils.prompt_template import PROMPT_TEMPLATE_ZH
from utils.llm_client import llm_chat_stream
from utils.product_code_generator import select_all_breaker_models
from utils.log_utils import write_llm_log
from utils.search_product_info import sn_to_pattern, collect_sn_detail_table
from breaker_recommend import extract_breaker_info_from_output
from trip_recommend import (
    get_function_fields, normalize_need_dict,
    filter_trip_units_strict, select_minimal_trip_model_strict,
    extract_trip_info_from_output
)
import streamlit as st
import pandas as pd

def run_chat_pipeline(user_input: str, trip_df: pd.DataFrame, sn_order_map: dict, product_df: pd.DataFrame):
    """主聊天处理流程"""
    PARSE_BREAKER_TEMPLATE = PROMPT_TEMPLATE_ZH["PARSE_BREAKER_TEMPLATE"]
    PARSE_TRIP_TEMPLATE = PROMPT_TEMPLATE_ZH["PARSE_TRIP_TEMPLATE"]

    # ===== 1. 结构化断路器解析 =====
    breaker_box = st.empty()
    reply_breaker = ""
    for partial in llm_chat_stream(
        user_input, PARSE_BREAKER_TEMPLATE,
        LLM_CFG["model_name"], LLM_CFG["xinference_url"], max_tokens=LLM_CFG["max_tokens_breaker"]):
        reply_breaker = partial
        breaker_box.markdown("正在解析断路器需求...")
    breaker_box.markdown("")
    result_breaker = extract_breaker_info_from_output(reply_breaker)

    # ===== 2. 脱扣器解析 =====
    result_trip = {}
    trip_box = st.empty()
    reply_trip = ""
    if trip_df is not None:
        func_fields = get_function_fields(trip_df, model_col="型号")
        trip_prompt = PARSE_TRIP_TEMPLATE.format(func_fields="\n".join(func_fields), question=user_input)
        for partial in llm_chat_stream(
            user_input, trip_prompt, LLM_CFG["model_name"], LLM_CFG["xinference_url"], max_tokens=LLM_CFG["max_tokens_trip"]):
            reply_trip = partial
            trip_box.markdown("正在查找合适的脱扣器型号...")
        trip_box.markdown("")
        result_trip = extract_trip_info_from_output(reply_trip, func_fields)

        need = normalize_need_dict(result_trip, func_fields)
        filtered = filter_trip_units_strict(trip_df, need, model_col="型号")
        model, _ = select_minimal_trip_model_strict(filtered, model_col="型号")
        result_breaker["推荐脱扣器"] = model if model else "NA"
        if not model:
            st.warning("没有找到满足条件的脱扣器型号")
    else:
        result_breaker["推荐脱扣器"] = "NA"

    # ===== 3. 显示产品序列号/订货号、详细技术参数 =====
    try:
        sn_list = select_all_breaker_models(result_breaker)
        table_rows = []
        for sn in sn_list:
            order_no = sn_order_map.get(sn, "未找到订货号")
            table_rows.append({"产品序列号": sn, "订货号": order_no})

        st.markdown("#### 断路器推荐：")
        st.table(pd.DataFrame(table_rows))

        merged_df, not_found = collect_sn_detail_table(sn_list, product_df, sn_to_pattern)
        if merged_df is not None:
            st.markdown("#### 断路器详细参数：")
            st.table(merged_df)
        if not_found:
            st.warning("以下型号未找到详细参数信息：\n" + "\n".join(not_found))
    except Exception as e:
        table_rows = []
        st.warning(f"型号筛选出错：{e}")

    # ===== 4. 写入日志和历史 =====
    write_llm_log(
        user_input=user_input,
        breaker_structured=result_breaker,
        trip_structured=result_trip,
        table_rows=table_rows,
        log_path=LOG_CFG["path"],
        max_entries=LOG_CFG["max_entries"]
    )

    st.session_state[SESSION_CFG["history"]].append({
        "role": "assistant",
        "content": "",
        "table_rows": table_rows
    })
