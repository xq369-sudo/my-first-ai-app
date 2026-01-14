import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import requests
from docx import Document 
from io import BytesIO 

# 1. 网页配置
st.set_page_config(page_title="Astra", page_icon="💫", layout="wide")
st.title("💫 Astra 小星AI (智能联网增强版)")

# --- 初始化对话记忆 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 初始化客户端
DEEPSEEK_KEY = st.secrets.get("api_key", "sk-0a477b0f3c874c8184f0a2ec168c3f2d")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY", "") 

client = OpenAI(
    api_key=DEEPSEEK_KEY, 
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏：文件处理与智能工具
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

    # --- 师父秘籍：智能动态导出功能 ---
    st.subheader("📝 成果导出")
    
    if len(st.session_state.messages) > 0:
        def create_word():
            doc = Document()
            
            # 【功能优化：智能总结标题】
            # 取第一个问题的前15个字作为核心，如果没有则用默认名
            raw_title = st.session_state.messages[0]["content"][:15].strip()
            summary_title = f"关于【{raw_title}】的深度分析报告"
            
            # 设置 Word 文档主标题
            doc.add_heading(summary_title, 0)
            
            # 遍历所有对话记录，确保实时同步
            for msg in st.session_state.messages:
                role_name = "👤 用户提问" if msg["role"] == "user" else "🤖 Astra 助手回答"
                doc.add_heading(role_name, level=1)
                doc.add_paragraph(msg["content"])
                doc.add_paragraph("-" * 30)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer, summary_title

        # 生成 Word 数据和动态文件名
        word_data, file_title = create_word()

        st.download_button(
            label="✨ 点击下载全量报告 (Word)",
            data=word_data,
            file_name=f"{file_title}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="download_btn_pro"
        )
        st.caption(f"文件名将自动设为：{file_title}")
    else:
        st.info("💡 请先在下方开始对话，我会为您即时准备分析报告。")

    st.divider()
    if st.button("🗑️ 清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

# 4. 主界面：展示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 主界面：输入区
if user_question := st.chat_input("输入你的问题，或者让Astra帮你搜搜实时动态..."):
    
    # 存入用户问题
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # 助手思考与回答
    with st.chat_message("assistant"):
        with st.spinner('Astra 正在跨越时空为您整合资料...'):
            try:
                # --- 智能联网逻辑 ---
                search_results = ""
                if TAVILY_KEY:
                    try:
                        resp = requests.post(
                            "https://api.tavily.com/search",
                            json={"api_key": TAVILY_KEY, "query": user_question, "max_results": 3}
                        )
                        results = resp.json().get("results", [])
                        search_results = "\n".join([f"来源: {r['title']}\n内容: {r['content']}" for r in results])
                        st.sidebar.info("🌐 已从 Tavily 获取实时动态")
                    except:
                        pass
                
                if not search_results:
                    trigger_words = ["搜", "查", "最新", "政策", "2026", "行情", "天气"]
                    if any(word in user_question for word in trigger_words):
                        try:
                            from duckduckgo_search import DDGS
                            with DDGS() as ddgs:
                                results = [r for r in ddgs.text(user_question, region='cn-zh', max_results=3)]
                                if results:
                                    search_results = "\n".join([f"来源: {r['title']}\n内容: {r['body']}" for r in results])
                                    st.sidebar.info("🌐 已成功获取联网信息")
                        except:
                            pass

                # --- 构造指令 ---
                system_instruction = "你是一个全能专家，请结合文档和联网信息给出深度、清晰的回答。"
                if file_content:
                    system_instruction += f"\n\n【本地文档】：\n{file_content}"
                if search_results:
                    system_instruction += f"\n\n【最新联网信息】：\n{search_results}"

                # API 请求
                res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages
                )
                
                answer = res.choices[0].message.content
                st.markdown(answer)
                
                # 关键一步：存入回答并立即重刷页面，确保侧边栏按钮同步获取最新内容
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun() 
                
            except Exception as e:
                st.error(f"抱歉，小星在生成时遇到一点阻碍：{e}")
