FROM ubuntu

RUN apt-get update
RUN apt-get install -y mysql-server netcat-traditional

COPY mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf
COPY test_users.sql ./

RUN service mysql restart && mysql < ./test_users.sql

EXPOSE 3306

CMD service mysql start && nc -lvp 12345
