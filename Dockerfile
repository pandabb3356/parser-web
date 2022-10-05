# Use an official Python runtime as a parent image
FROM python:3.7-slim-stretch

# Define environment variables for installation
ENV TERM linux
ENV INSTALL_DIR /parser-web

# Set the working directory to $INSTALL_DIR
RUN echo $INSTALL_DIR
RUN mkdir -p $INSTALL_DIR

WORKDIR $INSTALL_DIR

# Copy the current directory contents into the container at /app
COPY . .

# Define environment variable
ENV NAME=world
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

RUN set -ex ;\
    apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libblas-dev \
        liblapack-dev \
        libpq-dev \
        libsqlite3-dev \
        python3-dev \
        python-dev \
        python3-pip \
        python3-requests \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
        unzip \
        libaio1 \
        libaio-dev \
        vim \
        supervisor; \
    sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen ;\
    locale-gen ;\
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ;\
    pip install -U pip setuptools wheel;\
    apt-get clean ;\
    rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r prod-requirements.txt

RUN cp -rf scripts/start.conf /etc/supervisor/conf.d/start.conf
#    cp -rf scripts/entrypoint.sh /tmp/entrypoint.sh; \
#    chmod +x /tmp/entrypoint.sh

EXPOSE 5300
