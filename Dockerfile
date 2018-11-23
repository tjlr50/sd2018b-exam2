FROM centos:7

RUN yum install httpd
EXPOSE 80

CMD sudo systemctl start httpd
CMD systemctl enable httpd


