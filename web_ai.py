import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# 1. 网页配置
st.set_page_config(page_title="Astra", page_icon="💫")
st.title("💫  Astra 小星助手")

# 2. 初始化客户端 (使用 Streamlit Secrets 保护你的 Key)
# 提示：如果你还没设置 Secrets，先临时写死 key 调试，成功后再改
client = OpenAI(
    api_key="sk-0a477b0f3c874c8184f0a2ec168c3f2d", 
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏：上传文档
with st.sidebar:
    st.header("📂 文件上传")
    uploaded_file = st.file_uploader("上传 PDF 文档", type="pdf")
    
    file_content = ""
    if uploaded_file:
        # 读取 PDF 内容
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            file_content += page.extract_text()
        st.success("✅ 文档读取成功！")

# 4. 主界面
# 无论是否上传文件，都显示输入框
user_question = st.text_input("在这里输入你的问题：", placeholder="可以直接问我，也可以上传PDF后针对文档提问...")

if st.button("开始生成"):
    if user_question:
        with st.spinner('正在思考中...'):
            # 如果有文件，就把内容喂给系统；如果没有，就当普通助手
            context = f"以下是参考文档内容：\n{file_content}" if uploaded_file else "你是一个全能助手。"
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_question}
                ]
            )
            st.subheader("💡 Astra 回答：")
            st.write(response.choices[0].message.content)

    if st.button("开始分析"):
        if user_question:
            with st.spinner('正在翻阅文档中...'):
                try:
                    # 这里的逻辑是：把文档内容塞给 AI 的系统提示词里
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": f"你是一个文档分析专家。以下是文档内容：\n\n{file_content}"},
                            {"role": "user", "content": user_question}
                        ]
                    )
                    st.subheader("💡 Astra 回答：")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"分析失败：{e}")
