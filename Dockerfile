FROM registry.cn-hangzhou.aliyuncs.com/510908220/develop:ubuntu16.04_nodejs

MAINTAINER WestDoorBlowCola

# Install required packages and remove the apt packages cache when done.
# 监控要用到ssh,所以这里加上了openssh-server
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        libssl-dev \
        libffi-dev \
        nginx \
        git \
        python-pip\ 
        libmysqlclient-dev\
        supervisor \
        sqlite3 \
        python-mysqldb \
        openssh-server \
        p7zip-full \
  && rm -rf /var/lib/apt/lists/*


# setup all the configfiles
# RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY ./nginx-app.conf /etc/nginx/sites-available/default
#COPY supervisor-app.conf /etc/supervisor/conf.d/

COPY .  /docker/heartbeats/

RUN pip install  pipenv
RUN hash -r
# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installinig (all your) dependencies when you made a change a line or two in your app.
ENV LANG C.UTF-8

RUN cd /docker/heartbeats && pipenv install 

RUN export TERM=xterm # 会出现错误TERM environment variable not set

# add (the rest of) our code
WORKDIR /docker/heartbeats/

# install django, normally you would remove this step because your project would already
# be installed in the code/app/ directory
# ENTRYPOINT ["python","/code/upgrade.py"]
# CMD ["--help"]
