import os
from deta import Deta
from dotenv import load_dotenv

#load env var

load_dotenv(".env")

DETA_KEY="d0c9wa32xpv_VQEwCrdyfc1AYapuiBk5Ss6VTCD2z8Yx"
deta=Deta(DETA_KEY)

cred=deta.Base("Creds")
admin=deta.Base("Admin")


def emailexists(email):
    dev=fetch_all_users()
    emails=[user["email"] for user in dev]
    for user in dev:
        if(user["email"]==email):
            return True
    else:
        return False

def insert_user(email,password,number):
    cred.put({"key":email,"password":password,"number":number,"curkey":""})

def insert_admin(username,password,email,number):
    admin.put({"key":username,"password":password,"email":email,"number":number})

def update_user(email,password,number):
    cred.update({"password":password,"number":number,"curkey":""},email)

def authenticate(username,password):
    var=1
    dev=fetch_all_users()
    emails=[user["key"] for user in dev]
    for user in dev:
        if(username==user["key"] and user["password"]==password):
            return True
            var=0
    if(var):
        return False

def ad_authenticate(username,password):
    var=1
    dev=fetch_all_admins()
    usernames=[user["key"] for user in dev]
    emails=[user["email"] for user in dev]
    for user in dev:
        if(username==user["key"] and user["password"]==password):
            return True
            var=0
    if(var):
        return False

def fetch_all_users():
    res=cred.fetch()
    return res.items

def fetch_all_admins():
    res=admin.fetch()
    return res.items

def forgot_pass(email,otp):
    dev=fetch_all_users()
    usernames=[user["key"] for user in dev]
    emails=[user["email"] for user in dev]
    for user in dev:
        if(user["email"]==email):
            mkey=user["key"]
            change={"curkey":otp}
            cred.update(change,mkey)
