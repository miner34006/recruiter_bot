FROM python:3.7
RUN apt-get update -y && apt-get install -y \
    python3 python3-dev python3-pip libssl-dev libffi-dev libpq-dev python-psycopg2 less


EXPOSE 5000

COPY . /usr/local/src/recruiter_bot/
WORKDIR /usr/local/src/recruiter_bot/
RUN pip3 install -r /usr/local/src/recruiter_bot/requirements.txt

COPY ./certificates/www.recruiter-bot.ru.crt /etc/ssl/

RUN touch /var/log/recruiter_bot.log.debug

CMD [ "uwsgi", "--ini", "./deployment/uwsgi.ini" ]
