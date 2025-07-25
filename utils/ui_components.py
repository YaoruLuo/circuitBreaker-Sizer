import streamlit as st
import pandas as pd
from config.config import UI_CFG, SESSION_CFG


def init_page():
    """初始化页面信息和标题"""
    st.set_page_config(page_title=UI_CFG["page_title"], layout=UI_CFG["layout"])
    st.markdown(f"""
        <h1 style="margin-bottom:0;color:#009999;">{UI_CFG["page_title"]}</h1>
        <div style="color: #888; font-size:16px;margin-top:0;">
        SIEMENS IOX-AI
        </div>
        <hr>
    """, unsafe_allow_html=True)


def render_sidebar():
    """展示侧边栏上传和配置按钮"""
    from trip_recommend import load_trip_df_with_transpose

    with st.sidebar:
        st.markdown("### 📂 断路器知识库")
        uploaded_file = st.file_uploader("上传参数表（Excel）", type=["xlsx"])

        if uploaded_file:
            trip_df = load_trip_df_with_transpose(uploaded_file)
            st.session_state[SESSION_CFG["trip_df"]] = trip_df
            st.success(f"成功读取 {len(trip_df)} 条脱扣器型号")
            with st.expander("预览前10条"):
                st.dataframe(trip_df.head(10), use_container_width=True)
        elif st.session_state.get(SESSION_CFG["trip_df"]) is not None:
            trip_df = st.session_state[SESSION_CFG["trip_df"]]
        else:
            trip_df = None

        st.caption("上传后可直接用自然语言选型/查表。数据只保存在本地浏览器内存。")
        st.markdown("---")
        if st.button("清除历史对话", key="clean"):
            st.session_state[SESSION_CFG["history"]] = []
            st.experimental_rerun()

    return trip_df


def render_chat_history():
    """展示历史聊天内容（仅用户输入和表格）"""
    for msg in st.session_state[SESSION_CFG["history"]]:
        with st.chat_message(msg["role"]):
            if msg.get("role") == "user" and msg.get("content"):
                st.markdown(msg["content"], unsafe_allow_html=True)
            elif msg.get("role") == "assistant" and msg.get("table_rows"):
                st.markdown("#### 断路器推荐：")
                df = pd.DataFrame(msg["table_rows"])
                if not df.empty:
                    st.table(df)


def render_footer():
    st.markdown(
        "<div style='color:#bbb; font-size:13px; margin-top:32px'>仅用于学习与测试，数据与解析结果请最终以官方文档和人工校验为准。</div>",
        unsafe_allow_html=True
    )
