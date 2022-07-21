FROM ubuntu:20.04


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
        python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# python install
WORKDIR /tmp
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
RUN bash Miniconda3-latest-Linux-aarch64.sh -b -p /root/conda
ENV PATH "/root/conda/bin:$PATH"
COPY docker/api/environment.yml /tmp/environment.yml
RUN conda env create -f environment.yml && \
    conda init bash && \
    conda clean -a
RUN echo "conda activate birbs" >> ~/.bashrc

# create user
RUN useradd -d /home/user -ms /bin/bash -u $UID -G sudo,video,spiuser,i2c user
RUN echo user:user | chpasswd

RUN echo "export PATH=$PATH" >> /home/user/.bashrc
RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH" >> /home/user/.bashrc
RUN echo "export VISIBLE=now" >> /home/user/.bashrc
RUN echo "export NOTVISIBLE=$NOTVISIBLE" >> /home/user/.bashrc
RUN cat /root/.bashrc >> /home/user/.bashrc

# ssh fix
RUN mkdir /var/run/sshd
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN echo "echo \"PasswordAuthentication no\" >> /etc/ssh/sshd_config" >> /root/ssh_disable_password.sh && \
    echo "service ssh restart" >> /root/ssh_disable_password.sh && \
    chmod +x /root/ssh_disable_password.sh

# copy environment
WORKDIR /home/user/birbs
COPY docker/api/supervisor /etc/supervisor/conf.d/

# expose api ports
EXPOSE 8080
EXPOSE 8888
EXPOSE 22

USER user

CMD ["supervisord", "-n"]