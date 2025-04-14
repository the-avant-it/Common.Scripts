

from os import environ
import requests;
import tempfile
from datetime import date
from locale import Error
from ansible.module_utils.basic import *
import requests
from requests.auth import HTTPBasicAuth
import multiprocessing as mp
import docker
from urllib.parse import urlparse
import urllib.parse
import threading

def sync_docker_image(image_name, image_tag):
    client = docker.client.DockerClient(timeout=999)

    source_image = f'{source_docker_url}/{image_name}:{image_tag}'
    print(f"Docker pull {source_image}...")
    client.login(registry=source_docker_url, username=source_username, password=source_password)
    client.images.pull(source_image)

    dest_image = f'{dest_docker_url}/{image_name}:{image_tag}'
    print(f"Docker push {dest_image}...")
    image = client.images.get(source_image)
    image.tag(f'{dest_docker_url}/{image_name}', image_tag)
    image.save()
    client.login(registry=dest_docker_url, username=dest_username, password=dest_password)
    client.images.push(repository=f'{dest_docker_url}/{image_name}', tag=f'{image_tag}')

def sync(source_url, source_docker_url, source_username, source_password, source_repository_name, 
    dest_url, dest_docker_url, dest_username, dest_password, dest_repository_name):
    source_params = {
        'repository': source_repository_name
    }

    continuation_token = ""
    while continuation_token != None:

        if continuation_token != "":
            source_params['continuationToken'] = continuation_token
        response = requests.get(f"{source_url}/service/rest/v1/components", params=source_params, auth=HTTPBasicAuth(source_username, source_password))
        if response.status_code not in [200]:
            print("Error while listing components")
            raise ValueError("")
        content = response.json()
        print(f"Found {len(content['items'])} items in {source_repository_name}")
        print(content)
        continuation_token = content["continuationToken"]

        threads = []
        for item in content["items"]:
            print(f"Found {len(item['assets'])} assets in {item['name']}")
            for asset in item["assets"]:

                if item["format"] == "docker":

                    print(f'Starting thread for image {item["name"]}:{item["version"]}...')
                    t = threading.Thread(
                        target=sync_docker_image, 
                        args=(item["name"], item["version"]), 
                        daemon=True
                    )
                    t.start()
                    threads.append(t)

                elif item["format"] == "raw":

                    print(f"Downloading {asset['path']}...")
                    with requests.get(asset["downloadUrl"], auth=HTTPBasicAuth(source_username, source_password), stream=True) as r:
                        with tempfile.TemporaryFile() as f:
                            shutil.copyfileobj(r.raw, f)
                            f.seek(0)

                            url = f"{dest_url}/repository/{dest_repository_name}/{urllib.parse.quote(item['name'])}"
                            print(f"Uploading {item['name']} ({url})...")                          
                            response = requests.put(url,
                                files={"file": f},
                                auth=HTTPBasicAuth(dest_username, dest_password), 
                                stream=True
                            )
                            if response.status_code not in [200, 201]:
                                print(f"Error while uploading to dest {response.status_code} {response.headers} {response.content}")
                                if "Repository does not allow updating assets" in str(response.content):
                                    print(f"The error is not critical")
                                else:
                                    raise ValueError("")
                
                # PyPi
                else:

                    print(f"Downloading {asset['path']}...")
                    with requests.get(asset["downloadUrl"], auth=HTTPBasicAuth(source_username, source_password), stream=True) as r:
                        with tempfile.TemporaryFile() as f:
                            shutil.copyfileobj(r.raw, f)
                            f.seek(0)

                            print(f"Uploading {asset['path']}...")
                            dest_params = {
                                'repository': dest_repository_name
                            }
                            response = requests.post( 
                                f"{dest_url}/service/rest/v1/components", 
                                params=dest_params, 
                                files={"file": f},
                                auth=HTTPBasicAuth(dest_username, dest_password), 
                                stream=True
                            )
                            if response.status_code not in [200, 204]:
                                print(f"Error while uploading to dest {response.status_code} {response.content}")
                                if "Repository does not allow updating assets" in str(response.content):
                                    print(f"The error is not critical")
                                else:
                                    raise ValueError("")
        for t in threads:
            print("Waiting for thread to stop...")
            t.join()

print(f"Arg0: {sys.argv[0]}")
print(f"Arg1 (source_url): {sys.argv[1]}")
print(f"Arg2 (source_docker_url): {sys.argv[2]}")
print(f"Arg3 (source_username): {sys.argv[3]}")
print(f"Arg4 (source_password): {sys.argv[4]}")
print(f"Arg5 (source_repository_name): {sys.argv[5]}")
print(f"Arg6 (dest_url): {sys.argv[6]}")
print(f"Arg7 (dest_docker_url): {sys.argv[7]}")
print(f"Arg8 (dest_username): {sys.argv[8]}")
print(f"Arg9 (dest_password): {sys.argv[9]}")
print(f"Arg10 (dest_repository_name): {sys.argv[10]}")

source_url=sys.argv[1]
source_docker_url=sys.argv[2]
source_username=sys.argv[3]
source_password=sys.argv[4]
source_repository_name=sys.argv[5]
dest_url=sys.argv[6]
dest_docker_url=sys.argv[7]
dest_username=sys.argv[8]
dest_password=sys.argv[9]
dest_repository_name=sys.argv[10]

sync(source_url, source_docker_url, source_username, source_password, source_repository_name, dest_url, dest_docker_url, dest_username, dest_password, dest_repository_name)