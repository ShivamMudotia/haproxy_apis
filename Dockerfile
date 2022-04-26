
FROM python:3.9

WORKDIR /haproxy_apis

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /haproxy_apis/app
COPY .env /haproxy_apis
COPY haproxy.cfg /haproxy_apis

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
