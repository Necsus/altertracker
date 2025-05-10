FROM python:3.11-slim

WORKDIR /api
COPY . .
RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

ENV FLASK_APP=run.py

CMD ["flask", "run", "--host=0.0.0.0"]
