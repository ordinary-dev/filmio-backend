FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .env* config.ini* ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "uvicorn", "filmio.main:app", "--reload", "--host", "0.0.0.0" ]