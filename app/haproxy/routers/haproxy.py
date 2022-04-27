from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi import APIRouter
import os
import re

import subprocess

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


from dotenv import load_dotenv

load_dotenv()


# to get a string like this run:
# openssl rand -hex 32
#SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# This is usually /etc/haproxy on Linux machines. Update .env file accordingly 
HAPROXY_BASE_PATH=os.getenv('HAPROXY_BASE_PATH')

# Add a user or update password of existing user
# open a python command prompt
# import bcrypt
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# pwd_context.hash('secret')  # Here 'secret' is the new password that you want to set.
# update the new hash in belwo DB to update user's password.
# same process can be followed while adding new user.


fake_users_db = {
    "shivam": {
        "username": "shivam",
        "full_name": "Shivam Mudotia",
        "email": "shivam.mudotia@somecompany.com",
        #"hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "hashed_password": '$2b$12$Y/zVOnVS.XpxPMYrtPkkFONwM7rtRdqZZWpdmZVewaNLkeMjr3vc2',
        # hashed password is --> Admin321@Admin@123!
        "disabled": False,
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin The Administrator",
        "email": "admin@somecompany.com",
        "hashed_password": "$2b$12$7CNU3D7b2Hf3OfRkNcs4duRMnCL3kymH0YQ1XXc5mZlbWqJMRBbzW",
        # hashed password is --> Admin321@Admin@123!
        "disabled": False,
    }

}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    #prefix="/haproxy"

)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token , tags=['HAProxy - Authentication'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User , tags=['HAProxy - Authentication'])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# HAProxy API's

@router.get("/", tags=['HAProxy - Fetch configuration'])
async def just_a_welcome_message(current_user: User = Depends(get_current_active_user)):
    return {"Hello": "Welcome to HAProxy LB Manager"}
    #return {"token": token}

@router.get("/backends", tags=['HAProxy - Fetch configuration'])
async def list_all_backends(current_user: User = Depends(get_current_active_user)):
    # backends = []
    # backendregex = re.compile(r'^backend')
    # os.chdir(HAPROXY_BASE_PATH)
    # haproxyfile = open('./haproxy.cfg', 'r')

    # for line in haproxyfile.readlines():
    #     if backendregex.search(line):
    #         backend = line.split(" ")[1].rstrip("\n")
    #         backends.append(backend)

    # haproxyfile.close()

    # Above code is commented as there is no need to discover and show other backends apart from matrix.
    # Below line is added to hardcode to send only matrix backend. 
    
    backends=["https_prodmatrix"]

    return{"All_Backends": backends}


@router.get("/backends/{backend}", tags=['HAProxy - Fetch configuration'])
async def fetch_backend_servers_and_status(backend: str, current_user: User = Depends(get_current_active_user)):

    backends = []
    backendregex = re.compile(r'^backend')
    os.chdir(HAPROXY_BASE_PATH)
    haproxyfile = open('./haproxy.cfg', 'r')

    for line in haproxyfile.readlines():
        if backendregex.search(line):
            backend_found = line.split(" ")[1].rstrip("\n")
            backends.append(backend_found)

    haproxyfile.close()

    if backend not in backends:
        return {"Invalid Backend supplied": f"Backend should be one of these --> {backends} "}

    backend_lines = []
    serversregex = re.compile(r'^[#|\s]*server')
    backendregex = re.compile(r'^backend')
    blanklineregex = re.compile(r'^$')
    os.chdir(HAPROXY_BASE_PATH)
    haproxyfile = open('./haproxy.cfg', 'r')

    for line in haproxyfile.readlines():
        if backendregex.search(line):
            backend_found = line.split(" ")[1].rstrip("\n")
            if backend_found == backend:
                backend_lines.append(line.rstrip("\n"))
            pass
        elif len(backend_lines):
            if blanklineregex.search(line):
                break
            elif serversregex.search(line):
                backend_lines.append(line.rstrip("\n"))
    backend_servers = backend_lines[1:]

    backend_servers_state = {}
    commentedlineregex = re.compile(r'^#')
    for server in backend_servers:
        if commentedlineregex.search(server):
            state = "Disabled"
        else:
            state = "Enabled"

        backend_servers_state[re.split(' +', server)[2]] = state

    haproxyfile.close()

    return {backend: backend_servers_state}


@router.patch("/backends/{backend}/{server}/{desired_state}", tags=['HAProxy - Enable / Disable a Backend Server'])
async def update_backend(backend: str, server: str, desired_state: str, current_user: User = Depends(get_current_active_user)):

    backends = []
    backendregex = re.compile(r'^backend')
    os.chdir(HAPROXY_BASE_PATH)
    haproxyfile = open('./haproxy.cfg', 'r')

    for line in haproxyfile.readlines():
        if backendregex.search(line):
            backend_found = line.split(" ")[1].rstrip("\n")
            backends.append(backend_found)

    haproxyfile.close()

    if backend not in backends:
        return {"Invalid Backend supplied": f"Backend should be one of these --> {backends} "}

    backend_lines = []
    serversregex = re.compile(r'^[#|\s]*server')
    backendregex = re.compile(r'^backend')
    blanklineregex = re.compile(r'^$')
    os.chdir(HAPROXY_BASE_PATH)
    haproxyfile = open('./haproxy.cfg', 'r')

    for line in haproxyfile.readlines():
        if backendregex.search(line):
            backend_found = line.split(" ")[1].rstrip("\n")
            if backend_found == backend:
                backend_lines.append(line.rstrip("\n"))
            pass
        elif len(backend_lines):
            if blanklineregex.search(line):
                break
            elif serversregex.search(line):
                backend_lines.append(line.rstrip("\n"))
    backend_servers = backend_lines[1:]

    backend_servers_state = {}
    commentedlineregex = re.compile(r'^#')
    for line in backend_servers:
        if commentedlineregex.search(line):
            state = "Disabled"
        else:
            state = "Enabled"

        backend_servers_state[re.split(' +', line)[2]] = state

    haproxyfile.close()

    all_backends = list(dict.keys(backend_servers_state))
    if server not in all_backends:
        return {"Invalid Backend Server": f"Server should be one of these for backend {backend} --> {all_backends}"}

    if desired_state not in ["Enabled", "Disabled"]:
        return {"Invalid Desired State": "State can either be Enabled or Disabled"}

    if desired_state == "Disabled":
        if backend_servers_state[server] == "Disabled":
            return {backend: backend_servers_state}
        for key in backend_servers_state:
            if backend_servers_state[key] == "Disabled":
                return{"backend": "Only one one backend server can be disabled at a time"}
        total_enabled=0
        for key in backend_servers_state:
            if backend_servers_state[key] == "Enabled":
                total_enabled+=1
            print(total_enabled)
        if total_enabled < 2:
            return{"backend": "Minimum on backend server should be Enabled"}
        os.chdir(HAPROXY_BASE_PATH)
        os.rename('./haproxy.cfg', './haproxy.cfg_backup')
        with open('./haproxy.cfg_backup') as infile:
            with open('./haproxy.cfg', 'w') as outfile:
                for line in infile:
                    if serversregex.search(line):
                        server_found = re.split(' +', line)[2]
                        if server_found == server:
                            outfile.write('#' + line)
                        else:
                            outfile.write(line)
                    else:
                        outfile.write(line)

        backend_servers_state[server] = desired_state
        return {backend: backend_servers_state}
    else:
        if backend_servers_state[server] == "Enabled":
            return {backend: backend_servers_state}
        os.chdir(HAPROXY_BASE_PATH)
        os.rename('./haproxy.cfg', './haproxy.cfg_backup')
        with open('./haproxy.cfg_backup') as infile:
            with open('./haproxy.cfg', 'w') as outfile:
                for line in infile:
                    if serversregex.search(line):
                        if commentedlineregex.search(line):
                            new_line = re.split('#', line)[1]
                            server_found = re.split(' +', line)[2]
                            if server_found == server:
                                outfile.write(new_line)
                            else:
                                outfile.write(line)
                        else:
                            outfile.write(line)
                    else:
                        outfile.write(line)

        backend_servers_state[server] = desired_state
        return {backend: backend_servers_state}


@router.post("/reload", tags=['HAProxy - Reload / Check Status'])
async def reload_haproxy(current_user: User = Depends(get_current_active_user)):
    # Add OS specific code to reload haproxy and accoering send a respoce
    status = subprocess.call(["sudo", "systemctl", "reload",  "haproxy"])
    if status == 0:
        return {"Success" : True } # Do not return any other value on Success
    else:
        return {"Success" : False } # Do not return any other value on Failure


@router.get("/status", tags=['HAProxy - Reload / Check Status'])
async def status_haproxy(current_user: User = Depends(get_current_active_user)):
    # Add OS specific code to get haproxy status 
   status = subprocess.call(["systemctl", "is-active",  "haproxy"])
   if status == 0: # 0 means "active": 
       return {"Success" : True } # Do not return any other value on Success
   else:
       return {"Success" : False } # Do not return any other value on Failure
