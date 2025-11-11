#verificar no dockerhub qual imagem e tag
#FROM python:3.9.0a3-alpine3.10
FROM ubuntu:18.04

# Update packages
#RUN apk update && apk upgrade
RUN apt autoclean -y && apt autoremove -y && apt update -y && apt upgrade -y && apt install python3.6 -y && apt install python3-pip -y

# Install Python Setuptools
RUN apt install -y python-setuptools

# Install pip
#RUN easy_install pip

# Add and install Python modules
RUN mkdir /headfirst
WORKDIR /headfirst
ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Bundle app source
ADD . /headfirst

# instala modulo vsearch
RUN cd mymodules/dist; python3 -m pip install vsearch-1.0.tar.gz

# instala connector mysql
#RUN apk update && apk add mysql-client; cd /headfirst/mysql-connector-python-8.0.17; python3 setup.py install
RUN cd /headfirst/mysql-connector-python-8.0.17; python3 setup.py install

# Expose
EXPOSE  5000

# Run 
#CMD ["python3", "./webapp/vsearch4web.py"]
#CMD ["/bin/sh"]   # para testar
CMD ["/bin/bash"]   # para testar
