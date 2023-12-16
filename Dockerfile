FROM httpd:2.4

COPY static/ /webapp/static
COPY templates/ /webapp/templates
COPY webref.py /webapp
COPY config/webref.wsgi /webapp
COPY config/httpd.conf /usr/local/apache2/conf
COPY requirements.txt /webapp
RUN mkdir /var/run/apache2      # needed to store files for WSGI
RUN mkdir /var/www              # home of www-data user
WORKDIR /webapp

RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y libapache2-mod-wsgi-py3
RUN pip3 install -r requirements.txt --break-system-packages

CMD ["/usr/local/apache2/bin/httpd", "-D", "FOREGROUND"]
