FROM python:3.7.9
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY ./sources.list /etc/apt
ADD . /devops
WORKDIR /devops
# RUN apt-get update && apt-get install python3-dev default-libmysqlclient-dev sshpass -y
RUN cd /devops && /usr/local/bin/pip install --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
#RUN cd /devops && /usr/local/bin/pip install --trusted-host pypi.doubanio.com -i https://pypi.doubanio.com/simple -r requirements.txt
RUN cd /devops && echo_supervisord_conf > /etc/supervisord.conf && cat supervisord.conf >> /etc/supervisord.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord.conf
RUN dpkg -i sshpass_1.06-1_amd64.deb
EXPOSE 8000
EXPOSE 8001
EXPOSE 2222
ENV PYTHONOPTIMIZE 1
ENV LANG C.UTF-8
RUN echo 'Asia/Shanghai' > /etc/timezone
ENV TZ='Asia/Shanghai'
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
