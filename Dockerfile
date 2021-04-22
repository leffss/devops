FROM python:3.7.9
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY ./sources.list /etc/apt
ADD . /devops
WORKDIR /devops
# RUN apt-get update && apt-get install python3-dev default-libmysqlclient-dev sshpass -y
RUN cd /devops && /usr/local/bin/pip install --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
#RUN cd /devops && /usr/local/bin/pip install --trusted-host pypi.doubanio.com -i https://pypi.doubanio.com/simple -r requirements.txt

RUN cd /devops && echo_supervisord_conf > /etc/supervisord.conf && /bin/cp -a /etc/supervisord.conf /etc/supervisord_all.conf && cat supervisord_all.conf >> /etc/supervisord_all.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_all.conf


RUN cd /devops && /bin/cp -a /etc/supervisord.conf /etc/supervisord_celery_beat.conf && cat supervisord_celery_beat.conf >> /etc/supervisord_celery_beat.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_celery_beat.conf

RUN cd /devops && /bin/cp -a /etc/supervisord.conf /etc/supervisord_celery_worker.conf && cat supervisord_celery_worker.conf >> /etc/supervisord_celery_worker.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_celery_worker.conf

RUN cd /devops && /bin/cp -a /etc/supervisord.conf /etc/supervisord_devops_daphne.conf && cat supervisord_devops_daphne.conf >> /etc/supervisord_devops_daphne.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_devops_daphne.conf

RUN cd /devops && /bin/cp -a /etc/supervisord.conf /etc/supervisord_devops_gunicorn.conf && cat supervisord_devops_gunicorn.conf >> /etc/supervisord_devops_gunicorn.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_devops_gunicorn.conf

RUN cd /devops && /bin/cp -a /etc/supervisord.conf /etc/supervisord_sshd.conf && cat supervisord_sshd.conf >> /etc/supervisord_sshd.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord_sshd.conf

RUN dpkg -i sshpass_1.06-1_amd64.deb
EXPOSE 8000
EXPOSE 8001
EXPOSE 2222
ENV PYTHONOPTIMIZE 1
ENV LANG C.UTF-8
RUN echo 'Asia/Shanghai' > /etc/timezone
ENV TZ='Asia/Shanghai'
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord_all.conf"]
