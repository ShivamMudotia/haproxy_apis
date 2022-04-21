
## install requirements
pip install -r requirements.txt

## start app
uvicorn app.main:app --reload

## Test if it is up and running

## http://127.0.0.1:8000/docs

## http://127.0.0.1:8000/redoc


## Authentication
### username  -->  shivam
### password  -->  secret


## Routes

## List all backends and servers under them and their status (enabled /disbled)
GET /backend 
## List specific backend and servers under it and their status (enabled/disabled)
GET /backend/<backend> 
## Check specific server under a specific backend whether enabled or disabled 
GET /backend/<backend>/<server> 
## Disable specific server under a specific backend.
POST/PATCH /backend/<backend>/<server>/disable
## Enable specific server under a specific backend.
POST/PATCH /backend/<backend>/<server>/enable

## Reload haproxy - Add OS specific command in the code
POST /reload
## Check haproxy status - Add OS specific command in the code
POST /status


### This is also a frontend available to call these API's which is available at 

https://github.com/ShivamMudotia/haproxyfe.git





