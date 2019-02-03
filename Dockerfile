FROM python:2.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && echo 'slapd/root_password password password' | debconf-set-selections \
  && echo 'slapd/root_password_again password password' | debconf-set-selections \
  && DEBIAN_FRONTEND=noninteractive apt-get -y install sudo \
    apt-utils \
    clamav-daemon \
    clamav-freshclam \
    default-libmysqlclient-dev \
    python-dev \
    python-pip \
    slapd \
    ssh \
    vim \
    wget \
    rsync \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy and make Aurora scripts
COPY scripts/RAC* /usr/local/bin/
COPY import_sample_data.sh /usr/local/bin/import_sample_data
RUN chmod +x /usr/local/bin/RAC* && chmod +x /usr/local/bin/import_sample_data

# Setup SSH
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
RUN mkdir -p /code/
COPY . /code

RUN mkdir -p /data/

# Install Python modules
RUN pip install --upgrade pip && pip install -r /code/requirements.txt

EXPOSE 8000 3310

# clamav daemon bootstrapping
ADD clamav_bootstrap.sh /
CMD ["/clamav_bootstrap.sh"]

WORKDIR /code/aurora
