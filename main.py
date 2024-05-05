import streamlit as st
from streamlit_option_menu import option_menu
import database as db
import validations as val
import time
import send_mail as sm
import hasher as hs
import cv2
import pandas as pd
from tempfile import NamedTemporaryFile
#---------------------------------------------------

page_title="Sign Language to Text"
page_icon=""
layout="centered"

st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
st.title(page_title+" "+page_icon)

#--------------------------------------------------
#hide the header and footer     

hide_ele="""
        <style>
        #Mainmenu {visibility:hidden;}
        footer {visibility:hidden;}
        header {visibility:hidden;}
        </style>
        """
st.markdown(hide_ele,unsafe_allow_html=True)

def set_default_bg(url):
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("{url}");
              background-size: 100% 120%;
             opacity: 0.8; 
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

#---------------------------------------------------
import numpy as np

import cv2
import os, sys
import time
import operator

from string import ascii_uppercase
import tkinter as tk
from PIL import Image, ImageTk
import enchant
from keras.models import model_from_json

hs = enchant.Dict('en_US')
vs = cv2.VideoCapture(0)
current_image = None
current_image2 = None
json_file = open("Models\model_new.json", "r")
model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(model_json)
loaded_model.load_weights("Models\model_new.h5")

json_file_dru = open("Models\model-bw_dru.json" , "r")
model_json_dru = json_file_dru.read()
json_file_dru.close()

loaded_model_dru = model_from_json(model_json_dru)
loaded_model_dru.load_weights("Models\model-bw_dru.h5")    
json_file_tkdi = open("Models\model-bw_tkdi.json" , "r")
model_json_tkdi = json_file_tkdi.read()
json_file_tkdi.close()

loaded_model_tkdi = model_from_json(model_json_tkdi)
loaded_model_tkdi.load_weights("Models\model-bw_tkdi.h5")
json_file_smn = open("Models\model-bw_smn.json" , "r")
model_json_smn = json_file_smn.read()
json_file_smn.close()

loaded_model_smn = model_from_json(model_json_smn)
loaded_model_smn.load_weights("Models\model-bw_smn.h5")

ct = {}
ct['blank'] = 0
blank_flag = 0

for i in ascii_uppercase:
    ct[i] = 0

print("Loaded model from disk")

stri = ""
word = " "
current_symbol = "Empty"
photo = "Empty"
data = [['--', '--', '--']]
columns = ['Prediction1', 'Prediction2', 'Prediction3']
preds = pd.DataFrame(data, columns=columns)
preds = preds.applymap(lambda x: x.encode() if isinstance(x, str) else x)
# video_loop()
if("key" not in st.session_state):
    so=st.button("Sign Out")
    if(so):
        st.session_state["key"] = "log_sign"
        st.experimental_rerun()
dat_fra=st.empty()
cs=st.empty()
cw=st.empty()
cst=st.empty()

for i in ascii_uppercase:
    ct[i] = 0

def updateword(word):
    cw.write("Current Word : "+word)
    time.sleep(0.1)

def updatetext(current_symbol):
    cs.write("Current Symbol : "+current_symbol)
    time.sleep(0.1)

def updatestri(stri):
    cst.write("Current String : "+stri)

def updatepreds(dataframe):
    dat_fra.dataframe(dataframe)

def predict(test_image):
    global word
    global stri
    test_image = cv2.resize(test_image, (128, 128))
    result = loaded_model.predict(test_image.reshape(1, 128, 128, 1))
    result_dru = loaded_model_dru.predict(test_image.reshape(1 , 128 , 128 , 1))
    result_tkdi = loaded_model_tkdi.predict(test_image.reshape(1 , 128 , 128 , 1))
    result_smn = loaded_model_smn.predict(test_image.reshape(1 , 128 , 128 , 1))
    prediction = {}
    prediction['blank'] = result[0][0]
    inde = 1
    for i in ascii_uppercase:
        prediction[i] = result[0][inde]
        inde += 1
    #LAYER 1
    prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)
    current_symbol = prediction[0][0]
    #LAYER 2
    if(current_symbol == 'D' or current_symbol == 'R' or current_symbol == 'U'):
        prediction = {}
        prediction['D'] = result_dru[0][0]
        prediction['R'] = result_dru[0][1]
        prediction['U'] = result_dru[0][2]
        prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)
        current_symbol = prediction[0][0]
    if(current_symbol == 'D' or current_symbol == 'I' or current_symbol == 'K' or current_symbol == 'T'):
            prediction = {}
            prediction['D'] = result_tkdi[0][0]
            prediction['I'] = result_tkdi[0][1]
            prediction['K'] = result_tkdi[0][2]
            prediction['T'] = result_tkdi[0][3]
            prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)
            current_symbol = prediction[0][0]
    if(current_symbol == 'M' or current_symbol == 'N' or current_symbol == 'S'):
            prediction1 = {}
            prediction1['M'] = result_smn[0][0]
            prediction1['N'] = result_smn[0][1]
            prediction1['S'] = result_smn[0][2]
            prediction1 = sorted(prediction1.items(), key = operator.itemgetter(1), reverse = True)
            if(prediction1[0][0] == 'S'):
                current_symbol = prediction1[0][0]
            else:
                current_symbol = prediction[0][0]
    
    if(current_symbol == 'blank'):
        for i in ascii_uppercase:
            ct[i] = 0
    ct[current_symbol] += 1
    if(ct[current_symbol] > 20):
        for i in ascii_uppercase:
            if i == current_symbol:
                continue
            tmp = ct[current_symbol] - ct[i]
            if tmp < 0:
                tmp *= -1
            if tmp <= 10:
                ct['blank'] = 0
                for i in ascii_uppercase:
                    ct[i] = 0
                return
        ct['blank'] = 0
        for i in ascii_uppercase:
            ct[i] = 0
        if current_symbol == 'blank':
            if blank_flag == 0:
                blank_flag = 1
                if len(stri) > 0:
                    stri += " "
                stri += word
                word = " "
        else:
            if(len(stri) > 7):
                stri = ""
            blank_flag = 0
            word += current_symbol
        updateword(word)
        updatestri(stri)
    print(word," || ",stri," || ",current_symbol)
    updatetext(current_symbol)
    

#---------------------------------------------------
curlogin=""
otp=""

def log_sign():
    selected=option_menu(
        menu_title=None,
        options=["Login","Signup","Admin"],
        icons=["bi bi-fingerprint","bi bi-pencil-square","bi bi-people"],
        orientation="horizontal"
    )
    global submit
    if(selected=="Login"):
        tab1,tab2=st.tabs(["Login","Forgot Password"])
        with tab1:
            with st.form("Login",clear_on_submit=True):
                st.header("Login")
                username=st.text_input("Email")
                password=st.text_input("Password",type="password")
                submit=st.form_submit_button()
                if(submit):
                    if(username=="" or password==""):
                        st.warning("Enter your login credentials")
                    else:
                        # password=hs.hasher(password)  
                        if(db.authenticate(username,password)):
                            st.session_state["curlogin"]=username
                            st.session_state["key"]="main"
                            with st.spinner('Logging In...'):
                                time.sleep(3)
                                st.success('Done!')
                            st.experimental_rerun()
                        else:
                            st.error("Please check your username / password ")
        with tab2:
            with st.form("Forgot Password",clear_on_submit=True):
                st.header("Forgot Password")
                email=st.text_input("Email")
                submit=st.form_submit_button()
                if(submit):
                    if(email==""):
                        st.warning("Enter your email")
                    elif(not db.emailexists(email)):
                        st.warning("User with associated email is not found,kindly recheck the email!")
                    else:
                        otp=sm.forgot_password(email)
                        db.forgot_pass(email,otp)
                        st.success("Check your email for password reset instructions!.")
                
    elif(selected=="Signup"):
         with st.form("Sign Up",clear_on_submit=False):
            st.header("Sign Up")
            email=st.text_input("Enter your email")
            number=st.text_input("Enter your Mobile Number")
            password=st.text_input("Enter your password",type="password")
            submit=st.form_submit_button()
            if(submit):
                dev=db.fetch_all_users()
                emails=[]
                numbers=[]
                for user in dev:
                    emails.append(user["email"])
                    numbers.append(user["number"])
                var=True
                if(val.validate_email(email)==False):
                    st.error("Enter email in a valid format like 'yourname@srmap.edu.in'")
                elif(email in emails):
                    st.error("email already exists!\nTry with another email !")
                elif(val.validate_mobile(number)==False):
                    st.error("Please Check your mobile Number")
                elif(number in numbers):
                    st.error("Phone number already exists\nTry with another number")
                elif(val.validate_password(password)==False):
                    st.error("Password must be between 6-20 characters in length and must have at least one Uppercase Letter , Lowercase letter , numeric character and A Special Symbol(#,@,$,%,^,&,+,=)")
                elif(var):
                    # password=hs.hasher(password)
                    db.insert_user(email,password,number)
                    st.success("Signed Up Successfully....Redirecting!!")
                    time.sleep(2)
                    st.session_state["curlogin"]=email
                    st.session_state["key"]="main"
                    st.experimental_rerun()
    
    elif selected=="Admin":
        with st.form("Admin Login",clear_on_submit=True):
            st.header("Admin Login")
            username=st.text_input("Username")
            password=st.text_input("Password",type="password")
            submit=st.form_submit_button()
            if(submit):
                if(username=="" or password==""):
                    st.warning("Enter your login credentials")
                else:
                    # password=hs.hasher(password)
                    if(db.ad_authenticate(username,password)):
                        st.session_state["curlogin"]=username
                        st.session_state["key"]="adminmain"
                        st.experimental_rerun()
                    else:
                        st.error("Please check your username / password ")
def main():
    opt=option_menu(
        menu_title=None,
        options=["Live Video Input","File Upload"],
        icons=["bi-play-circle","bi-database-fill"],
        orientation="horizontal"
    )

    if(opt=="Live Video Input"):
        run = st.checkbox('Start')
        FRAME_WINDOW = st.image([])
        cv2imgs=st.image([])
        curimgs=st.image([])
        resimgs=st.image([])
        if(run):
            with st.spinner('Loading ML Model...'):
                    time.sleep(3)
                    st.success('Loaded ML Model Successfully')
        camera = cv2.VideoCapture(0)
        while run:
            ok, frame = camera.read()
            if ok:
                cv2image = cv2.flip(frame, 1)
                x1 = int(0.5 * frame.shape[1])
                y1 = 10
                x2 = frame.shape[1] - 10
                y2 = int(0.5 * frame.shape[1])
                cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0) ,1)
                cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
                # cv2imgs.image(cv2image)
                current_image = Image.fromarray(cv2image)
                cv2image = cv2image[y1 : y2, x1 : x2]
                gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 2)
                th3 = cv2.adaptiveThreshold(blur, 255 ,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                FRAME_WINDOW.image(frame)
                curimgs.image(current_image)
                resimgs.image(res)  
                predict(res)
                predicts = hs.suggest(word)
                print(predicts)
                if(len(predicts) > 1):
                    preds['Prediction1'] = predicts[0]
                else:
                    preds['Prediction1']="--"
                if(len(predicts) > 2):
                    preds['Prediction2'] = predicts[1]
                else:

                    preds['Prediction2'] = "--"

                if(len(predicts) > 3):
                    preds['Prediction3']=predicts[2]
                else:
                    preds['Prediction3']="--"
                updatepreds(preds)

        
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            st.write('Stopped')
    else:
        uploaded_file = st.file_uploader("Choose a file",type=["mp4"])
        FRAME_WINDOW = st.image([])
        cv2imgs=st.image([])
        curimgs=st.image([])
        resimgs=st.image([])
        if uploaded_file:
            with NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            video_capture = cv2.VideoCapture(tmp_file_path)

            if not video_capture.isOpened():
                st.error("Error: Unable to open video file.")
                exit()
            while video_capture.isOpened():
                ret, frame = video_capture.read()
                if not ret:
                    print("Video ended.")
                    break
                else:
                    cv2image = cv2.flip(frame, 1)
                    x1 = int(0.5 * frame.shape[1])
                    y1 = 10
                    x2 = frame.shape[1] - 10
                    y2 = int(0.5 * frame.shape[1])
                    cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0) ,1)
                    cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
                    # cv2imgs.image(cv2image)
                    current_image = Image.fromarray(cv2image)
                    cv2image = cv2image[y1 : y2, x1 : x2]
                    gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (5, 5), 2)
                    th3 = cv2.adaptiveThreshold(blur, 255 ,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                    ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                    FRAME_WINDOW.image(frame)
                    curimgs.image(current_image)
                    resimgs.image(res)  
                    predict(res)
                    predicts = hs.suggest(word)
                    print(predicts)
                    if(len(predicts) > 1):
                        preds['Prediction1'] = predicts[0]
                    else:
                        preds['Prediction1']="--"
                    if(len(predicts) > 2):
                        preds['Prediction2'] = predicts[1]
                    else:

                        preds['Prediction2'] = "--"

                    if(len(predicts) > 3):
                        preds['Prediction3']=predicts[2]
                    else:
                        preds['Prediction3']="--"
                    updatepreds(preds)
                frame_count += 1


        

def admin():
    op=option_menu(
        menu_title=None,
            options=["Password Change","Delete User"],
            icons=["bi-shield-lock-fill","bi-trash-fill"],
            orientation="horizontal"
    )
    if(op=="Password Change"):
        with st.form("Password Change",clear_on_submit=False):
            st.header("Update Details")
            email=st.text_input("Enter your email")
            number=st.text_input("Enter your Mobile Number")
            password=st.text_input("Enter your password",type="password")
            submit=st.form_submit_button()
            if(submit):
                var=True
                if(val.validate_email(email)==False):
                        st.error("Enter email in a valid format like 'yourname@srmap.edu.in'")
                elif(val.validate_mobile(number)==False):
                        st.error("Please Check your mobile Number")
                elif(val.validate_password(password)==False):
                        st.error("Password must be between 6-20 characters in length and must have at least one Uppercase Letter , Lowercase letter , numeric character and A Special Symbol(#,@,$,%,^,&,+,=)")
                elif(var):
                    if(db.emailexists(email)):
                        # password=hs.hasher(password)
                        db.update_user(email,password,number)
                        st.success("Database Updated Successfully")
                    else:
                        st.error("No account found with the email address")
    else:
        with st.form("Delete Acc",clear_on_submit=True):
            st.header("Delete Account")
            email=st.text_input("Enter your email")
            submit=st.form_submit_button("Submit")
            if(submit):
                if(db.emailexists(email)):
                    db.delete_user(email)
                    st.success("User Account Deleted Successfully")
                else:
                    st.error("No Account found with the email address")

if "key" not in st.session_state:
    st.session_state["key"] = "log_sign"

if st.session_state["key"] == "log_sign":
    log_sign()

elif st.session_state["key"] == "adminmain":
    admin()

elif st.session_state["key"] == "main":
    main()