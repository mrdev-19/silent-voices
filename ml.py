import streamlit as st
from streamlit_option_menu import option_menu
import database as db
import validations as val
import time
import send_mail as sm
import hasher as hs
import cv2
import numpy as np
import operator
from string import ascii_uppercase
from PIL import Image
from keras.models import model_from_json
import enchant

#---------------------------------------------------
# page config settings:

page_title = "Sign Language to Text"
page_icon = ""
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

#--------------------------------------------------
# hide the header and footer
hide_ele = """
        <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        header {visibility:hidden;}
        </style>
        """
st.markdown(hide_ele, unsafe_allow_html=True)
#---------------------------------------------------

vs = cv2.VideoCapture(0)
json_file = open("Models\model_new.json", "r")
model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(model_json)
loaded_model.load_weights("Models\model_new.h5")

json_file_dru = open("Models\model-bw_dru.json", "r")
model_json_dru = json_file_dru.read()
json_file_dru.close()
loaded_model_dru = model_from_json(model_json_dru)
loaded_model_dru.load_weights("Models\model-bw_dru.h5")

json_file_tkdi = open("Models\model-bw_tkdi.json", "r")
model_json_tkdi = json_file_tkdi.read()
json_file_tkdi.close()
loaded_model_tkdi = model_from_json(model_json_tkdi)
loaded_model_tkdi.load_weights("Models\model-bw_tkdi.h5")

json_file_smn = open("Models\model-bw_smn.json", "r")
model_json_smn = json_file_smn.read()
json_file_smn.close()
loaded_model_smn = model_from_json(model_json_smn)
loaded_model_smn.load_weights("Models\model-bw_smn.h5")

print("Loaded model from disk")

stri = " "
word = " "
current_symbol = "Empty"
photo = "Empty"
ct = {}
ct['blank'] = 0
blank_flag = 0

for i in ascii_uppercase:
    ct[i] = 0

# Define global variables for display
cont = st.empty()
contw = st.empty()
conts = st.empty()


def predict(test_image):
    global blank_flag

    test_image = cv2.resize(test_image, (128, 128))

    result = loaded_model.predict(test_image.reshape(1, 128, 128, 1))
    result_dru = loaded_model_dru.predict(test_image.reshape(1, 128, 128, 1))
    result_tkdi = loaded_model_tkdi.predict(test_image.reshape(1, 128, 128, 1))
    result_smn = loaded_model_smn.predict(test_image.reshape(1, 128, 128, 1))

    prediction = {}
    prediction['blank'] = result[0][0]
    inde = 1

    for i in ascii_uppercase:
        prediction[i] = result[0][inde]
        inde += 1

    # LAYER 1
    prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
    current_symbol = prediction[0][0]

    # LAYER 2
    if current_symbol in ['D', 'R', 'U']:
        prediction = {'D': result_dru[0][0], 'R': result_dru[0][1], 'U': result_dru[0][2]}
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        current_symbol = prediction[0][0]

    if current_symbol in ['D', 'I', 'K', 'T']:
        prediction = {'D': result_tkdi[0][0], 'I': result_tkdi[0][1], 'K': result_tkdi[0][2], 'T': result_tkdi[0][3]}
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        current_symbol = prediction[0][0]

    if current_symbol in ['M', 'N', 'S']:
        prediction1 = {'M': result_smn[0][0], 'N': result_smn[0][1], 'S': result_smn[0][2]}
        prediction1 = sorted(prediction1.items(), key=operator.itemgetter(1), reverse=True)
        current_symbol = prediction1[0][0] if prediction1[0][0] == 'S' else prediction[0][0]

    if current_symbol == 'blank':
        for i in ascii_uppercase:
            ct[i] = 0

    ct[current_symbol] += 1

    if ct[current_symbol] > 60:
        for i in ascii_uppercase:
            if i == current_symbol:
                continue
            tmp = ct[current_symbol] - ct[i]

            if tmp < 0:
                tmp *= -1

            if tmp <= 20:
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

                word = ""
        else:
            if len(stri) > 16:
                stri = " "
            blank_flag = 0
            word += current_symbol


def main():
    opt = option_menu(
        menu_title=None,
        options=["Live Video Input", "File Upload"],
        orientation="horizontal"
    )

    if opt == "Live Video Input":
        run = st.checkbox('Start')
        FRAME_WINDOW = st.image([])
        camera = cv2.VideoCapture(0)

        while run:
            ok, frame = camera.read()
            if ok:
                cv2image = cv2.flip(frame, 1)
                x1 = int(0.5 * frame.shape[1])
                y1 = 10
                x2 = frame.shape[1] - 10
                y2 = int(0.5 * frame.shape[1])

                cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0), 1)
                cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)

                current_image = Image.fromarray(cv2image)
                cv2image = cv2image[y1: y2, x1: x2]

                FRAME_WINDOW.image(cv2image)

                gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 2)
                th3 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                predict(res)

                cont.write(current_symbol)
                contw.write(word)
                conts.write(stri)
                print(current_symbol," ",word," ",stri)
            else:
                st.write('Stopped')


if __name__ == "__main__":
    main()
