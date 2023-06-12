FROM ubuntu:latest
CMD python -c "print('Hello world')"
CMD export DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN yes | apt install curl 
RUN yes | apt install gpg
RUN curl www.google.com
RUN curl https://baltocdn.com/helm/signing.asc | gpg --dearmor |  tee /usr/share/keyrings/helm.gpg > /dev/null
RUN  apt-get install apt-transport-https --yes
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" |  tee /etc/apt/sources.list.d/helm-stable-debian.list
RUN apt-get update
RUN apt-get install helm
RUN helm repo add aembit https://helm.aembit.io
ENTRYPOINT /bin/bash
