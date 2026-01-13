import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# 1. 网页配置
st.set_page_config(page_title="Astra", page_icon="💫", layout="wide")
st.title("💫 Astra 小星AI (联网搜索增强版)")

# --- 核心记忆：初始化对话记忆 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        try:
            reader = PdfReader(uploaded_file)
            file_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.success("✅ 您的文档已装载！")
        except Exception as e:
            st.error(f"读取PDF失败: {e}")
    
    st.divider()
    if st.button("🗑️ 清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

# 4. 主界面：展示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 主界面：输入区 (这里是师父帮你改好的核心逻辑)
if user_question := st.chat_input("问问我，或者让我帮搜搜最新的行业动态..."):
    
    # A. 存入用户问题
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # B. 助手思考与回答
    with st.chat_message("assistant"):
        with st.spinner('Astra 正在思考(联网搜索中)...'):
            try:
                # --- 智能搜索逻辑（进阶容错版） ---
                search_results = ""
                # 定义触发联网的词
                trigger_words = ["搜", "查", "最新", "新闻", "政策", "2026", "行情", "天气", "什么时候"]
                
                if any(word in user_question for word in trigger_words):
                    try:
                        # 动态导入库，增强稳定性
                        from duckduckgo_search import DDGS
                        with DDGS() as ddgs:
                            # 搜索前3条相关信息
                            results = [r for r in ddgs.text(user_question, region='cn-zh', max_results=3)]
                            if results:
                                search_results = "\n".join([f"来源: {r['title']}\n内容: {r['body']}" for r in results])
                                st.sidebar.info("🌐 小星已成功获取联网实时信息")
                    except Exception as search_e:
                        # 侧边栏静默报错，不打断主聊天
                        st.sidebar.warning(f"联网搜索暂时不可用: {search_e}")

                # --- 构造增强版系统指令 ---
                system_instruction = """你是一个世界顶级的职业导师和全能专家。
                1. 如果提供了【联网信息】，请将其作为最新的事实背景来回答。
                2. 如果提供了【参考文档】，请优先结合文档回答用户关于规划的问题。
                3. 如果两者都有，请结合实时动态分析文档。
                4. 始终使用专业、客观且友好的语气。"""
                
                if file_content:
                    system_instruction += f"\n\n【参考文档内容】：\n{file_content}"
                if search_results:
                    system_instruction += f"\n\n【最新联网信息】：\n{search_results}"

                # C. 构造请求消息
                messages_for_api = [{"role": "system", "content": system_instruction}] + st.session_state.messages
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_for_api
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                
                # D. 存入助手回答
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"抱歉，Astra小星遇到了一点技术问题：{e}")
