FROM python:3.10-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get -y install sudo \
    apt-utils \
    clamav-daemon \
    clamav-freshclam \
    default-libmysqlclient-dev \
    python-dev \
    python3-pip \
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
    sed -i 's/^DatabaseOwner .*$/DatabaseOwner root/g' /etc/clamav/freshclam.conf && \
    freshclam

# Set up SSH
RUN mkdir /run/sshd && cp -r /etc/ssh /etc/ssh2

# Install Python dependencies
RUN mkdir -p /code/
COPY requirements.txt /code

RUN mkdir -p /data/

# Install Python modules
RUN pip install --upgrade pip && pip install -r /code/requirements.txt

COPY . /code

EXPOSE 8000
EXPOSE 22

WORKDIR /code
