import pickle
from models import *
import streamlit as st
import torch,torchvision
import os
import cv2
import torch
import numpy as np
from datetime import datetime,timedelta
import torch.nn.functional as F
from torchvision.transforms.functional import normalize
torch.set_warn_always(False)
st.set_page_config(page_title="打卡APP", page_icon=":material/edit:")
def login():
    st.header("登录")
    text = st.empty()
    def checkN(x):
        username = text.text_input("请输入你的姓名:", value="", key=x)
        if username != "":
            
            if not username in student_names:
                #text.write("<font style='red'>无效姓名</font>",key=x)
                checkN(x+1)
            else:
                st.session_state.username_flag=True
                st.session_state.user = username
                return
    
    student_names = ["李天恩",st.secrets["ADMIN_USERNAME"]]
    checkN(0)
    if st.session_state.username_flag:
        st.rerun()
# Function to find all files N days after the date the file was stored
def find_files(usr_name, days_list):
    # List to store the matching files
    matching_files = []
    
    for filename in os.listdir():
        # Extract date from filename
        file_date_str = filename
        #st.write(file_date_str.split("."))

        if file_date_str.split("-")[0] == usr_name:
            

            file_date = datetime.strptime(file_date_str.split("-")[1].replace(".png",""), '%Y_%m_%d')
            # Check if file matches any of the days in the list
            for days in days_list:
                target_date = file_date + timedelta(days=days)
                target_date_str = target_date.strftime('%Y_%m_%d')
                #st.write(target_date_str+".png")
                
                if os.path.exists(f"{usr_name}-{target_date_str}.png"):
                    matching_files.append([f"{usr_name}-{target_date_str}.png",days])

    return matching_files


def clearUp(dataset_path):
    for datas in dataset_path:
        if datas[1] == 15:
            os.remove(datas[0])
    return True
def logout():
    st.session_state.username_flag=False
    st.session_state.user = ""
    st.rerun()
if "install_font" not in st.session_state:
    st.session_state.install_font = False
if "username_flag" not in st.session_state:
    st.session_state.username_flag = False

if "input_size" not in st.session_state:
    st.session_state.input_size = [1024, 1024]
@st.cache_resource  # 👈 Add the caching decorator
def load_model():
    net = ISNetDIS()
    net.load_state_dict(torch.load("isnet.pth", map_location="cpu"))
    net.eval()
    return net
if "progress" not in st.session_state:
    st.session_state.progress = 0
if st.session_state.username_flag:
    if st.session_state.user != st.secrets["ADMIN_USERNAME"]:
        st.session_state.net = load_model()
        dataset_path=f"{st.session_state.user}_wr"  #Your dataset path
        model_path="isnet.pth"  # the model path
        result_path=f"{st.session_state.user}_res"  #The folder path that you want to save the results
        if os.path.exists(f"{st.session_state.user}_cal.pkl"):
            array = pickle.load(open(f"{st.session_state.user}_cal.pkl", "rb"))
            for x in array['打卡状态']:
              if x == "✅":
                st.session_state.progress+=1
        st.write(st.session_state.user != st.secrets["ADMIN_USERNAME"])
        st.markdown(f"<p style='text-align: left; position: absolute; top:15px;'>第{(st.session_state.progress//10)*10}天</p>", unsafe_allow_html = True)
        st.markdown(f"<p style='text-align: right;'>第{(st.session_state.progress//10+1)*10}天</p>", unsafe_allow_html = True)
        st.progress(st.session_state.progress*10)
    
        #st.title(f"你好！{st.session_state.user}")
        times = [1,2,4,7,15]
    
        review_list = find_files(st.session_state.user, times)
        
        #os.system("ls")
        if len(review_list) == 0:
            delete_page = st.Page("wrong_questions.py", title="错题分析", icon=":material/notification_important:")
            create_page = st.Page(logout, title="登出", icon=":material/logout:")
            learning = st.Page("learning_curve.py", title="记忆曲线", icon="📉")
            calendar = st.Page("calender.py", title="打卡记录", icon = ":material/dashboard:")
            pg = st.navigation({f"{st.session_state.user}的":[calendar,delete_page],f"{st.session_state.user}的账号":[create_page]})

    else:
        pg = st.navigation([st.Page('admin.py')])
else:
    pg = st.navigation([st.Page(login)])
pg.run()
