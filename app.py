import streamlit as st
import random
import re
import json
from openai import OpenAI

# ==================== 页面配置 ====================
st.set_page_config(page_title="新人破冰助手", page_icon="🧊")
st.title("🧊 新人破冰助手")
st.caption("帮你找到兴趣相投的搭子，打破尴尬，轻松开聊！")

# ==================== 同学库 ====================
STUDENT_MEMBERS = {
    "001": {
        "nickname": "阿泽",
        "tags": ["跑步", "马拉松", "夜跑", "运动健身", "户外"],
        "intro": "跑龄3年，每周固定3次夜跑，参加过半马",
        "type": "student"
    },
    "002": {
        "nickname": "小夏",
        "tags": ["读书", "悬疑小说", "推理", "文学", "线下读书会"],
        "intro": "悬疑推理迷，每月读3-5本新书，会组织同城读书分享会",
        "type": "student"
    },
    "003": {
        "nickname": "阿凯",
        "tags": ["摄影", "拍街", "胶片", "城市风光", "相机"],
        "intro": "胶片摄影爱好者，喜欢城市拍摄",
        "type": "student"
    },
    "004": {
        "nickname": "七七",
        "tags": ["烘焙", "甜品", "咖啡", "手作", "美食"],
        "intro": "在家做烘焙，擅长戚风、曲奇",
        "type": "student"
    },
    "005": {
        "nickname": "大东",
        "tags": ["游戏", "王者荣耀", "开黑", "电竞"],
        "intro": "王者荣耀钻石段位，主玩射手",
        "type": "student"
    },
    "006": {
        "nickname": "小雨",
        "tags": ["跑步", "晨跑", "健康"],
        "intro": "晨跑爱好者，每天早上5公里",
        "type": "student"
    }
}

# ==================== 老师库（兴趣同好版） ====================
TEACHER_MEMBERS = {
    "101": {
        "nickname": "张老师",
        "tags": ["跑步", "马拉松", "运动健身", "户外"],
        "intro": "高中数学老师，跑龄5年，已完成3次全马，喜欢约跑交流",
        "type": "teacher"
    },
    "102": {
        "nickname": "李老师",
        "tags": ["读书", "文学", "悬疑小说", "分享"],
        "intro": "英语老师，热爱阅读，每月读书会固定成员，喜欢聊书",
        "type": "teacher"
    },
    "103": {
        "nickname": "王老师",
        "tags": ["摄影", "街拍", "城市风光", "相机"],
        "intro": "物理老师，摄影爱好者，周末喜欢扫街拍照，可以一起约拍",
        "type": "teacher"
    },
    "104": {
        "nickname": "陈老师",
        "tags": ["游戏", "原神", "二次元", "开黑"],
        "intro": "信息技术老师，原神老玩家，全地图100%，欢迎一起探索",
        "type": "teacher"
    },
    "105": {
        "nickname": "刘老师",
        "tags": ["烘焙", "甜品", "咖啡", "手作"],
        "intro": "语文老师，业余烘焙达人，擅长戚风和曲奇，喜欢交流配方",
        "type": "teacher"
    },
    "106": {
        "nickname": "赵老师",
        "tags": ["瑜伽", "冥想", "健康", "运动"],
        "intro": "体育老师，瑜伽爱好者，每天早晨练习，可以一起晨练",
        "type": "teacher"
    },
    "107": {
        "nickname": "孙老师",
        "tags": ["编程", "开源", "Python", "AI"],
        "intro": "计算机老师，热爱编程，业余做开源项目，欢迎技术交流",
        "type": "teacher"
    }
}

# 破冰话题库
ICE_BREAKER_LIBRARY = {
    "跑步": [
        "你一般在哪里跑步？有没有推荐的路线？",
        "你跑过最长的距离是多少？",
        "你喜欢晨跑还是夜跑？为什么？"
    ],
    "读书": [
        "最近在读什么书？有没有特别想推荐的？",
        "你更喜欢纸质书还是电子书？",
        "你一般怎么选书？看榜单还是朋友推荐？"
    ],
    "摄影": [
        "你最喜欢拍什么题材？人像还是风景？",
        "你用手机还是相机拍？",
        "有没有特别满意的作品可以分享？"
    ],
    "烘焙": [
        "你最拿手的甜点是什么？",
        "你是什么时候开始学烘焙的？",
        "有没有失败过很好笑的经历？"
    ],
    "游戏": [
        "你最喜欢玩什么英雄？",
        "你平时是打排位还是娱乐模式多？",
        "晚上有空一起开黑吗？"
    ],
    "瑜伽": [
        "你练瑜伽多久了？",
        "你最喜欢哪个体式？",
        "早上练还是晚上练？"
    ],
    "编程": [
        "你最喜欢用什么编程语言？",
        "最近在做什么项目？",
        "有什么学习资源推荐吗？"
    ]
}

GENERIC_ICE_BREAKERS = [
    "你当初是怎么开始这个爱好的？",
    "你理想中的搭子是什么样的？",
    "你平时都是一个人做这件事吗？"
]

WELCOME_MESSAGES = [
    "🎉 欢迎新朋友！\n\n我是新人破冰助手，专门帮你：\n✅ 找到兴趣相投的同学/老师搭子\n✅ 提供破冰话题，告别尴尬开场\n\n---\n开始之前，请先选择：\n🔹 扣 1 → 找同学搭子\n🔹 扣 2 → 找老师搭子",
    "👋 你好呀！\n\n我是你的专属破冰助手！\n\n现在告诉我：\n输入 1 找同学搭子\n输入 2 找老师搭子",
    "🧊 欢迎加入破冰小窝！\n\n第一步：选择搭子类型\n1️⃣ 同学搭子\n2️⃣ 老师搭子\n\n直接回复 1 或 2 吧！"
]

COLD_START_MESSAGES = [
    "请先告诉我：扣1找同学搭子，扣2找老师搭子",
    "不知道怎么开始？输入 1 找同学，输入 2 找老师",
    "别忘了先选类型哦：1=同学，2=老师"
]

CHAT_RESPONSES = {
    "一个人": "其实很多人刚开始都是一个人，找到搭子后会更有动力！",
    "怎么开始": "先告诉我你想找同学还是老师？扣1找同学，扣2找老师",
    "理想": "每个人理想的搭子都不一样～先选类型吧：1=同学，2=老师",
    "默认": "先选一下类型：扣1找同学搭子，扣2找老师搭子"
}

DEEPSEEK_API_KEY = "sk-8d639eac6c0c4bd3a0fc1096bf49ed93"

def get_ai_reply(messages):
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI服务暂时不可用：{str(e)}"

def get_current_members():
    if st.session_state.partner_type == "student":
        return STUDENT_MEMBERS, "同学"
    else:
        return TEACHER_MEMBERS, "老师"

def find_matches(user_input):
    members, type_name = get_current_members()
    matches = []
    for uid, member in members.items():
        score = 0
        matched_tags = []
        for tag in member["tags"]:
            if tag.lower() in user_input.lower():
                score += 1
                matched_tags.append(tag)
        if score > 0:
            matches.append({
                "member": member,
                "score": score,
                "matched_tags": matched_tags
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:3]

def get_icebreakers(matched_tags):
    for tag in matched_tags:
        for interest, questions in ICE_BREAKER_LIBRARY.items():
            if interest in tag or tag in interest:
                return questions[:3]
    return GENERIC_ICE_BREAKERS[:3]

def get_chat_reply(user_input):
    user_lower = user_input.lower()
    for key, reply in CHAT_RESPONSES.items():
        if key in user_lower:
            return reply
    return CHAT_RESPONSES["默认"]

def is_cold_start(messages):
    if len(messages) <= 1:
        return True
    for msg in reversed(messages):
        if msg["role"] == "user":
            text = msg["content"].strip()
            if len(text) < 3 or text in ["嗯", "哦", "好", "不知道", "随便"]:
                return True
            break
    return False

def detect_intent(user_input):
    user_lower = user_input.lower()
    
    if user_input in ["1", "2"]:
        return "select_type"
    
    if "喜欢" in user_lower or "想找" in user_lower:
        return "matching"
    
    matching_keywords = ["找搭子", "匹配", "推荐", "兴趣", "跑步", "读书", "游戏", "摄影", "烘焙", "瑜伽", "编程"]
    
    for q in GENERIC_ICE_BREAKERS:
        if q.lower() in user_lower:
            return "chat"
    
    if any(kw in user_lower for kw in matching_keywords):
        return "matching"
    
    if len(user_input) < 5:
        return "cold"
    
    return "chat"

# ==================== 初始化 ====================
if "is_new_user" not in st.session_state:
    st.session_state.is_new_user = True
    st.session_state.messages = []
    st.session_state.partner_type = None
    welcome_msg = random.choice(WELCOME_MESSAGES)
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome_msg
    })

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.partner_type = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
if prompt := st.chat_input("输入1或2选择类型，然后告诉我你的兴趣..."):
    if st.session_state.is_new_user:
        st.session_state.is_new_user = False
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    intent = detect_intent(prompt)
    
    if intent == "select_type" or (st.session_state.partner_type is None and prompt in ["1", "2"]):
        if prompt == "1":
            st.session_state.partner_type = "student"
            reply = "✅ 已选择【同学搭子】！\n\n现在告诉我你的兴趣、空闲时间和位置，我来帮你匹配～\n\n💡 例如：我喜欢跑步，周六上午有空"
        else:
            st.session_state.partner_type = "teacher"
            reply = "✅ 已选择【老师搭子】！\n\n老师也可以是兴趣同好～告诉我你的兴趣爱好，我来帮你匹配有相同兴趣的老师！\n\n💡 例如：我喜欢跑步，想找同样爱跑步的老师"
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
    
    elif st.session_state.partner_type is None:
        cold_reply = random.choice(COLD_START_MESSAGES)
        st.session_state.messages.append({"role": "assistant", "content": cold_reply})
        with st.chat_message("assistant"):
            st.markdown(cold_reply)
    
    elif is_cold_start(st.session_state.messages) or intent == "cold":
        type_display = "同学" if st.session_state.partner_type == "student" else "老师"
        cold_reply = f"你现在找的是{type_display}搭子。告诉我你的兴趣，我来帮你匹配～\n\n💡 例如：我喜欢跑步，周六上午有空"
        st.session_state.messages.append({"role": "assistant", "content": cold_reply})
        with st.chat_message("assistant"):
            st.markdown(cold_reply)
    
    elif intent == "chat":
        chat_reply = get_chat_reply(prompt)
        st.session_state.messages.append({"role": "assistant", "content": chat_reply})
        with st.chat_message("assistant"):
            st.markdown(chat_reply)
    
    else:
        matches = find_matches(prompt)
        type_name = "同学" if st.session_state.partner_type == "student" else "老师"
        
        if matches:
            reply = "🔍 **为你找到以下" + type_name + "搭子：**\n\n"
            for i, m in enumerate(matches, 1):
                member = m["member"]
                reply += str(i) + ". **" + member["nickname"] + "**：" + member["intro"] + "\n"
                reply += "   📌 匹配标签：" + ", ".join(m["matched_tags"]) + "\n\n"
            
            best_match = matches[0]
            icebreakers = get_icebreakers(best_match["matched_tags"])
            reply += "---\n💬 **不知道怎么开口？试试这些破冰问题：**\n"
            for i, q in enumerate(icebreakers, 1):
                reply += "\n" + str(i) + ". " + q
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        else:
            reply = "😅 暂时没找到匹配的" + type_name + "搭子。\n\n你可以：\n1. 换个兴趣试试\n2. 告诉我更具体的需求\n\n或者直接说：我喜欢跑步，周六上午有空"
            st.session_state.messages.append