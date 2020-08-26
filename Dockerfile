FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get -y install sudo \
    apt-utils \
    clamav-daemon \
    clamav-freshclam \
    default-libmysqlclient-dev \
    python-dev \
    python-pip \
    ssh \
    vim \
    wget \
    rsync \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy and make Aurora scripts
COPY scripts/* /usr/local/bin/
RUN chmod +x /usr/local/bin/*

# Clamav configs and permissions
RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav && \
    sed -i 's/^User .*$/User root/g' /etc/clamav/clamd.conf && \
    sed -i 's/^DatabaseOwner .*$/DatabaseOwner root/g' /etc/clamav/freshclam.conf

# Update clamav databases
RUN wget -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
    wget -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
    wget -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
    chown clamav:clamav /var/lib/clamav/*.cvd


# Make directory needed by SSH
RUN mkdir /run/sshd

# Copy Aurora application files
RUN mkdir -p /code/
COPY . /code

RUN mkdir -p /data/

# Install Python modules
RUN pip install --upgrade pip && pip install -r /code/requirements.txt

EXPOSE 8000
EXPOSE 22

WORKDIR /code/aurora
