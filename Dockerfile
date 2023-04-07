FROM python:3.10-slim

ENV DEBIAN_FRONTEND noninteractive

COPY ./converter_telegram_bot .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y wget

RUN wget http://ftp.us.debian.org/debian/pool/non-free/r/rar/rar_5.5.0-1_amd64.deb
RUN dpkg -i rar_5.5.0-1_amd64.deb
RUN apt-get install -f

EXPOSE 8888

CMD ["python", "converter.py"]