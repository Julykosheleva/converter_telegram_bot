FROM python:3.10-slim

COPY ./converter_telegram_bot .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y unar

EXPOSE 8888

CMD ["python", "converter.py"]