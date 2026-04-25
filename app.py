import streamlit as st
import requests
import json

st.set_page_config(page_title="AI 搭子助手", page_icon="🤖")
st.title("🤖 AI 搭子助手 - 由 Coze 驱动")

# ========== 在这里填入你的 Coze 凭证 ==========
COZE_API_TOKEN = "pat_xxxxxx"   # pat_8KuJ2g2tTgk3UJC6ZmRJVyM7Tp3ziHwDJ1sUgRhkyPZ3mg7zcYcsDtgJALGgXGk3
BOT_ID = "7632668226932965418"   # 7632668226932965418
# ============================================

# Coze API 调用函数
def call_coze(user_input, chat_history):
    url = "https://api.coze.cn/v1/chat"
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    # 构建消息列表（Coze 要求格式）
    messages = []
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    messages.append({"role": "user", "content": user_input})
    
    payload = {
        "bot_id": BOT_ID,
        "user_id": "streamlit_user",
        "messages": messages,
        "auto_save_history": True
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # 提取回复内容
        return data["messages"][-1]["content"]
    except Exception as e:
        return f"调用 Coze 失败：{e}"

# 初始化会话
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "嗨！我是你的破冰小助手，想找同学还是老师搭子？告诉我你的兴趣吧～"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 用户输入
prompt = st.chat_input("例如：我想找个喜欢跑步的同学")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Coze 智能体思考中..."):
            reply = call_coze(prompt, st.session_state.messages[:-1])  # 传历史（不含刚添加的）
            st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})