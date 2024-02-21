FROM python:3.8

ENV HOME /

WORKDIR /

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD python3 -u server.py