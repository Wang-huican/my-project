import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#保存会话信息
def save_session():
    if st.session_state.history:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "session_id": st.session_state.session_id,
            "history": st.session_state.history
        }
        # 创建一个文件夹
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open(f"sessions/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
#加载所有的会话信息
def load_sessions():
    sessions_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filenaem in file_list:
            if filenaem.endswith(".json"):
                sessions_list.append(filenaem[:-5:])
    sessions_list.sort(reverse=True)
    return sessions_list
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.history = session_data["history"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.session_id = session_name
    except Exception as e:
        st.error("加载会话失败：", e)

def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if session_name == st.session_state.session_id:
                st.session_state.history = []
                st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        st.error("删除失败：", e)

#大标题
st.title("AI智能伴侣")

#logo
st.logo("six/logo.png")

client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")
#系统提示词
system_prompt = """"你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。"""


#初始化聊天信息
if "history" not in st.session_state:
    st.session_state.history = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "塔派"
#性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的川渝姑娘"

#会话标识
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 显示聊天记录
st.text(f"会话名称：{st.session_state.session_id}")
for message in st.session_state.history:
    st.chat_message(message["role"]).write(message["content"])

with st.sidebar:
    #AI控制面板
    st.subheader("AI控制面板")
    #新建会话
    if st.button("新建会话", icon="✏️"):
        #保存当前会话信息
        save_session()
        #创建新的的会话
        if st.session_state.history:
           st.session_state.history = []
           st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
           save_session()
           st.rerun()

    #会话历史
    st.text("会话历史")
    sessions_list = load_sessions()
    for session in sessions_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #三元运算符
            if st.button(session, icon="📄", type="primary" if session == st.session_state.session_id else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", icon="🗑️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
    st.divider()

    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    st.session_state.nick_name = nick_name
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    st.session_state.nature = nature

#聊天消息的输入框
message = st.chat_input("请输入你的问题")
if message:#字符串会自动转化为布尔值
    st.chat_message("user").write(message)
    print("----------->调用大模型， 提示词", message)

    st.session_state.history.append({"role": "user", "content": message})
    # 与AI大模型进行对话（参数）

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content":system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.history
        ],
        stream=True
    )

    response_message = st.empty() #创建一个空的消息框
    full_response = ""

    # 输出大模型返回的结果（非流式输出的解析方式）
    #st.chat_message("assistant").write(response.choices[0].message.content)
    for chunk in response:
        if chunk.choices[0].delta.content  is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    st.session_state.history.append({"role": "assistant", "content": full_response})

    save_session()
