FROM ubuntu:22.04


# install apt packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y --no-install-recommends \
        build-essential \
        software-properties-common \
        pkg-config \
        sudo  \
        curl \
        vim \
        wget \
        libpq-dev \
        supervisor \
        libssl-dev zlib1g-dev libbz2-dev \
        libsm6 libxext6 \
        libgl1-mesa-glx \
        openssh-server \
        python3-pip python3-dev \
        tzdata

ENV TZ="Asia/Tomsk"
# python install
WORKDIR /tmp
COPY docker/api/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r requirements.txt

# create user
# TODO: fix gid for specific groups
ARG UNAME=user
ARG USER_ID=1000
ARG GID=1000
RUN groupadd -g 1001 spiuser
RUN groupadd -g 117 i2c

RUN groupadd -g $GID -o $UNAME

RUN useradd -d /home/$UNAME -ms /bin/bash -u $USER_ID -g $GID -G sudo,video,spiuser,i2c $UNAME
RUN echo $UNAME:$UNAME | chpasswd

RUN echo "export PATH=$PATH" >> /home/$UNAME/.bashrc
RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH" >> /home/$UNAME/.bashrc
RUN echo "export VISIBLE=now" >> /home/$UNAME/.bashrc
RUN echo "export NOTVISIBLE=$NOTVISIBLE" >> /home/$UNAME/.bashrc
RUN cat /root/.bashrc >> /home/$UNAME/.bashrc

# ssh fix
RUN mkdir /var/run/sshd
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN echo "echo \"PasswordAuthentication no\" >> /etc/ssh/sshd_config" >> /root/ssh_disable_password.sh && \
    echo "service ssh restart" >> /root/ssh_disable_password.sh && \
    chmod +x /root/ssh_disable_password.sh

# copy environment
WORKDIR /home/$UNAME/birbs
COPY docker/api/supervisor /etc/supervisor/conf.d/

# expose api ports
EXPOSE 8080
EXPOSE 8888
EXPOSE 22


CMD ["supervisord", "-n"]