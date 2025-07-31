import streamlit as st

from config.config import DATA_CFG, SESSION_CFG
from utils.ui_components import init_page, render_sidebar, render_chat_history, render_footer, render_input_hint
from chat_logic import run_chat_pipeline
from data_loader import load_product_df, load_sn_order_map

# 初始化页面和 UI
init_page()

# 初始化 session 状态
if SESSION_CFG["history"] not in st.session_state:
    st.session_state[SESSION_CFG["history"]] = []
if SESSION_CFG["trip_df"] not in st.session_state:
    st.session_state[SESSION_CFG["trip_df"]] = None

# 加载订货号
sn_order_map = load_sn_order_map(path=DATA_CFG["order_num_json"])
# 加载断路器参数
product_df = load_product_df(path=DATA_CFG["breaker_3WA_1"])

# 渲染侧边栏，并返回 trip_df
trip_df = render_sidebar()

# 渲染历史记录
render_chat_history()

# 获取用户输入
render_input_hint()
user_input = st.chat_input("请输入您的问题...")
if user_input:
    st.session_state[SESSION_CFG["history"]].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        run_chat_pipeline(user_input, trip_df, sn_order_map, product_df)

# 页脚
render_footer()
