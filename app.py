import streamlit as st
import random
from openai import OpenAI

st.set_page_config(page_title="新人破冰助手", page_icon="🧊")
st.title("🧊 新人破冰助手")

# 同学库（含唱歌搭子）
STUDENTS = {
    "阿泽": {"tags": ["跑步", "马拉松"], "intro": "跑龄3年，参加过半马"},
    "小夏": {"tags": ["读书", "悬疑"], "intro": "悬疑推理迷，每月读3-5本书"},
    "麻辣小林": {"tags": ["火锅", "麻辣", "饭搭子"], "intro": "无辣不欢，找饭搭子"},
    "甜品小艺": {"tags": ["甜品", "奶茶", "饭搭子"], "intro": "甜品控，找下午茶搭子"},
    "麦霸小陈": {"tags": ["唱歌", "KTV", "流行音乐", "歌友"], "intro": "KTV麦霸，擅长流行情歌，找歌友一起去K歌"},
    "民谣小周": {"tags": ["唱歌", "民谣", "吉他", "弹唱"], "intro": "民谣爱好者，会弹吉他，喜欢一起弹唱交流"},
}

# 老师库（含唱歌搭子）
TEACHERS = {
    "张老师": {"tags": ["跑步", "马拉松"], "intro": "数学老师，跑龄5年"},
    "李老师": {"tags": ["读书", "文学"], "intro": "英语老师，热爱阅读"},
    "周老师": {"tags": ["日料", "饭搭子"], "intro": "化学老师，日料爱好者"},
    "王老师": {"tags": ["唱歌", "KTV", "经典老歌"], "intro": "音乐老师，喜欢经典老歌，可以一起K歌交流"},
    "陈老师": {"tags": ["唱歌", "美声", "合唱"], "intro": "声乐老师，擅长美声和合唱，找歌友一起练习"},
}

# 破冰问题
ICE_BREAKERS = {
    "跑步": ["你一般在哪里跑步？", "你跑过最长的距离？"],
    "读书": ["最近在读什么书？", "你最喜欢哪个作者？"],
    "火锅": ["你最喜欢什么锅底？", "有没有推荐的火锅店？"],
    "甜品": ["你最喜欢的奶茶是哪家？", "蛋糕你喜欢什么口味？"],
    "日料": ["你最喜欢吃什么刺身？", "日料店你推荐哪家？"],
    "唱歌": ["你最喜欢唱谁的歌？", "KTV你必点哪首歌？", "你擅长什么类型的歌？"],
    "民谣": ["你最喜欢的民谣歌手是谁？", "你会弹吉他吗？", "最近在练什么歌？"],
    "KTV": ["你多久去一次KTV？", "你最喜欢和谁一起去唱歌？", "有没有私藏的KTV推荐？"],
}

DEFAULT_ICE = ["你是怎么开始这个爱好的？", "你理想中的搭子是什么样的？"]

DEEPSEEK_API_KEY = "sk-8d639eac6c0c4bd3a0fc1096bf49ed93"

def find_matches(user_input, members):
    matches = []
    # 同义词映射
    user_input_lower = user_input.lower()
    if "唱歌" in user_input_lower or "k歌" in user_input_lower or "ktv" in user_input_lower or "歌友" in user_input_lower:
        user_input_lower = user_input_lower.replace("k歌", "唱歌").replace("ktv", "唱歌").replace("歌友", "唱歌")
    
    for name, info in members.items():
        for tag in info["tags"]:
            if tag in user_input_lower or tag in user_input:
                matches.append((name, info))
                break
    return matches[:3]

if "step" not in st.session_state:
    st.session_state.step = "welcome"
    st.session_state.type = None

if st.session_state.step == "welcome":
    st.write("🎉 欢迎！找同学搭子扣1，找老师搭子扣2")
    prompt = st.chat_input("输入1或2")
    if prompt == "1":
        st.session_state.type = "student"
        st.session_state.step = "ask"
        st.rerun()
    elif prompt == "2":
        st.session_state.type = "teacher"
        st.session_state.step = "ask"
        st.rerun()

elif st.session_state.step == "ask":
    members = STUDENTS if st.session_state.type == "student" else TEACHERS
    type_name = "同学" if st.session_state.type == "student" else "老师"
    st.write(f"你找的是{type_name}搭子，告诉我你的兴趣吧～")
    st.write("💡 例如：我喜欢跑步、我想找饭搭子、我喜欢唱歌")
    prompt = st.chat_input("说说你的兴趣...")
    if prompt:
        matches = find_matches(prompt, members)
        if matches:
            reply = f"🔍 找到以下{type_name}搭子：\n"
            for name, info in matches:
                reply += f"\n**{name}**：{info['intro']}"
            # 找破冰问题
            for tag in matches[0][1]["tags"]:
                if tag in ICE_BREAKERS:
                    reply += f"\n\n💬 破冰问题：{ICE_BREAKERS[tag][0]}"
                    break
                # 检查相关关键词
                for key in ICE_BREAKERS:
                    if key in tag:
                        reply += f"\n\n💬 破冰问题：{ICE_BREAKERS[key][0]}"
                        break
            st.write(reply)
        else:
            st.write("😅 没找到匹配的搭子，试试换个兴趣？\n💡 试试：我喜欢跑步、我想找饭搭子、我喜欢唱歌")
        st.session_state.step = "welcome"
        st.rerun()