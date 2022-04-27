#gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0 &
uvicorn app.main:app --reload --host 0.0.0.0 &