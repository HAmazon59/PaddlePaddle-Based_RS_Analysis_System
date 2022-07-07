import streamlit as st

st.set_page_config(page_title="功能介绍", page_icon='static_data/变化检测.png')

with st.sidebar:
    st.title("🏝️遥感图像自动解译系统--功能介绍")
    choice3 = ['目标提取', '变化检测', '目标检测', '地物分类']
    tag = st.selectbox('功能:', choice3)

if tag == choice3[0]:
    st.image('static_data/mbtq.png')
    st.subheader("目标提取")
    st.markdown('**目标提取**是指单幅图像或序列图像中将感兴趣的目标与背景分割开来，从图像中识别和解译有意义的物体实体而提取不同的图像特征的操作。'
                ' 目标提取是一个至关重要的环节，它直接决定后续识别和跟踪性能的好坏。 现阶段，目标提取的应用范围很广，在计算机视觉提取人脸'
                '特征和指纹等，在摄影测量与遥感中，用于特征点线的提取来进行影像匹配和三维建模等。 目标提取是指单幅图像或序列图像中将'
                '感兴趣的目标与背景分割开来，从图像中识别和解译有意义的物体实体而提取不同的图像特征的操作。')
if tag == choice3[1]:
    st.image('static_data/bhjc.png')
    st.subheader("变化检测")
    st.markdown('**变化检测**是遥感对地观测技术研究领域一个热点问题，具有重大的研究意义和应用价值。遥感变化检测的正式概念是：利用多时相遥感数据，'
                '采用多种图像处理和模式识别方法提取变化信息，并定量分析和确定地表变化的特征与过程。'
                '近年来，变化检测在土地资源管理、农林监测、自然灾害监测与评价等方面有'
                '着重要的应用。然而面对呈爆炸性增长的遥感数据，我们需要高效并且自动的进行变化信息的分析和理解，这成为遥感技术领域一个重要的研究热点。')

if tag == choice3[2]:
    st.image('static_data/mbjc.png')
    st.subheader("目标检测")
    st.markdown('**目标检测**的任务是找出图像中所有感兴趣的目标（物体），确定它们的类别和位置，是计算机视觉领域的核心问题之一。'
                '由于各类物体有不同的外观、形状和姿态，加上成像时光照、遮挡等因素的干扰，目标检测一直是计算机视觉领域最具有挑战性的问题。')
    st.write("在计算机视觉众多的技术领域中，目标检测也是一项非常基础的任务，图像分割、物体追踪、关键点检测等通常都要"
             "依赖于目标检测。在目标检测时，由于每张图像中物体的数量、大小及姿态各有不同，也就是非结构化的输出，这是与图像分类非常不同的一点，"
             "并且物体时常会有遮挡截断，所以物体检测技术也极富挑战性，从诞生以来始终是研究学者最为关注的焦点领域之一。")
if tag == choice3[3]:
    st.image('static_data/dwfl.png')
    st.subheader("地物分类")
    st.markdown('**地物分类**是一种计算机利用统计方法,将遥感图象相似亮度范围的像元归类的方法。地物分类实现了高光谱分辨率和高精度空间分辨率'
                '对地物直接识别的能力，对地质的蚀变信息的分类识别有良好效果。')


with st.sidebar:
    st.subheader('便签')
    st.text_area(label='随便写点什么吧!', value='空空如也~', height=30)
    st.markdown("[访问 AI Studio 官网](https://aistudio.baidu.com/aistudio/index '飞桨AI Studio')")
    st.markdown("[访问 飞桨 官网](https://www.paddlepaddle.org.cn/ '飞桨PaddlePaddle')")