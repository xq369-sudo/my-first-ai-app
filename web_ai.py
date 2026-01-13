import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# 1. 网页配置
st.set_page_config(page_title="Astra", page_icon="💫", layout="wide")
st.title("💫 Astra 小星AI")

# --- 核心记忆：初始化对话记忆 ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # 这个盒子用来装所有的聊天记录

# 2. 初始化客户端
client = OpenAI(
    api_key="sk-0a477b0f3c874c8184f0a2ec168c3f2d", 
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏：文件处理和功能区
with st.sidebar:
    st.header("📂 文件上传")
    uploaded_file = st.file_uploader("上传 PDF 文档", type="pdf")
    
    file_content = ""
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        # 提取文字并防止粘连
        file_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        st.success("✅ 你的文档已装载完毕！")
    
    st.divider() # 画条线
    if st.button("🗑️ 清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

# 4. 主界面：展示对话历史
# 用气泡的方式展示之前聊过的内容
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 主界面：输入区
# 使用 st.chat_input，它会自动固定在页面底部，体验极好
if user_question := st.chat_input("跟小星聊聊你的规划，或者针对文档提问..."):
    
    # A. 先把你的问题存进记忆，并显示在网页上
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # B. 调用 AI 进行回答
    with st.chat_message("assistant"):
        with st.spinner('Astra 正在思考中...'):
            try:
                # 设定 AI 的人设（你可以根据需要修改）
                system_instruction = """你是一个世界顶级的职业生涯规划专家，拥有心理学和人力资源管理的双重背景。
                你会阅读用户上传的内容，并结合上下文提供有洞察力的分析。
                回答要求：逻辑清晰、语气专业且富有启发性，多使用 Markdown 格式（标题、加粗、列表）。"""
                
                # 如果有上传文件，就把文件内容塞进系统提示词里
                if file_content:
                    system_instruction += f"\n\n以下是参考文档内容：\n{file_content}"

                # 构造发送给 DeepSeek 的完整消息列表（系统人设 + 历史记忆）
                messages_for_api = [{"role": "system", "content": system_instruction}] + st.session_state.messages
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_for_api,
                    stream=False # 如果想要打字机效果可以设为 True，新手建议先选 False
                )
                
                answer = response.choices[0].message.content
                
                # C. 把 AI 的回答存进记忆，并显示出来
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"发生错误：{e}")
