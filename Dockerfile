FROM phusion/baseimage:latest
MAINTAINER Robert Olejnik "robert@teonite.com"

RUN apt-get -y update
RUN apt-get -y install --no-install-recommends libldap2-dev libsasl2-dev gettext \
	python-virtualenv python2.7-dev openssh-server postgresql-client-9.3 \
	postgresql-server-dev-9.3 libjpeg8-dev libfreetype6-dev liblcms2-dev \
	python-setuptools git gcc less vim mc python-lxml libcairo2 libpango1.0-0 \
	libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libxml2-dev libxslt1-dev &&\
	apt-get purge -y --auto-remove &&\
	apt-get clean

# == SERVICES ===

# celery
RUN mkdir /etc/service/celery_flower
ADD src/tools/celery_flower.sh /etc/service/celery_flower/run

RUN mkdir /etc/service/celery_beat
ADD src/tools/celery_beat.sh /etc/service/celery_beat/run

RUN mkdir /etc/service/celery_workers
ADD src/tools/celery_workers.sh /etc/service/celery_workers/run

RUN mkdir /etc/service/ochotnicy
ADD src/tools/run_backend.sh /etc/service/ochotnicy/run

# == CODE ===

RUN easy_install pip

RUN mkdir /code/
ADD src/ /code/
COPY src/conf/localsettings.py_prod_template /code/conf/localsettings.py

WORKDIR /code/

RUN pip install -r requirements/prod.txt

# == FINISHup ===

# Running celery in docker is from root
ENV C_FORCE_ROOT="true"

VOLUME ["/code", "/code/logs", "/code/media"]

EXPOSE 22
EXPOSE 8080
EXPOSE 5555

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]
