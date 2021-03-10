PWGIS dependencies configuration and installation:
====================

## 1 - Clone pwgis repository from GitHub:

```
cd ~
git clone https://github.com/jasp382/pwgis
```


## 2 - Install Python, Pip and Virtualenv: ##

```
sudo apt update
sudo apt install software-properties-common
sudo apt install python3 python3-pip
sudo -H pip3 install --upgrade pip

sudo -H pip3 install virtualenv virtualenvwrapper

echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" | sudo tee --append ~/.bashrc
echo "export WORKON_HOME=~/.virtualenvs" | sudo tee --append ~/.bashrc
echo "export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv" | sudo tee --append ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" | sudo tee --append ~/.bashrc

source ~/.bashrc
```


## 3 - Setup Docker:

Install Docker

```
sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

sudo apt update

sudo apt install docker-ce
```

Use docker without sudo:

```
sudo usermod -aG docker ${USER}

su - ${USER}

id -nG
```

Install docker compose

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

docker-compose --version
```


## 4 - Install GDAL and GRASS GIS: ##

```
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt update && sudo apt upgrade
sudo apt install grass grass-dev
```

**Set GDALDATA environment variable:**

```
echo "export GDAL_DATA=/usr/share/gdal" | sudo tee --append ~/.bashrc
echo "export PROJ_LIB=/usr/share/proj" | sudo tee --append ~/.bashrc
source ~/.bashrc
```


## 5 - Install PostgreSQL and PostGIS:

```
sudo apt install postgis
```
	
**PostGIS basic configuration:**

```
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'admin';"
sudo -u postgres psql -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -c "CREATE EXTENSION postgis_topology;"
sudo -u postgres createdb postgis_template
sudo -u postgres psql -d postgis_template -c "UPDATE pg_database SET datistemplate=true WHERE datname='postgis_template'"
sudo -u postgres psql -d postgis_template -c "CREATE EXTENSION hstore;"
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/postgis.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/postgis_comments.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/spatial_ref_sys.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/rtpostgis.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/raster_comments.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/topology.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/topology_comments.sql
```

## 6 - Setup Python virtual environment:

```
# Create new virtual env
mkvirtualenv pwgisenv
workon pwgisenv

# Install Python dependencies
cd ~/pwgis && pip install -r requirements.txt
gv=$(ogr2ogr --version)
gvv="${gv:5:-21}"
pip install pygdal==$gvv.6

pv=$(/usr/bin/python3 --version)
pvv="${pv:7:-2}"
echo "/home/$USER/pwgis" | sudo tee ~/.virtualenvs/pwgisenv/lib/python$pvv/site-packages/pycode.pth

# Install pgadmin4
sudo mkdir /var/lib/pgadmin
sudo mkdir /var/log/pgadmin
sudo chown $USER /var/lib/pgadmin
sudo chown $USER /var/log/pgadmin
pip install pgadmin4
```

## 7 - Setup Docker containers:

```
cd ~/pwgis

docker-compose build
docker-compose up -d

sudo ufw allow 22
sudo ufw allow 8686
sudo ufw enable
```

## 8 - Install NodeJS and NPM:

```
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | bash

source ~/.profile

nvm install 14.15.1
```