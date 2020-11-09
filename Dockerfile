FROM python:3.8-slim
WORKDIR /app
COPY *.py /app/
RUN adduser --disabled-login -q covidapp && pip install slack_bolt requests && mkdir /app/config
USER covidapp
EXPOSE 3000
CMD [ "python", "SlackBoltBot.py" ]