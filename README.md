
## This is also a frontend available to call these API's which is available at 

## https://github.com/ShivamMudotia/haproxyfe.git

### install requirements
## pip install -r requirements.txt

### start app
## uvicorn app.main:app --reload

### Test if it is up and running

## http://127.0.0.1:8000/docs

## http://127.0.0.1:8000/redoc

## make sure to create a .env file. Here is the sample data and variables currently used.

SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
HAPROXY_BASE_PATH='../haproxy_apis'


## Authentication - Default in-built users - See code comments to manage these.

### username  -->  shivam
### password  -->  Admin321@Admin@123!

### username  -->  admin
### password  -->  Admin321@Admin@123!

## Some points to keep in mind
### replace your haproxy.cfg with sample one in the code. update path in .env if it is supposed to be kep at different path.
### while manually editing the file, always add a "#" as the first charater of the backend server line, else API's will break


## Routes

### List all backends and servers under them and their status (enabled /disbled)
- "GET /backend"
### List specific backend and servers under it and their status (enabled/disabled)
- "GET /backend/#backend "
### Check specific server under a specific backend whether enabled or disabled 
- "GET /backend/#backend/#server "
### Disable specific server under a specific backend.
- "POST/PATCH /backend/#backend/#server/disable"
### Enable specific server under a specific backend.
- "POST/PATCH /backend/#backend/#server/enable"

### Reload haproxy - Add OS specific command in the code (app/haproxy/routers/haproxy.py)
- "POST /reload"
### Check haproxy status - Add OS specific command in the code (app/haproxy/routers/haproxy.py)
- "POST /status"







