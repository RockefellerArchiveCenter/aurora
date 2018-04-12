FROM python:2.7

RUN apt-get update && apt-get -y install apt-utils libsasl2-dev python-dev libldap2-dev libssl-dev

COPY scripts/RAC* /usr/local/bin/

RUN mkdir -p /data/htdocs

COPY . /data/htdocs/aurora

RUN pip install -r /data/htdocs/aurora/requirements.txt

CMD ["python","/data/htdocs/aurora/project_electron/manage.py","runserver","0.0.0.0:8000"]

EXPOSE 8000

#ENTRYPOINT ["/data/htdocs/aurora/project_electron"]
