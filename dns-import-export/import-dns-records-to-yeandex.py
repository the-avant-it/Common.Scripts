#!/usr/bin/python3

import requests
import re
import os
import yaml

SECRET_KEY('Input Cloudflare API token: ')

response = requests.get(
    f"https://api.cloudflare.com/client/v4/user/tokens/verify",
    headers={"Authorization": f"Bearer {token}"})

if response.status_code != 200:
    print("ERROR: Token is INVALID!")
    exit(1)

response = requests.get(
    f"https://api.cloudflare.com/client/v4/zones",
    headers={"Authorization": f"Bearer {token}"},
    params={"per_page":100})

if response.status_code != 200:
    print("ERROR: Looks like the token doesn't have access to zones api!")
    exit(1)
else:
    print("Token is valid!")

print(response.text)

for i, zone in enumerate(response.json()["result"]):
    print(f"{i}) {zone['name']} {zone['id']}")

zones = input('Enter space separated numbers of zones you want to export. Enter -1 to export all:')
zones = [int(z) for z in str.split(zones, " ")]
if len(zones) == 0:
    print("You entered nothing we could understand, please, try again!")
    exit(1)

for zone in zones:
    zone_export = {
        "a_records": [],
        "aaaa_records": [],
        "cname_records": [],
        "txt_records": [],
        "mx_records": [],
        "other_records": [],
    }

    print(f"Exporting {zone['name']}...")

    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records",
        headers={"Authorization": f"Bearer {token}"},
        params={"per_page":100})
    data = response.json()
    
    for page in range(1, data['result_info']['total_pages']):
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records",
            headers={"Authorization": f"Bearer {token}"},
            params={"page":page, "per_page":100})
        content = response.json()
        for record in content['result']:
            if record["type"] in ["A", "AAAA", "CNAME", "TXT"]:
                zone_export[f"{str.lower(record['type'])}_records"].append({
                    "type": record["type"],
                    "name": record["name"],
                    "value": record["content"]
                })
            elif record["type"] == "MX":
                zone_export[f"{str.lower(record['type'])}_records"].append({
                    "type": record["type"],
                    "name": record["name"],
                    "value": record["content"]
                })    
            else:
                zone_export["other_records"].append({
                    "type": record["type"],
                    "name": record["name"],
                    "value": record["content"]
                })

    f = open(zone['name'], "w")
    f.write(yaml.dump(zone_export,f))
    f.close()

    print(f"{zone['name']} exported")