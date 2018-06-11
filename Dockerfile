FROM python:2.7

RUN apt-get update \
  && echo 'slapd/root_password password password' | debconf-set-selections \
  && echo 'slapd/root_password_again password password' | debconf-set-selections \
  && DEBIAN_FRONTEND=noninteractive apt-get -y install sudo \
    apt-utils \
    clamav-daemon \
    clamav-freshclam \
    default-libmysqlclient-dev \
    ldap-utils \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    python-dev \
    python-pip \
    slapd \
    ssh \
    vim \
    wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy and make Aurora scripts
COPY ldap/ldap.* /etc/
COPY scripts/RAC* /usr/local/bin/
RUN gcc /usr/local/bin/RACcreateuser.c -o /usr/local/bin/RACcreateuser -lldap -llber -lresolv
RUN chmod +x /usr/local/bin/RAC*

RUN sed -i 's/Port 22/Port 12060/gi' /etc/ssh/sshd_config
RUN sed -i 's/systemctl restart sshd2.service/service ssh restart/gi' /usr/local/bin/RACaddorg

# Update clamav databases
RUN wget -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
    wget -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
    wget -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
    chown clamav:clamav /var/lib/clamav/*.cvd

# Permissions for clamav
RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

# Copy Aurora application files
RUN mkdir -p /data/htdocs/aurora/
COPY requirements.txt /data/htdocs/aurora/
COPY test_bags/ /data/htdocs/aurora/test_bags
COPY aurora/ /data/htdocs/aurora/aurora
COPY setup_objects.py /data/htdocs/aurora/

# Install Python modules
RUN pip install -r /data/htdocs/aurora/requirements.txt

EXPOSE 8000 3310

# clamav daemon bootstrapping
ADD clamav_bootstrap.sh /
CMD ["/clamav_bootstrap.sh"]

WORKDIR /data/htdocs/aurora/aurora
