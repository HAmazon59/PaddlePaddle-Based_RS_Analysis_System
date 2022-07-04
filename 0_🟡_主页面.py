import streamlit as st

st.set_page_config(
    page_title="遥感图像自动解译系统 ",
    page_icon="🚀"
)

hide_streamlit_style = """
            <style>
            footer {
	        visibility: hidden;
	            }
            footer:after {
	            content:'遥感图片分析系统 developed by 极客制造';  
				font-family: 'Microsoft YaHei';
	            visibility: visible;
	            display: block;
	            position: relative;
	            padding: 5px;
	            top: 2px;
                    }
            </style>
            """

st.markdown(hide_streamlit_style,unsafe_allow_html=True)

st.sidebar.success("请选择上方任意功能~")
st.subheader('欢迎使用')
st.header('基于百度飞浆的遥感图像自动解译系统！')
st.image('./static_data/tp1.png')

with st.sidebar:
    st.markdown("[访问 AI Studio 官网](https://aistudio.baidu.com/aistudio/index '飞浆AI Studio')")
    st.markdown("[访问 飞浆 官网](https://www.paddlepaddle.org.cn/ '飞浆PaddlePaddle')")