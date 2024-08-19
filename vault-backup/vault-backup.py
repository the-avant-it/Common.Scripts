#!/bin/python3

import requests
import os

vault_url = input('Input Vault url: ')
vault_SECRET_KEY('Input Vault root token: ')

def popen(command:str) -> str:
    with os.popen(command) as p:
        result = p.read()
    return result

def backup(mount:str, path:str, mount_type:str):
    response = requests.request(
        method="GET",
        url=f"{vault_url}/v1/{mount}/metadata/{path}?list=true" if mount_type == "kv2" else f"{vault_url}/v1/{mount}/{path}?list=true",
        headers={"X-Vault-SECRET_KEY},
    )
    print(response.content)
    response_dict = response.json()

    fs_path = f"vault-backup/{mount}/{path}"

    # Non leaf
    if 'data' in response_dict:
        print(f"Extract keys from {path}")
        for p in response_dict["data"]["keys"]:
            popen(f"mkdir -p {fs_path}")
            if str.startswith(p, "/") or str.endswith(path, "/"):
                backup(mount, f"{path}{p}", mount_type)
            else:
                backup(mount, f"{path}/{p}", mount_type)
    # Leaf
    else:
        print(f"Get variables from {path}")
        response = requests.request(
            method="GET",
            url=f"{vault_url}/v1/{mount}/data/{path}" if mount_type == "kv2" else f"{vault_url}/v1/{mount}/{path}",
            headers={"X-Vault-SECRET_KEY},
        )
        print(response.content)
        f = open(fs_path, "w")
        f.write(response.text)
        f.close()

# Here add all mounts
backup("main-ci-apps", "", "kv2")
backup("secret", "", "kv1")
