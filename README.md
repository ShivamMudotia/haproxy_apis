
# install requirements
pip install -r requirements.txt

# start app
uvicorn app.main:app --reload

# Test if it is up and running
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc


# Authentication
# username  -->  shivam
# password  -->  secret


# Routes

GET /backend # List all backends and servers under them and their status (enabled /disbled)
GET /backend/<backend>  # List specific backend and servers under it and their status (enabled/disabled)
GET /backend/<backend>/<server> # specific server under a specific backend whether enabled or disabled

POST/PATCH /backend/<backend>/<server>/disable
POST/PATCH /backend/<backend>/<server>/enable

POST /reload # Reload haproxy
POST /status # Haproxy status


