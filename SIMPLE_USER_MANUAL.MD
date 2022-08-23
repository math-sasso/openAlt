# Criar uma maquina Ubuntu 20.04 que aceite http e https
# Install some basic utilities
sudo apt-get update  && sudo apt-get install -y ca-certificates sudo git bzip2 libx11-6 build-essential vim curl libssl-dev libffi-dev systemctl python3-pip

# clone repo
https://github.com/math-sasso/openAlt.git

# python already installed
sudo apt-get -y purge python3.8
sudo apt-get -y autoremove
sudo apt-get install -y python3-pip python3-dev python3.8-venv


# install mysql
sudo apt update && sudo apt install -y mysql-server
sudo systemctl start mysql.service
sudo apt-get install -y libmysqlclient-dev

# requrired to install flask_mysqldb
pip3 install wheel
sudo apt-get install -y build-essential libssl-dev libffi-dev 
# Enter repo
cd openAlt/

# install requirments
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# some initial commands mysql
RUN mysql -u root -p
USE mysql;
UPDATE user SET plugin='mysql_native_password' WHERE User='root' ;
FLUSH PRIVILEGES;
source ~/openAlt/SQL/CrossrefeventdataWithMain/crossrefeventdataWithMain.sql
source ~/openAlt/SQL/DOI_Author_Database/dr_bowman_doi_data_tables.sql
ctrl+D


# create this required file 
touch passwd.txt

# call tag api
python3 ./pythonScripts/tapAPI.py

FLASK_APP=web.app.py flask run --host=0.0.0.0 --port=80