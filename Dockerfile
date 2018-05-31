FROM python:2.7

RUN apt-get update && apt-get -y install sudo apt-utils libsasl2-dev python-dev libldap2-dev libssl-dev python-pip default-libmysqlclient-dev vim ssh

RUN sed -i 's/Port 22/Port 12060/gi' /etc/ssh/sshd_config

COPY scripts/RAC* /usr/local/bin/
COPY scripts/ldap.secret /etc/
COPY scripts/ldap.conf /etc/


RUN sed -i 's/systemctl restart sshd2.service/service ssh restart/gi' /usr/local/bin/RACaddorg

RUN chmod +x /usr/local/bin/RAC*

RUN mkdir -p /data/htdocs/aurora/

COPY requirements.txt /data/htdocs/aurora/

COPY test_bags/ /data/htdocs/aurora/test_bags

COPY aurora/ /data/htdocs/aurora/aurora

RUN pip install -r /data/htdocs/aurora/requirements.txt

COPY scripts/add_orgs_for_container.py /data/htdocs/aurora/

WORKDIR /data/htdocs/aurora/aurora

EXPOSE 8000
