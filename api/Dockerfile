FROM python:3.11-slim

WORKDIR /api
COPY . .

RUN apt-get update && apt-get install -y netcat-openbsd dos2unix && \
    dos2unix entrypoint.sh && \
    chmod +x entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

ENV FLASK_APP=run.py

CMD ["flask", "run", "--host=0.0.0.0"]
