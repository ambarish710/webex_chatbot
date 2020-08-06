# Downloading and Installing Basics
FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y unzip git make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev tar tree

# Downloading and Installing pyenv
RUN git clone git://github.com/yyuu/pyenv.git /root/.pyenv
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git /root/.pyenv/plugins/pyenv-virtualenv
ENV PATH /root/.pyenv/bin:$PATH
RUN eval "$(pyenv init -)"
RUN eval "$(pyenv virtualenv-init -)"
RUN pyenv install 2.7.10
RUN /root/.pyenv/versions/2.7.10/bin/python -m pip install --upgrade pip
RUN pyenv versions
RUN pyenv virtualenv 2.7.10 maglev2
ENV PATH /root/.pyenv/versions/2.7.10/bin/:$PATH

# Installing pip dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Downloading and installing Java (Kafka dependency requirement)
# Installling OpenJDK-8
RUN apt-get update
RUN apt-get install -y openjdk-8-jdk
RUN apt-get install -y ant
RUN apt-get clean
# Fixing certificate issues
RUN apt-get update
RUN apt-get install ca-certificates-java
RUN apt-get clean
RUN update-ca-certificates -f
# Setting up JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME
RUN java -version

# Downloading chatbot utility and setting up WORKDIR
RUN mkdir -p /root/CiscoWork/chatbot_utility
WORKDIR /root/CiscoWork/chatbot_utility/
RUN pwd
COPY chatbot_utility.tar.gz /root/CiscoWork/chatbot_utility
RUN tar xf chatbot_utility.tar.gz
RUN ls
RUN tree

# Downloading and Installing Kafka
RUN wget -O kafka_2.12-2.3.0.tgz http://ftp.wayne.edu/apache/kafka/2.3.0/kafka_2.12-2.3.0.tgz
RUN tar -xvzf kafka_2.12-2.3.0.tgz
RUN cd kafka_2.12-2.3.0
