docker run -d --name redis -p 6379:6379 redis:6.0.8
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 mysql:5.7.31
docker run -d --name guacd -e GUACD_LOG_LEVEL=info -v /home/workspace/devops/media/guacd:/fs -p 4822:4822 guacamole/guacd:1.1.0
