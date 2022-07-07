import streamlit as st
import paddle

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
	            content:'遥感图片解译系统 developed by 极客智造';  
				font-family: 'Microsoft YaHei';
	            visibility: visible;
	            display: block;
	            position: relative;
	            padding: 5px;
	            top: 2px;
                    }
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if 'computer_type' not in st.session_state:
    st.session_state.computer_type = paddle.is_compiled_with_cuda()
# print(st.session_state.computer_type)

st.sidebar.success("请选择上方任意功能~")
st.subheader('欢迎使用')
st.header('基于百度飞桨的遥感图像自动解译系统！')
st.image('./static_data/fm-o.png')


with st.sidebar:
    st.subheader('便签')
    st.text_area(label='随便写点什么吧!', value='空空如也~', height=30)
    st.markdown("[访问 AI Studio 官网](https://aistudio.baidu.com/aistudio/index '飞桨AI Studio')")
    st.markdown("[访问 飞桨 官网](https://www.paddlepaddle.org.cn/ '飞桨PaddlePaddle')")