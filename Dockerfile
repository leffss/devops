FROM python:3.7
ADD . /devops
WORKDIR /devops
RUN cd /devops && pip install -i https://pypi.douban.com/simple -r requirements.txt
RUN cd /devops && echo_supervisord_conf > /etc/supervisord.conf && cat deamon.ini >> /etc/supervisord.conf && \
	sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord.conf
# RUN apt-get update && apt-get install sshpass -y
RUN dpkg -i sshpass_1.06-1_amd64.deb
EXPOSE 8000
EXPOSE 8001
EXPOSE 2222
ENV PYTHONOPTIMIZE 1
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
