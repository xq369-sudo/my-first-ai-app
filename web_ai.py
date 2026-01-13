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
   # 修改读取 PDF 的部分
if uploaded_file:
    reader = PdfReader(uploaded_file)
    # 给每一页内容后面加个换行符，防止文字粘在一起
    file_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    st.success("✅ 你的职业规划书已装载完毕！")
    
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
    {
        "role": "system", 
        "content": """你是一个世界顶级的职业生涯规划专家，拥有心理学和人力资源管理的双重背景。
        你现在的任务是阅读用户上传的《职业生涯规划书》PDF，并提供极具洞察力的分析。
        
        你的回答要求：
        1. **拒绝废话**：直接指出文档中的核心竞争力、潜在风险和行动建议。
        2. **深度缩写**：不是简单的字数减少，而是逻辑提取。用‘现状-目标-路径’的结构来重构。
        3. **语气专业**：要像一位经验丰富的导师在跟学生谈心，既严谨又有启发性。
        4. **Markdown排版**：多用标题、加粗和列表，让回答赏心悦目。"""
    },
    {"role": "user", "content": f"请阅读以下内容并进行深度缩写和逻辑总结：\n\n{file_content}\n\n我的具体要求是：{user_question}"}
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
