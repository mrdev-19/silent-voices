import smtplib
import ssl
import random as ran
import os
def forgot_password(email_to):
    smtp_port=587
    smtp_server="smtp.gmail.com"

    email_from="mrdevinfinity@gmail.com"
    passw=os.getenv("pass")

    def otpgen():
        otp=""
        for i in range(6):
            otp+=str(ran.randint(1,9))
        return "Your 6 Digit OTP for Sign Language to Text "+otp
    message=otpgen()+"\nYou can enter your OTP and new password at : https://password-reset.streamlit.app"
    #fill the details here after creating new app
    email_context = ssl.create_default_context()

    try:
        TIE_server = smtplib.SMTP(smtp_server,smtp_port)
        TIE_server.starttls(context=email_context)
        TIE_server.login(email_from,passw)
        TIE_server.sendmail(email_from,email_to,message)
        TIE_server.quit()
        return message[46:52]
    except Exception as d:
        print(d)
        return -1