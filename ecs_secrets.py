import os
import json
import base64
import boto3
from subprocess import Popen, PIPE
import json
from pathlib import Path
import helper.ecs as ecs
projects = []

session = boto3.Session()
clusters = ecs.list_clusters(session)

print("{},{},{},{},{}".format("cluster","service","type", "key","value"))
for item in clusters:
    cluster_arn = item
    tasks = ecs.get_taskdefinitions_from_ecs(item)
    for current_task in tasks:
        service_arn = current_task["name"]
        if "secrets" in current_task:
            for secretName  in current_task["secrets"]:
                for key, value in secretName.items():
                    print("{},{},secret,{},\"{}\"".format(cluster_arn,service_arn, key,value))
        if "environments" in current_task:
            for secretName  in current_task["environments"]:
                for key, value in secretName.items():
                    print("{},{},environment,{},\"{}\"".format(cluster_arn,service_arn, key,value))
 

