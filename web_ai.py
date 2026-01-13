import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import requests  # 用来发搜索请求

# 1. 网页配置
st.set_page_config(page_title="Astra", page_icon="💫", layout="wide")
st.title("💫 Astra 小星 AI (Tavily 增强版)")

# --- 初始化记忆 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 获取配置 (从 Secrets 读取)
DEEPSEEK_KEY = "sk-0a477b0f3c874c8184f0a2ec168c3f2d"
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY", "") # 从安全设置里拿 Key

client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

# 3. 侧边栏
with st.sidebar:
    st.header("📂 知识库")
    uploaded_file = st.file_uploader("上传 PDF", type="pdf")
    file_content = ""
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        file_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        st.success("✅ 文档已加载")
    if st.button("🗑️ 清空记忆"):
        st.session_state.messages = []
        st.rerun()

# 4. 展示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 核心搜索与对话逻辑
if user_question := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner('Astra 正在穿越时空搜寻资料...'):
            search_context = ""
            # 只要有 Key 且用户想搜，就调用专业搜索接口
            if TAVILY_KEY:
                try:
                    # 发送专业搜索请求
                    response = requests.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": TAVILY_KEY,
                            "query": user_question,
                            "search_depth": "basic",
                            "max_results": 3
                        }
                    )
                    results = response.json().get("results", [])
                    if results:
                        search_context = "\n".join([f"来源: {r['title']}\n内容: {r['content']}" for r in results])
                        st.sidebar.info("🌐 已从 Tavily 获取实时动态")
                except:
                    st.sidebar.warning("搜索暂时有点堵车...")

            # 构建系统提示词
            system_prompt = "你是一个全能专家。结合以下信息回答："
            if file_content: system_prompt += f"\n\n【本地文档】：{file_content}"
            if search_context: system_prompt += f"\n\n【最新动态】：{search_context}"

            # 调用 DeepSeek
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
            )
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
