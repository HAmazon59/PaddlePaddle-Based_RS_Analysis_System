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
                if (color >= np.array([80, 80, 80, 255])).all():
                    img[h, w] = changed_color
                else:
                    img[h, w] = [0, 0, 0, 0]
    change_radios = change_pixel / all_pixel
    return img, change_radios


def show_radio(change_radios):
    if abs(change_radios) > 0.5:
        st.metric("变化程度：", "变化显著", str(change_radios * 100) + "%")
    elif abs(change_radios) > 0.1:
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


with st.sidebar:
    st.title("🌏遥感图像自动解译系统")
    choice = ['目标提取', '变化检测', '目标检测', '地物分类']
    tag = st.selectbox('功能:', choice)


if tag == choice[0]:
    st.title('目标提取')

    with st.expander("目标提取图像上传与预览"):
        uploaded_file1 = st.file_uploader("上传待提取图片", type=['png', 'jpg', 'jpeg'], help="允许上传png, jpg, jpeg格式图片")
        if uploaded_file1 is not None:
            file_bytes = np.asarray(bytearray(uploaded_file1.read()), dtype=np.uint8)
            opencv_image1 = cv2.imdecode(file_bytes, 1)
            st.image(opencv_image1, channels="BGR", caption='被检测图片')

    if uploaded_file1 is not None:

        with st.spinner("请稍候......"):
            predictor = Predictor("static_models/1", use_gpu=True)
            res = predictor.predict(opencv_image1)
            if isinstance(res,list):
                cm_1024x1024 = res[0]['label_map']
            elif isinstance(res,dict):
                cm_1024x1024 = res['label_map']
            image = (cm_1024x1024 * 255).astype('uint8')
            with st.expander("提取结果"):
                st.image(image, channels="RGB", caption='道路提取')
                cv2.imwrite('cache/mbtq.png', image)
                col1,col2=st.columns([2.07,3])
                with col2:
                    with open("cache/mbtq.png", "rb") as file:
                        btn = st.download_button(
                            label="下载该图片",
                            data=file,
                            file_name="mbtq.png",
                            mime="image/png"
                        )

        with st.spinner('可视化渲染......'):
            with st.expander("提取结果可视化", expanded=True):
                col_color, col_alpha = st.columns(2)
                with col_color:
                    color1 = st.color_picker('请选取可视化时的颜色(默认为蓝色):', '#0000ff')
                with col_alpha:
                    alpha1 = st.slider('选择可视化颜色的透明度:')
                    mat1 = 1 - alpha1 / 100
                    alpha1 = 255 - 2.55 * alpha1
                mbtq_img = cv2.imread('cache/mbtq.png')
                mbtq_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)  # 结果转为四通道RGBA
                b, g, r = hex2rgb(color1)
                new_transparent, x = black2transparent(mbtq_img, [r, g, b, alpha1])  # 获取被提取的道路像素，转为蓝色 --》可增加颜色选择模块
                cv2.imwrite('cache/new_transparent.png', new_transparent)
                new_transparent = cv2.imread('cache/new_transparent.png')
                out = cv2.addWeighted(opencv_image1, 1,
                                        new_transparent, mat1, 0)  # 前为原图像A，后为道路信息
                st.image(out, channels="BGR", caption='变化检测')
                cv2.imwrite('cache/mbtq_out.png', out)
                col1,col2=st.columns([2.07,3])
                with col2:
                    with open("cache/mbtq_out.png", "rb") as file:
                        btn = st.download_button(
                            label="下载该图片",
                            data=file,
                            file_name="mbtq_out.png",
                            mime="image/png"
                        )
        st.success("完成!")
    else:
        st.info("请上传提取图片。")


if tag == choice[1]:
    st.title('变化检测')
    
    with st.expander("双时相图像上传与预览"):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file1 = st.file_uploader("上传图片A", type=['png', 'jpg', 'jpeg'], help="允许上传png, jpg, jpeg格式图片")
            if uploaded_file1 is not None:
                file_bytes = np.asarray(bytearray(uploaded_file1.read()), dtype=np.uint8)
                bh1 = cv2.imdecode(file_bytes, 1)
                st.image(bh1, channels="BGR", caption='时相图A')
        with col2:
            uploaded_file2 = st.file_uploader("上传图片B", type=['png', 'jpg', 'jpeg'], help="允许上传png, jpg, jpeg格式图片")
            if uploaded_file2 is not None:
                file_bytes = np.asarray(bytearray(uploaded_file2.read()), dtype=np.uint8)
                bh2 = cv2.imdecode(file_bytes, 1)
                st.image(bh2, channels="BGR", caption='时相图B')


    if uploaded_file1 is not None and uploaded_file2 is not None:

        with st.spinner("请稍候......"):
            predictor = Predictor("static_models/4(1024x1024)", use_gpu=True)
            res = predictor.predict((bh1, bh2))
            if isinstance(res,list):
                cm_1024x1024 = res[0]['label_map']
            elif isinstance(res,dict):
                cm_1024x1024 = res['label_map']
            image = (cm_1024x1024 * 255).astype('uint8')
            cv2.imwrite('cache/bhjc.png', image)  # 结果保存
            with st.expander("检测结果"):
                st.image(image, caption='变化检测')
                col1,col2=st.columns([2.07,3])
                with col2:
                    with open("cache/bhjc.png", "rb") as file:
                        btn = st.download_button(
                            label="下载该图片",
                            data=file,
                            file_name="bhjc.png",
                            mime="image/png"
                        )

        with st.spinner('可视化渲染......'):
            with st.expander("提取结果可视化", expanded=True):
                col_color2, col_alpha2 = st.columns(2)
                with col_color2:
                    color2 = st.color_picker('请选取可视化时的颜色(默认为蓝色):', '#0000ff')
                with col_alpha2:
                    alpha2 = st.slider('选择可视化颜色的透明度:')
                    mat2 = 1 - alpha2 / 100
                    alpha2 = 255 - 2.55 * alpha2
                choose = st.radio("选择在哪张时相图上查看检测结果", ('时相图A', '时相图B'))
                white_img = cv2.imread('cache/bhjc.png')
                white_img = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)  # 结果转为四通道RGBA
                b, g, r = hex2rgb(color2)
                new_transparent, change_radio = black2transparent(white_img, [r, g, b, alpha2])  # 获取被提取的道路像素，转为蓝色 --》可增加颜色选择模块
                cv2.imwrite('cache/new_transparent.png', new_transparent)
                new_transparent = cv2.imread('cache/new_transparent.png')

                if choose == "时相图A":
                    if uploaded_file1 is not None and uploaded_file2 is not None:
                        show_radio(change_radio)
                        out = cv2.addWeighted(bh1, 1,new_transparent, mat2, 0)  # 前为原图像A，后为道路信息
                        st.image(out, channels="BGR", caption='变化检测')
                        cv2.imwrite('cache/bhjc_out_a.png', out)  # 结果保存
                        col1,col2=st.columns([2.07,3])
                        with col2:
                            with open("cache/bhjc_out_a.png", "rb") as file:
                                btn = st.download_button(
                                    label="下载该图片",
                                    data=file,
                                    file_name="bhjc_out_a.png",
                                    mime="image/png"
                                )
                        st.success('完成!')

                elif choose == "时相图B":
                    if uploaded_file1 is not None and uploaded_file2 is not None:
                        show_radio(change_radio)
                        out = cv2.addWeighted(bh2, 1, new_transparent, mat2, 0)  # 前为原图像A，后为道路信息
                        st.image(out, channels="BGR", caption='变化检测')
                        cv2.imwrite('cache/bhjc_out_b.png', out)  # 结果保存
                        col1,col2=st.columns([2.07,3])
                        with col2:
                            with open("cache/bhjc_out_b.png", "rb") as file:
                                btn = st.download_button(
                                    label="下载该图片",
                                    data=file,
                                    file_name="bhjc_out_b.png",
                                    mime="image/png"
                                )
                        st.success('完成!')
    else:
        st.info("请上传检测图片。")


if tag == choice[2]:
    st.title('目标检测')

    with st.expander('参数预设', expanded = True):
        add_radio = st.multiselect(
            "请选择要检测的目标",
            ["playground", "oiltank", "overpass", "aircraft"]
        )
        if "playground" in add_radio:
            slide_pla = st.slider('请选择playground置信度 (0~1)', max_value=1., min_value=0., step=0.01, value=0.5)
            playground["confidence"] = slide_pla
        if "oiltank" in add_radio:
            slide_oil = st.slider('请选择oiltank置信度 (0~1)', max_value=1., min_value=0., step=0.01, value=0.5)
            oiltank["confidence"] = slide_oil
        if "overpass" in add_radio:
            slide_ove = st.slider('请选择overpass置信度 (0~1)', max_value=1., min_value=0., step=0.01, value=0.5)
            overpass["confidence"] = slide_ove
        if "aircraft" in add_radio:
            slide_air = st.slider('请选择aircraft置信度 (0~1)', max_value=1., min_value=0., step=0.01, value=0.5)
            aircraft["confidence"] = slide_air
        if not add_radio:
            st.info("请选择检测目标！")

    # 文件上传模块
    with st.expander("目标检测图片上传与预览"):
        uploaded_file1 = st.file_uploader("上传待检测图片", type=['png', 'jpg', 'jpeg'], help="允许上传png, jpg, jpeg格式图片")
        if uploaded_file1 is not None:
            file_bytes = np.asarray(bytearray(uploaded_file1.read()), dtype=np.uint8)
            mb = cv2.imdecode(file_bytes, 1)
            st.image(mb, channels="BGR", caption='被检测图片')

        # 点击按钮
    if uploaded_file1 is not None and add_radio:

        with st.spinner("请稍候......"):
            res = mb
            flag = True  # 判断是否为第一个添加的目标锚框
            num = 0
            if "playground" in add_radio:
                flag = False
                predictor = Predictor("static_models/3/playground", use_gpu=True)  # 加载模型
                resu = predictor.predict(mb)  # 预测结果
                playground["count"] = count_res(resu, slide_pla)
                res = result(resu, mb, R, slide_pla)  # 在原图添加锚框
            if "oiltank" in add_radio:
                predictor = Predictor("static_models/3/oiltank", use_gpu=True)
                resu = predictor.predict(mb)
                oiltank["count"] = count_res(resu, slide_oil)
                if flag:
                    flag = False
                    res = result(resu, mb, G, slide_oil)  # 在原图添加锚框
                else:
                    res = result(resu, res, G, slide_oil)  # 在前面结果的基础上添加锚框
            if "overpass" in add_radio:
                predictor = Predictor("static_models/3/overpass", use_gpu=True)
                resu = predictor.predict(mb)
                overpass["count"] = count_res(resu, slide_ove)
                if flag:
                    flag = False
                    res = result(resu, mb, B, slide_ove)
                else:
                    res = result(resu, res, B, slide_ove)
            if "aircraft" in add_radio:
                predictor = Predictor("static_models/3/aircraft", use_gpu=True)
                resu = predictor.predict(mb)
                aircraft["count"] = count_res(resu, slide_air)
                if flag:
                    flag = False
                    res = result(resu, mb, Black, slide_air)
                else:
                    res = result(resu, res, Black, slide_air)
            vis = res

            if not flag:

                with st.expander("目标检测结果", expanded=True):
                    st.image(vis, channels="BGR", caption='目标检测')
                    st.subheader("检测结果：")
                    draw_counts_data(add_radio)
                    cv2.imwrite('cache/mbjc.png', vis)  # 保存以便下载
                    # 下载结果图片
                    col1,col2=st.columns([2.07,3])
                    with col2:
                        with open("cache/mbjc.png", "rb") as file:
                            btn = st.download_button(
                                label="下载该图片",
                                data=file,
                                file_name="mbjc.png",
                                mime="image/png"
                            )
                st.success("完成!")

    else:
        st.info('请添加预设参数并上传检测图片。')


if tag == choice[3]:
    st.title('地物分类')

    with st.expander("目标检测图片上传与预览"):
        uploaded_file1 = st.file_uploader("上传待分类图片", type=['png', 'jpg', 'jpeg'], help="允许上传png, jpg, jpeg格式图片")
        if uploaded_file1 is not None:
            file_bytes = np.asarray(bytearray(uploaded_file1.read()), dtype=np.uint8)
            dw = cv2.imdecode(file_bytes, 1)
            st.image(dw, channels="BGR", caption='被分类图片')

    if uploaded_file1 is not None:        
        with st.spinner("请稍候......"):
            with st.expander('地物分类结果'):
                predictor = Predictor("static_models/2", use_gpu=True)
                res = predictor.predict(dw)
                if isinstance(res,list):
                    cm_1024x1024 = res[0]['label_map']
                elif isinstance(res,dict):
                    cm_1024x1024 = res['label_map']
                im = cm_1024x1024.astype('uint8')
                lut = get_lut()
                if isinstance(im, str):
                    im = cv2.imread(im, cv2.IMREAD_COLOR)
                if lut is not None:
                    if im.ndim == 3:
                        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    im = lut[im]
                else:
                    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                
                col1,col2,col3=st.columns([1,2,1])
                with col2:
                    st.image(im, caption='地物分类')
                    st.image('static_data/图例.png',caption='图例')
                cv2.imwrite('cache/dwfl.png', im)
                col1,col2=st.columns([2.07,3])
                with col2:
                    with open("cache/dwfl.png", "rb") as file:
                        btn = st.download_button(
                            label="下载该图片",
                            data=file,
                            file_name="dwfl.png",
                            mime="image/png"
                        )
        st.success("完成!")
    
    else:
        st.info("请上传分类图片。")


with st.sidebar:
    st.subheader('便签')
    st.text_area(label='随便写点什么吧!', value='空空如也~', height=30)
    st.markdown("[访问 AI Studio 官网](https://aistudio.baidu.com/aistudio/index '飞浆AI Studio')")
    st.markdown("[访问 飞浆 官网](https://www.paddlepaddle.org.cn/ '飞浆PaddlePaddle')")
