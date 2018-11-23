FROM python:3.6

COPY . /handler_endpoint

WORKDIR /handler_endpoint

RUN pip3.6 install --upgrade pip
RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org -r requirements.txt

RUN ["chmod", "+x", "/handler_endpoint/deploy.sh"]

CMD ./deploy.sh
