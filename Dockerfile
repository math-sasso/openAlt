FROM ubuntu:20.04 
# FROM mysql-server:latest
WORKDIR /code/
ARG DEBIAN_FRONTEND=noninteractive
ARG MYSQL_ROOT_PASSWORD=root
# install python
RUN apt-get update && apt-get install -y python3.8 python3-distutils python3-pip python3-apt

RUN apt-get -y install systemctl
# install mysql
RUN apt update \
    && apt install -y mysql-server

#RUN systemctl start mysql.service
    # && apt update \
    # && apt install -y mysql-community-server


RUN apt-get install -y libmysqlclient-dev

# requrired to install flask_mysqldb
RUN pip install wheel
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Copy code to image and install requirments
COPY . /code/
RUN pip install -r /code/requirements.txt

# set SQL password as default
# RUN mysql -u root -p < USE mysql;
# RUN mysql -u root -p < UPDATE user SET plugin='mysql_native_password' WHERE User='root'; 
# RUN mysql -u root -p < FLUSH PRIVILEGES;
# RUN mysql -u root -p < exit;

# install SQL databases
# RUN systemctl stop mysql.service \
#     && usermod -d /var/lib/mysql/ mysql \
#     && systemctl start mysql.service
RUN mysql -u root -p << EOF\ 
USE mysql \
UPDATE user SET plugin='mysql_native_password' WHERE User='root' \
FLUSH PRIVILEGES\
EOF
#RUN service mysql start

RUN mysql -u root -p < /code/SQL/CrossrefeventdataWithMain/crossrefeventdataWithMain.sql 
RUN mysql -u root -p < /code/SQL/DOI_Author_Database/dr_bowman_doi_data_tables.sql
RUN python3 /code/pythonScripts/tapAPI.py


EXPOSE 5000

ENTRYPOINT ["FLASK_APP=web.app.py" "flask", "run", "--host=0.0.0.0" ] 