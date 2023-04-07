FROM python:3.10-slim

COPY ./converter_telegram_bot .

RUN pip install -r requirements.txt

RUN apt install unrar

EXPOSE 8888

CMD ["python", "converter.py"]