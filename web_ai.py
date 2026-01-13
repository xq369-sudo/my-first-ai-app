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
# ... 前面的代码保持不变 ...

if user_question := st.chat_input("跟我聊聊你的规划，或者让我帮你搜搜最新的行业动态..."):
    
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner('Astra 正在联网查资料并思考...'):
            try:
                # --- 新增：联网搜索逻辑 ---
                search_results = ""
                # 如果问题里包含“搜”、“查”、“最新”、“2026”等词，就触发搜索
                trigger_words = ["搜", "查", "最新", "新闻", "政策", "2026", "行情"]
                if any(word in user_question for word in trigger_words):
                    with DDGS() as ddgs:
                        # 抓取前 3 条搜索结果
                        results = [r for r in ddgs.text(user_question, region='cn-zh', max_results=3)]
                        search_results = "\n".join([f"标题: {r['title']}\n摘要: {r['body']}" for r in results])
                
                # --- 构造增强版的系统提示词 ---
                system_instruction = """你是一个拥有联网能力的专家助手。
                你会结合文档内容、对话历史和最新的联网搜索结果来回答。
                如果提供了搜索结果，请优先参考搜索结果中的实时信息。"""
                
                if file_content:
                    system_instruction += f"\n\n参考文档内容：\n{file_content}"
                if search_results:
                    system_instruction += f"\n\n最新的联网搜索结果：\n{search_results}"

                # 发送请求
                messages_for_api = [{"role": "system", "content": system_instruction}] + st.session_state.messages
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_for_api
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"联网搜索或生成失败：{e}")

