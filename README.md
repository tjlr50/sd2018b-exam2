### Examen 2
**Universidad ICESI**  
**Curso:** Sistemas Distribuidos  
**Docente:** Daniel Barragán C.  
**Tema:** Construcción de artefactos para entrega continua  
**Estudiante:** Tomas Lemus

**Correo:** tjlr50@gmail.com

**git:** github.com/tjlr50

**Codigo:** A00054616

### Objetivos
* Realizar de forma autómatica la generación de artefactos para entrega continua
* Emplear librerías de lenguajes de programación para la realización de tareas específicas
* Diagnosticar y ejecutar de forma autónoma las acciones necesarias para corregir fallos en
la infraestructura

### Tecnlogías sugeridas para el desarrollo del examen
* Vagrant
* Docker
* Box del sistema operativo CentOS7
* Repositorio Github
* Python3
* Librerias Python3: Flask, Connexion, Docker
* Ngrok

### Descripción
Para la realización de la actividad tener en cuenta lo siguiente:

* Crear un Fork del repositorio sd2018b-exam2 y adicionar las fuentes de un microservicio
de su elección.
* Alojar en su fork un archivo Dockerfile para la construcción de un artefacto tipo Docker a
partir de las fuentes de su microservicio.

Deberá probar y desplegar los siguientes componentes:

* Despliegue de un **registry** local de Docker para el almacenamiento de imágenes de Docker. Usar la imagen de DockerHub: https://hub.docker.com/_/registry/ . Probar que es posible descarga la imagen generada desde un equipo perteneciente a la red.

* Realizar un método en Python3.6 o superior que reciba como entrada el nombre de un servicio,
la version y el tipo (Docker ó AMI) y en su lógica realice la construcción de una imagen de Docker cuyo nombre deberá ser **service_name:version** y deberá ser publicada en el **registry** local creado en el punto anterior.

* Realizar una integración con GitHub para que al momento de realizar un **merge** a la rama
**develop**, se inicie la construcción de un artefacto tipo Docker a partir del Dockerfile y las fuentes del repositorio. Idee una estrategia para el envío del **service_name** y la **versión** a través del **webhook** de GitHub. La imagen generada deberá ser publicada en el **registry** local creado.

* Si la construcción es exitosa/fallida debera actualizarse un **badge** que contenga la palabra build y la versión del artefacto creado mas recientemente (**opcional**).

* En lugar de una máquina virtual de CentOS7 para alojar el CI server,  emplear la imagen de Docker de Docker hub para el ejecución de la API (webhook listener) y la generación del artefacto: https://hub.Docker.com/_/Docker/ (**opcional**).

![][1]
**Figura 1**. Diagrama de Entrega Continua

### Actividades
1. Documento README.md en formato markdown:  
  * Formato markdown (5%)
  * Nombre y código del estudiante (5%)
  * Ortografía y redacción (5%)
2. Documentación del procedimiento para el montaje del registry (10%). Evidencias del funcionamiento (5%).
3. Documentación e implementación del método para la generación del artefacto. Incluya el código fuente en el informe. Incluya comentarios en el código donde explique cada paso realizado (20%). Evidencias del funcionamiento (5%).
4. Documentación e integración de un repositorio de GitHub junto con la generación del artefacto tipo Docker (20%). Evidencias del funcionamiento (5%).
5. El informe debe publicarse en un repositorio de github el cual debe ser un fork de https://github.com/ICESI-Training/sd2018b-exam2 y para la entrega deberá hacer un Pull Request (PR) al upstream (10%). Tenga en cuenta que el repositorio debe contener todos los archivos necesarios para el aprovisionamiento
7. Documente algunos de los problemas encontrados y las acciones efectuadas para su solución al aprovisionar la infraestructura y aplicaciones (10%)


### Montaje registry 

```
 mkdir -p /docker_data/certs/
```
```
 openssl req -newkey rsa:4096 -nodes -sha256 -keyout `pwd`/docker_data/certs/domain.key -x509 -days 365 -out `pwd`/docker_data/certs/domain.crt
```
En el directorio que se creó, se ingresa a certs donde se genera el certificado como se muestra en la figura siguiente.

![][1]

### Documentación e implementación del método para la generación del artefacto.

Se procede a crear el archivo docker-compose.yml el cual contiene los servicios registry, ci server y ngrok.

![][2]

Docker-compose

```
version: '3'
services:
    registry:
        image: registry:2
        restart: always
        container_name: Registry_Server
        volumes:
            - './docker_data/certs:/certs'
        environment:
            - 'REGISTRY_HTTP_ADDR=0.0.0.0:443'
            - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt
            - REGISTRY_HTTP_TLS_KEY=/certs/domain.key
        ports:
            - '443:443'
    ci_server:
        build: CI_Server
        container_name: CI_Server
        volumes:
          - //var/run/docker.sock:/var/run/docker.sock
        environment:
          - 'CI_SERVER_HTTP_ADDR=0.0.0.0:8080'
        ports:
          - '8080:8080'
    ngrok:
        image: wernight/ngrok
        ports:
          - '0.0.0.0:4040:4040'
        links:
          - ci_server
        environment:
          NGROK_PORT: ci_server:8080
```

Dentro del CI_Server

Se tienen:

Un Dockerfile que es un archivo de texto plano que contiene las instrucciones necesarias para automatizar la creación de una imagen que será utilizada posteriormente para la ejecución de instancias específicas como el contenedor.

```
FROM python:3.6

COPY . /handler_endpoint

WORKDIR /handler_endpoint

RUN pip3.6 install --upgrade pip
RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org -r requirements.txt

RUN ["chmod", "+x", "/handler_endpoint/deploy.sh"]

CMD ./deploy.sh
```

* El deploy.sh es el encargado de levantar la aplicación.
```
export PYTHONPATH=$PYTHONPATH:`pwd`
export FLASK_ENV=development
connexion run gm_analytics/swagger/indexer.yaml --debug -p 8080
```

quien llama al Deploy.sh y acceder mediante el puerto 8080 y generar las dependencias

```
# integration
export PYTHONPATH=$PYTHONPATH:`pwd`
export FLASK_ENV=development
connexion run gm_analytics/swagger/indexer.yaml --debug -p 8080
```

encontradas en Requiriments.txt

```
connexion==1.5.2
Docker
```


Siguiente a esto, se encuentra la carpeta gm-analytics para las acciones que se requieren y para esto se implementa un handlers.py así:

```
import os
import logging
import requests
import json
import docker
from flask import Flask, request, json

def hello():
    result = {'command_return': 'work'}
    return result

def repository_changed():
    result_swagger   = ""
    post_json_data   = request.get_data()
    string_json      = str(post_json_data, 'utf-8')
    json_pullrequest = json.loads(string_json)
    branch_merged = json_pullrequest["pull_request"]["merged"]
    if branch_merged:
        pullrequest_sha  = json_pullrequest["pull_request"]["head"]["sha"]
        json_image_url     = "https://raw.githubusercontent.com/MasterKr123/sd2018b-exam2/" + pullrequest_sha + "/images.json"
        response_image_url = requests.get(json_image_url)
        image_data    =  json.loads(response_image_url.content)
        for service in image_data:
            service_name = service["service_name"]
            image_type = service["type"]
            image_version = service["version"]
            if image_type == 'Docker':
                dockerfile_image_url = "https://raw.githubusercontent.com/MasterKr123/sd2018b-exam2/" + pullrequest_sha + "/" + service_name + "/Dockerfile"
                file_response = requests.get(dockerfile_image_url)
                file = open("Dockerfile","w")
                file.write(str(file_response.content, 'utf-8'))
                file.close()
                image_tag  = "Registry_Server:443/" + service_name + ":" + image_version
                client = docker.DockerClient(base_url='unix://var/run/docker.sock')
                client.images.build(path="./", tag=image_tag)
                client.images.push(image_tag)
                client.images.remove(image=image_tag, force=True)
                result_swagger = image_tag + " - Image built - " + result_swagger
            else:
                out = {'command return' : 'JSON file have an incorrect format'}
        out = {'cammand return' : result_swagger}
    else:
        out= {'command_return': 'Pull request was not merged'}
        return out
```




Para recibir los eventos del Ngrok se crea la carpeta Swagger con el archivo indexer.yaml

```
swagger: '2.0'
info:
  title: User API
  version: "0.1.0"
paths:
  /ciserver/develop/changed:
    post:
      x-swagger-router-controller: gm_analytics
      operationId: handlers.repository_changed
      summary: The repository has changed.
      responses:
        200:
          description: Successful response.
          schema:
            type: object
            properties:
              command_return:
                type: string
                description: The information is procesing
  /:
    post:
      x-swagger-router-controller: gm_analytics
      operationId: handlers.hello
      summary: The repository has changed.
      responses:
        200:
          description: Successful response.
          schema:
            type: object
            properties:
              command_return:
                type: string
                description: The information is procesing
```  


Se procede al build del docker compose

![][3]

Tomamos la URL que nos brinda Ngrok para el webhook de la rama desde 0.0.0.0:4040/status, a continuación se muestra el pull request y la debida respuesta.

![][4]

![][5]

![][6]

![][7]

![][8]


Dentro de los problemas que econtré para el desarrollo, principalmente fue establecer un orden de trabajo que permita un desarrollo conciso de las tareas, para esto se tomó el diagrama del despliegue como base y se incorporó al sistema de archivos del sistema, tomando como ejemplo las actividades realizadas en clase. Personalmente, la busqueda de la información parece ser labor de gran importancia para este tipo de actividades como el aprovisionamiento de máquinas virtuales, ya que implica el abastecimiento de tecnologías que pueden ser nuevas y confusas como chef y el modelo de recetas; nuevamente, los ejemplos previos al exámen permiten generalizar el modelo. Finalmente, el entendimiento de las tecnologías sugeridas como la librerías de python y ngrok añaden complejidad al desarrollo, para esto se esudiaron las fuentes recomendadas. En terminos de trabajo sucedieron interrupciones como reservas de la sala inesperadas que al momento de seguir no recordaba lo que estaba fallando.


[1]: 1.png
[2]: 2.png
[3]: 3.png
[4]: 4.png
[5]: 5.png
[6]: 6.png
[7]: 7.png
[18: 8.png
