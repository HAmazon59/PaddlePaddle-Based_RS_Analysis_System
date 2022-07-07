import streamlit as st
from paddlers.deploy import Predictor
from paddlers.tasks.utils.visualize import visualize_detection
import numpy as np
import cv2


def hex2rgb(hex):
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    return r, g, b


def black2transparent(img, changed_color=[255, 0, 0, 255]):
    height, width, channel = img.shape
    all_pixel = height * width
    change_pixel = 0.
    for h in range(height):
        for w in range(width):
            color = img[h, w]
            if (color == np.array([0, 0, 0, 255])).all():

                img[h, w] = [0, 0, 0, 0]
            else:
                change_pixel = change_pixel + 1
            if (color >= np.array([120, 120, 120, 255])).all():
                img[h, w] = changed_color
    change_radios = change_pixel / all_pixel
    return img, change_radios


def show_radio(change_radios):
    if change_radios > 0.5:
        st.metric("变化程度：", "变化显著", str(change_radios * 100) + "%")
    elif change_radios > 0.1:
        st.metric("变化程度：", "变化一般", str(change_radios * 100) + "%")
    else:
        st.metric("变化程度：", "变化较少", str(change_radios * 100) + "%")
    return 0


# 该函数用于添加目标锚框，参数：（预测框， 原图， 颜色， 置信度）
def result(target, ori, color, threshold):
    if len(target) > 0:
        result_t = visualize_detection(
            ori, target,
            color=color,
            threshold=threshold, save_dir=None
        )
    return result_t


# 该函数用于获取目标锚框的个数，参数（预测结果， 置信度）
def count_res(checked, confidence):
    nums = 0
    for i in range(0, len(checked)):
        if resu[i]["score"] >= confidence:
            nums = nums + 1
    return nums


def draw_counts_data(select):
    if len(select) > 1:
        code = ""
        for i in range(1, len(select)):
            code = code + "col"
            code = code + str(i)+", "
        code = code + "col" + str(len(select))
        code = code + "= st.columns("+str(len(select))+")"
        exec(code)
        sums = 1
        if "playground" in add_radio:
            exec("col%s.metric('playground', '数量:%s', '置信度%s')" % (sums, playground["count"], playground["confidence"]))
            sums = sums + 1
        if "oiltank" in add_radio:
            exec("col%s.metric('oiltank', '数量:%s', '置信度%s')" % (sums, oiltank["count"], oiltank["confidence"]))
            sums = sums + 1
        if "overpass" in add_radio:
            exec("col%s.metric('overpass', '数量:%s', '置信度%s')" % (sums, overpass["count"], overpass["confidence"]))
            sums = sums + 1
        if "aircraft" in add_radio:
            exec("col%s.metric('aircraft', '数量:%s', '置信度%s')" % (sums, aircraft["count"], aircraft["confidence"]))
            sums = sums + 1
    else:
        if "playground" in add_radio:
            exec("st.metric('playground', '数量:%s', '置信度%s')" % (playground["count"], playground["confidence"]))
        if "oiltank" in add_radio:
            exec("st.metric('oiltank', '数量:%s', '置信度%s')" % (oiltank["count"], oiltank["confidence"]))
        if "overpass" in add_radio:
            exec("st.metric('overpass', '数量:%s', '置信度%s')" % (overpass["count"], overpass["confidence"]))
        if "aircraft" in add_radio:
            exec("st.metric('aircraft', '数量:%s', '置信度%s')" % (aircraft["count"], aircraft["confidence"]))
    return 0


def get_lut():
    lut = np.zeros((256, 3), dtype=np.uint8)
    lut[0] = [255, 0, 0]
    lut[1] = [30, 255, 142]
    lut[2] = [60, 0, 255]
    lut[3] = [255, 222, 0]
    lut[4] = [0, 0, 0]
    return lut


# 用于记录示例前进一步（全局变量，刷新网页恢复）
def nextstep(step, judge):
    if eval("st.session_state.%s" % step) == judge:
        if st.button("下一步"):
            exec("st.session_state.%s = st.session_state.%s + 1" % (step, step))
            st.experimental_rerun()


#  颜色常量设定
R = np.asarray([[255, 0, 0]], dtype=np.uint8)  # 红
G = np.asarray([[0, 255, 0]], dtype=np.uint8)  # 绿
B = np.asarray([[0, 0, 255]], dtype=np.uint8)  # 蓝
W = np.asarray([[255, 255, 255]], dtype=np.uint8)  # 白
Black = np.asarray([[0, 0, 0]], dtype=np.uint8)  # 黑
playground = {"name": "playground", "confidence": 0.5, "count": 0}
oiltank = {"name": "oiltank", "confidence": 0.5, "count": 0}
overpass = {"name": "overpass", "confidence": 0.5, "count": 0}
aircraft = {"name": "aircraft", "confidence": 0.5, "count": 0}

st.set_page_config(page_title="功能示例", page_icon='static_data/变化检测.png')

# 用于记录示例进行到哪一步
if 'step1' not in st.session_state:
    st.session_state.step1 = 1
if 'step2' not in st.session_state:
    st.session_state.step2 = 1
if 'step3' not in st.session_state:
    st.session_state.step3 = 1
if 'step4' not in st.session_state:
    st.session_state.step4 = 1

#  模型地址设定
Model_address_TargetExtraction = "static_models/TargetExtraction"  # 目标提取
Model_address_ChangeDetection = "static_models/ChangeDetection"  # 变化检测
Model_address_TargetDetection = "static_models/TargetDetection"  # 目标检测
Model_address_TerrainClassification = "static_models/TerrainClassification"  # 地物分类

with st.sidebar:
    st.title("🌏遥感图像自动解译系统--功能示例")
    choice1 = ['目标提取', '变化检测', '目标检测', '地物分类', '使用说明书']
    tag = st.selectbox('功能:', choice1)


if tag == choice1[0]:
    st.title('目标提取')
    st.write('本模块是对目标提取功能的实例展示，本实例以下图为例（实际使用过程中均可实现用户上传数据），展示如何通过简单的参数调控实现目标提取及其可视化。')
    st.subheader('1.点击即可展开或关闭测试图像的预览')
    with st.expander("目标提取测试图像预览"):
        img_mbtq = cv2.imread('static_data/example/mbtq.png')
        st.image(img_mbtq, channels="BGR", caption='目标提取测试图像')
    nextstep("step1", 1)
    if st.session_state.step1 > 1:
        st.write("在读取图片后，将进行目标提取（道路提取），并生成黑白的结果图，黑色为非目标，白色为被提取目标。")
        st.subheader("2.点击即可展开或关闭提取结果图像的预览")
        with st.expander("目标提取结果图像预览"):
            img_mbtq_result = cv2.imread('static_data/example/mbtq-result.png')
            st.image(img_mbtq_result, channels="BGR", caption='目标提取结果图像')
    nextstep("step1", 2)
    if st.session_state.step1 > 2:
        st.write("在获取完提取结果后，本系统提供了结果可视化方法，在下方可对相应参数进行调整，并查看可视化结果。")
        st.subheader("3.点击色块可调整可视化结果中目标的颜色，滑动滑块可调整可视化结果中目标的透明度")
        with st.spinner('可视化渲染......'):
            with st.expander("提取结果可视化", expanded=True):
                col_color, col_alpha = st.columns(2)
                with col_color:
                    color1 = st.color_picker('请选取可视化时的颜色(默认为蓝色):', '#0000ff')
                with col_alpha:
                    alpha1 = st.slider('选择可视化颜色的透明度(默认为0，不透明):')
                    mat1 = 1 - alpha1 / 100
                    alpha1 = 255 - 2.55 * alpha1
                if color1 == '#0000ff' and alpha1 == 255:
                    st.image('static_data/example/mbtq_view.png', caption='提取结果可视化')
                else:
                    mbtq_result_4 = cv2.cvtColor(img_mbtq_result, cv2.COLOR_BGR2RGBA)  # 结果转为四通道RGBA
                    b, g, r = hex2rgb(color1)
                    new_transparent, x = black2transparent(mbtq_result_4, [r, g, b, alpha1])  # 获取被提取的道路像素，转为蓝色 --》可增加颜色选择模块
                    cv2.imwrite('cache/new_transparent.png', new_transparent)
                    new_transparent = cv2.imread('cache/new_transparent.png')
                    out = cv2.addWeighted(img_mbtq, 1, new_transparent, mat1, 0)  # 前为原图像A，后为道路信息
                    st.image(out, channels="BGR", caption='提取结果可视化')


if tag == choice1[1]:
    st.title('变化检测')
    st.write('本模块是对变化检测功能的实例展示，本实例以下图为例（实际使用过程中均可实现用户上传数据），展示如何通过简单的参数调控实现变化检测及其可视化。')
    st.subheader('1.点击即可展开或关闭测试图像的预览')
    with st.expander("变化检测测试图像预览"):
        img_bhjc_A = cv2.imread('static_data/example/test_7A.png')
        img_bhjc_B = cv2.imread('static_data/example/test_7B.png')
        colA, colB = st.columns(2)
        with colA:
            st.image(img_bhjc_A, channels="BGR", caption='变化检测测试图像时相图A')
        with colB:
            st.image(img_bhjc_B, channels="BGR", caption='变化检测测试图像时相图B')
    nextstep("step2", 1)
    if st.session_state.step2 > 1:
        st.write("在读取图片后，将进行变化检测（建筑物检测），并生成黑白的结果图，黑色为非目标，白色为变化的建筑物。")
        st.subheader("2.点击即可展开或关闭检测结果图像的预览")
        with st.expander("变化检测结果图像预览"):
            bhjc_result = cv2.imread('static_data/example/bhjc-result.png')
            st.image(bhjc_result, channels="BGR", caption='变化检测结果图像')
    nextstep("step2", 2)
    if st.session_state.step2 > 2:
        st.write("在获取完变化检测结果后，本系统提供了结果可视化方法，在下方可对相应参数进行调整，并查看可视化结果。")
        st.subheader("3.点击色块可调整可视化结果中变化部分的颜色，滑动滑块可调整可视化结果中变化部分显示的透明度")
        with st.spinner('可视化渲染......'):
            with st.expander("检测结果可视化", expanded=True):
                col_color2, col_alpha2, col_AB = st.columns([2, 2, 1.5])
                with col_color2:
                    color2 = st.color_picker('请选取可视化时的颜色(默认为蓝色):', '#0000ff')
                with col_alpha2:
                    alpha2 = st.slider('选择可视化颜色的透明度(默认为0，不透明):')
                    mat2 = 1 - alpha2 / 100
                    alpha2 = 255 - 2.55 * alpha2
                with col_AB:
                    choose_bhjc = st.radio("选择需要可视化的图像", ('时相图A', '时相图B'))
                st.markdown("**本系统同时对变化占比进行了计算，并给出了评价，结果如下所示。**")
                if color2 == '#0000ff' and alpha2 == 255:
                    if choose_bhjc == "时相图A":
                        st.metric("变化程度：", "变化较少", "4.0313720703125%")
                        st.image('static_data/example/bhjc_out_a.png', caption='变化检测结果可视化')
                    elif choose_bhjc == "时相图B":
                        st.metric("变化程度：", "变化较少", "4.0313720703125%")
                        st.image('static_data/example/bhjc_out_b.png', caption='变化检测结果可视化')
                else:
                    bhjc_result_4 = cv2.cvtColor(bhjc_result, cv2.COLOR_BGR2BGRA)  # 结果转为四通道RGBA
                    b, g, r = hex2rgb(color2)
                    new_transparent, change_radio = black2transparent(bhjc_result_4, [r, g, b, alpha2])  # 获取被提取的像素
                    cv2.imwrite('cache/new_transparent.png', new_transparent)
                    new_transparent = cv2.imread('cache/new_transparent.png')
                    if choose_bhjc == "时相图A":
                        show_radio(change_radio)
                        out = cv2.addWeighted(img_bhjc_A, 1, new_transparent, mat2, 0)  # 前为原图像A，后为提取信息
                        st.image(out, channels="BGR", caption='变化检测结果可视化')
                    elif choose_bhjc == "时相图B":
                        show_radio(change_radio)
                        out = cv2.addWeighted(img_bhjc_B, 1, new_transparent, mat2, 0)  # 前为原图像B，后为提取信息
                        st.image(out, channels="BGR", caption='变化检测结果可视化')


if tag == choice1[2]:
    st.title('目标检测')
    st.write('本模块是对目标检测功能的实例展示，本实例以下图为例（实际使用过程中均可实现用户上传数据和更换检测对象），展示如何通过简单的参数调控实现目标检测及其可视化。')
    st.subheader('1.点击即可展开或关闭测试图像的预览')
    with st.expander("目标检测测试图像预览"):
        img_mbjc = cv2.imread('static_data/example/mbjc2.jpg')
        st.image(img_mbjc, channels="BGR", caption='目标检测测试图像')
    nextstep("step3", 1)
    if st.session_state.step3 > 1:
        st.write("在读取图片后，将进行目标检测（这里以油桶检测为例），在原图像上生成锚框和预测概率，不同的检测对象颜色不同。")
        st.subheader("2.滑动以改变目标检测置信度:")
        slide_oil = st.slider('请选择oiltank置信度 (0~1)', max_value=1., min_value=0., step=0.01, value=0.5)
        oiltank["confidence"] = slide_oil
        st.subheader("3.点击即可展开或关闭检测结果图像的预览")
        with st.spinner('可视化渲染......'):
            with st.expander("目标检测测试结果图像可视化", expanded=True):
                if slide_oil == 0.5:
                    st.subheader("检测结果：")
                    st.metric("oiltank", "数量:16", "置信度0.5")
                    st.image('static_data/example/mbjc-result.png', caption='目标检测结果可视化')
                else:
                    predictor = Predictor(Model_address_TargetDetection+"/oiltank", use_gpu=st.session_state.computer_type)
                    resu = predictor.predict(img_mbjc)
                    oiltank["count"] = count_res(resu, slide_oil)
                    res_mbjc = result(resu, img_mbjc, G, slide_oil)
                    st.subheader("检测结果：")
                    add_radio = ["oiltank"]
                    draw_counts_data(["oiltank"])
                    st.image(res_mbjc, channels="BGR", caption='目标检测结果可视化')


if tag == choice1[3]:
    st.title('地物分类')
    st.write('本模块是对地物分类功能的实例展示，本实例以下图为例（实际使用过程中均可实现用户上传数据），展示如何实现地物分类及其可视化。')
    st.subheader('1.点击即可展开或关闭测试图像的预览')
    with st.expander("地物分类测试图像预览"):
        colc1, colc2, colc3 = st.columns([1, 1.3, 1])
        with colc2:
            img_mbjc = cv2.imread('static_data/example/217.jpg')
            st.image(img_mbjc, channels="BGR", caption='地物分类测试图像')
    nextstep("step4", 1)
    if st.session_state.step4 > 1:
        st.write("读取图片后，将对图片进行地物分类，具体分类如图例所示。")
        st.subheader("2.点击即可展开或关闭分类结果图像的预览")
        with st.expander("地物分类结果图像预览"):
            cold1, cold2, cold3 = st.columns([1, 1.3, 1])
            with cold2:
                st.image('static_data/example/dwfl-result.png')
                st.image('static_data/图例.png', caption='地物分类结果可视化及图例')


if tag == choice1[4]:
    st.markdown('''
    # 使用说明书

本系统围绕 [***PaddleRS***](https://github.com/PaddleCV-SIG/PaddleRS) 框架进行开发，针对各类的遥感图片进行处理操作。功能分为目标提取，变化检测，目标检测，地物分类四个模块。

## 目标提取

本功能用于提取图片中的道路信息。基于上传的遥感图像，生成道路的分割图片，并在原图中渲染出可视化结果。

### 图片上传与预览：

1.	单击文件上传图标，选择上传一张遥感图片
   注：为保证结果有效性，请保证遥感图片中含有“道路”要素。
2.	图片格式支持png, jpg, jpeg。
3.	上传成功后会在下方自动生成预览图片。
4.	图片上传后将自动对图片进行分析。

### 提取结果：

1.	在“请稍后”图标消失后，单击“提取结果”即可展开扩展框查看道路提取图片。
2.	单击图片下方“下载该图片”按钮，即可下载生成的道路提取原始输出图片。
   提取结果可视化：
3.	在“可视化结果渲染”图标消失后，会自动展示可视化道路提取图片。
4.	可视化颜色默认为蓝色，单击颜色框即可选择调整将颜色修改为需要的颜色。
5.	可视化颜色透明度默认为0，拖动滑动条可以修改颜色透明度。
6.	每次修改颜色或透明度后需要重新渲染图片。
7.	单击图片下方“下载该图片”按钮，即可下载生成的道路提取可视化图片。

## 变化检测

本功能用于检测同一地点不同时期的遥感图片中的变化信息。基于上传的两张遥感图像，生成变化区块的图片，并在原图中渲染出可视化结果。

### 图片上传与预览：

1.	单击文件上传图标，左右各选择上传一张遥感图片。
   注：两张图片应该是同一地点不同时期下的遥感图片。
2.	图片格式支持png, jpg, jpeg。
3.	上传成功后会在下方自动生成预览图片。
4.	图片上传后将自动对图片进行分析。

### 检测结果：

1.	在“请稍后”图标消失后，单击“提取结果”即可展开扩展框查看变化检测图片。
2.	单击图片下方“下载该图片”按钮，即可下载生成的变化检测原始输出图片。

### 提取结果可视化：

1.	在“可视化结果渲染”图标消失后，会自动展示可视化变化检测图片。
2.	可视化颜色默认为蓝色，单击颜色框即可选择调整将颜色修改为需要的颜色。
3.	可视化颜色透明度默认为0，拖动滑动条可以修改颜色透明度。
4.	默认在时相图A上进行可视化，选择时相图B后即可将可视化结果生成在第二张上传的图片上。
5.	每次修改颜色、透明度、时相图后需要重新渲染图片。
6.	单击图片下方“下载该图片”按钮，即可下载生成的变化检测可视化图片。

## 目标检测

本功能用于检测遥感图片中的特定目标，目标包括操场，油罐，立交与飞机。基于上传的遥感图像，输出标注出需要的目标后的图像。

### 参数预设：

1.	选择需要检测的目标，可多选。
2.	对选择的目标进行置信度设置，输出中仅显示超过预设置信度的标注。

### 图片上传与预览：

1.	单击文件上传图标，选择上传一张遥感图片
2.	图片格式支持png, jpg, jpeg。
3.	上传成功后会在下方自动生成预览图片。
4.	图片上传并设置参数后将自动对图片进行分析。

### 检测结果：

1.	在“请稍后”图标消失后，即可查看变化检测图片以及目标数量与置信度。
2.	单击图片下方“下载该图片”按钮，即可下载生成的目标检测输出图片。

## 地物分类

本功能用于分类图片中的特定地形，地形包括草地，林场，水域，裸地，背景。基于上传的遥感图像，输出地物分类后的分块结果图像。

### 图片上传与预览：

1.	单击文件上传图标，选择上传一张遥感图片
2.	图片格式支持png, jpg, jpeg。
3.	上传成功后会在下方自动生成预览图片。
4.	图片上传后将自动对图片进行分析。

### 分类结果：

1.	在“请稍后”图标消失后，即可查看地物分类图片以及相关图例。
2.	单击图片下方“下载该图片”按钮，即可下载生成的地物分类输出图片。






    
    ''')


with st.sidebar:
    st.subheader('便签')
    st.text_area(label='随便写点什么吧!', value='空空如也~', height=30)
    st.markdown("[访问 AI Studio 官网](https://aistudio.baidu.com/aistudio/index '飞桨AI Studio')")
    st.markdown("[访问 飞桨 官网](https://www.paddlepaddle.org.cn/ '飞桨PaddlePaddle')")