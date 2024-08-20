#!/bin/python3

import requests
import os
import json
from os import listdir
from os.path import isfile, isdir, join

vault_url = input('Input Vault url: ')
vault_SECRET_KEY('Input Vault root token: ')
vault_mount = input('Input Vault mount to restore (e.g. main-ci-apps): ')
vault_mount_type = input('Input Vault mount type (kv2 or kv1): ')

def popen(command:str) -> str:
    with os.popen(command) as p:
        result = p.read()
    return result

def restore(mount:str, path:str, mount_type:str):
    fs_path = f"vault-backup/{mount}/{path}"

    print(f"Checking {fs_path}")
    files = [f for f in listdir(fs_path) if isfile(join(fs_path, f))]
    dirs = [f for f in listdir(fs_path) if isdir(join(fs_path, f))]

    if len(dirs) == 0 and len(files) == 0:
        print(f"Path {fs_path} is empty, skipping")
        return

    # Non leaf
    if len(dirs) != 0:
        print(f"Set keys under path {path}")
        for p in dirs:
            restore(mount, f"{path}{p}" if path.endswith("/") else f"{path}/{p}", mount_type)
    # Leaf
    else:
        print(f"Load variables to {path}")
        for file_name in files:
            fs_path_2 = f"{fs_path}{file_name}" if fs_path.endswith("/") else f"{fs_path}/{file_name}"
            print(f"Uploading data from: {fs_path_2}")
            f = open(fs_path_2, "r")
            data = json.loads(f.read())
            f.close()
            url_path = f"{path}/{file_name}" if path.startswith("/") else f"/{path}/{file_name}"
            response = requests.request(
                method="POST",
                url=f"{vault_url}/v1/{mount}/data{url_path}" if mount_type == "kv2" else f"{vault_url}/v1/{mount}{url_path}",
                headers={"X-Vault-SECRET_KEY},
                json={"data": data["data"]["data"]}
            )
            print(f"Code: {response.status_code}; Content: {response.content};")
            if response.status_code != 200:
                print("ERROR: NON 200 CODE!")
                return
    
restore(vault_mount, "", vault_mount_type)
