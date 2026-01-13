import streamlit as st
from openai import OpenAI

# 1. 网页配置
st.set_page_config(page_title="小星专属AI助手", page_icon="🤖")
st.title("🚀 我的第一个 AI 网页应用")
st.caption("基于 DeepSeek 大模型开发")

# 2. 初始化 DeepSeek 客户端（记得换成你的 Key）
client = OpenAI(
    api_key="sk-0a477b0f3c874c8184f0a2ec168c3f2d", 
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏设置
with st.sidebar:
    st.header("设置")
    system_prompt = st.text_input("给 小星 一个身份", value="你是一个很有帮助的 AI 助手")
    st.divider()
    st.info("输入你的需求，小星 将为你提供建议。")

# 4. 网页主体交互界面
user_input = st.text_area("在此输入你的问题或需要润色的文字：", placeholder="例如：帮我写一个计算机专业的转正申请大纲...")

if st.button("开始生成"):
    if user_input:
        with st.spinner('小星 正在思考中...'):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                answer = response.choices[0].message.content
                st.subheader("✨ 小星 的建议：")
                st.markdown(answer)
            except Exception as e:
                st.error(f"连接失败：{e}")
    else:

        st.warning("请先输入内容哦！")
        
