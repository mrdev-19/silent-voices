import re

#regular expression for email validation
regex_e = r'\b[A-Za-z0-9._%+-]+@srmap\.edu\.in\b'
regex_m=r'(""|91)?[6-9][0-9]{9}'
regex_p='^(?=.*[0-9])'+'(?=.*[1-z])(?=.*[A-Z])'+'(?=.*[@#$%^&+=])'+'(?=\\S+$).{6,20}$'
regex_u='^(?=[a-zA-Z0-9._]{4,20}$)(?!.*[_.]{2})[^_.].*[^_.]$'
def validate_email(email):
    if(re.fullmatch(regex_e,email)):
        return True
    else:
        return False

def validate_mobile(number):
    if((len(number)==13 and number[0:3]=="+91")or(len(number)==12 and number[0:2]=="91")):
        number=number[3:]
    if(re.fullmatch(regex_m,number)):
        return True
    else:
        return False

def validate_username(username):
    if(re.fullmatch(regex_u,username)):
        return True
    else:
        return False

def validate_password(password):
    if(re.fullmatch(regex_p,password)):
        return True
    else:
        return False