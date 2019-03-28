FROM bitnami/minideb:latest

RUN ln -fs /usr/share/zoneinfo/Asia/Krasnoyarsk /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get -y install python3 python3-pip libldap2-dev libsasl2-dev libssl-dev python3-psycopg2 iputils-ping locales && \
    apt-get clean autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

ENV PYTHONUNBUFFERED 1

ENV LOCALES_DEF ru_RU.UTF-8 en_US.UTF-8

RUN set -- junk $LOCALES_DEF  \
    shift;  \
    for THE_LOCALE in $LOCALES_DEF; do  \
        set --  $(echo $THE_LOCALE  |  awk -F'.' '{ print $1, $2 }');  \
        INPUT_FILE=$1;  \
        CHARMAP_FILE=$2;  \
        localedef  --no-archive -c -i $INPUT_FILE -f $CHARMAP_FILE $THE_LOCALE;  \
    done ; \
    locale-gen

RUN echo "generated locales are:" && locale -a

ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

RUN update-locale

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/

RUN pip3 install -r requirements.txt

ADD . /code/

RUN pip3 install requests
