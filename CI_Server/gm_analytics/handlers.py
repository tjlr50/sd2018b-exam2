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
        json_image_url     = "https://raw.githubusercontent.com/tjlr50/sd2018b-exam2/" + pullrequest_sha + "/images.json"
        response_image_url = requests.get(json_image_url)
        image_data    =  json.loads(response_image_url.content)
        for service in image_data:
            service_name = service["service_name"]
            image_type = service["type"]
            image_version = service["version"]
            if image_type == 'Docker':
                dockerfile_image_url = "https://raw.githubusercontent.com/tjlr50/sd2018b-exam2/" + pullrequest_sha + "/" + service_name + "/Dockerfile"
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

