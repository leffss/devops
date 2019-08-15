FROM python:3.7
ADD . /devops
WORKDIR /devops
RUN cd /devops && pip install -i https://pypi.douban.com/simple -r requirements.txt
RUN cd /devops && echo_supervisord_conf > /etc/supervisord.conf && cat deamon.ini >> /etc/supervisord.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord.conf
EXPOSE 8000
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
