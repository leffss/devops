docker rm mysql5.7
docker run --name mysql5.7 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 -d mysql:5.7 --lower_case_table_names=1
