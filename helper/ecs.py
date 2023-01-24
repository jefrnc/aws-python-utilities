
import os
import json
import base64
from subprocess import Popen, PIPE
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from pprint import pprint as pp
import sys

def list_clusters(sess):
    client = sess.client("ecs")

    clusters = []
    paginator = client.get_paginator('list_clusters')
    page_iterator = paginator.paginate()
    for page in page_iterator:
        for cluster_arn in page['clusterArns']:
            clusters.append(cluster_arn)
    return clusters

def task_list(sess,clustername):
    client = sess.client("ecs")
    task_list = []
    paginator = client.get_paginator('list_services')
    page_iterator = paginator.paginate(cluster=clustername)
    for page in page_iterator:
        for service_arn in page['serviceArns']:
            task_list.append(service_arn)
    return task_list

def get_image_service(sess,clustername,service):
    client = sess.client("ecs")
    image_list = []
    response = client.describe_services(cluster=clustername,services=[service])
    for i in response['services']:
        for y in i['deployments']:
            task_name = y['taskDefinition']
    tasks = client.describe_task_definition(taskDefinition=task_name)
    for image in tasks['taskDefinition']['containerDefinitions']:
        image_list.append(image['image'])
    return image_list

def get_secrets_service(sess,clustername,service):
    client = sess.client("ecs")
    secrets_list = []
    response = client.describe_services(cluster=clustername,services=[service])
    for i in response['services']:
        for y in i['deployments']:
            task_name = y['taskDefinition']
    tasks = client.describe_task_definition(taskDefinition=task_name)

    for container in tasks['taskDefinition']['containerDefinitions']:
        if "secrets" in container:
            for secret in container["secrets"]:
                secret_item = {}
                secret_item[secret["name"]] = secret["valueFrom"]
                secrets_list.append(secret_item)

    return secrets_list

def get_environments_service(sess,clustername,service):
    client = sess.client("ecs")
    environment_list = []
    response = client.describe_services(cluster=clustername,services=[service])
    for i in response['services']:
        for y in i['deployments']:
            task_name = y['taskDefinition']
    tasks = client.describe_task_definition(taskDefinition=task_name)

    for container in tasks['taskDefinition']['containerDefinitions']:
        for secret in container["environment"]:
            secret_item = {}
            secret_item[secret["name"]] = secret["value"]
            environment_list.append(secret_item)

    return environment_list


def get_tags_service(sess,clustername,service):
    client = sess.client("ecs")
    tag_list = {}
    response = client.describe_services(cluster=clustername,services=[service])
    # Get Amazon Tags
    for i in response['services']:
        serviceArn = i['serviceArn']
        try:
            response = client.list_tags_for_resource(resourceArn=serviceArn)['tags']
            for item in response:
                tag_list[item['key']] = item['value']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The resource was not found.")
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The input was not valid. [{}]".format(serviceArn))
            else:
                print("Unexpected error: %s" % e)

    return tag_list

def split_arn(arn):
    description = {}
    text = arn.split('/')
    description['image'] = text[1].split(':')[0]
    description['tag'] = text[1].split(':')[1]
    return description

def get_taskdefinitions_from_ecs(current_cluster):
    tasks_list = []
    sess = boto3.Session()
    services = task_list(sess,current_cluster)
    for i in services:
        secrets = get_secrets_service(sess, current_cluster, i)
        environments = get_environments_service(sess, current_cluster, i)
        current_task = {}
        current_task['cluster'] = current_cluster
        current_task['name'] = i
        current_task['secrets'] = secrets
        current_task['environments'] = environments
        tasks_list.append(current_task)

    return tasks_list
