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

for i, zone in enumerate(response.json()["result"]):
    print(f"{i}) {zone['name']} {zone['id']}")

zones_selection_enriched = []
zones_selection = input('Enter space separated numbers of zones you want to export. Enter -1 to export all: ')
zones_selection = [int(z) for z in str.split(zones_selection, " ")]
if len(zones_selection) == 0:
    print("You entered nothing we could understand, please, try again!")
    exit(1)
elif len(zones_selection) == 1 and zones_selection[0] == -1:
    if zones_selection[0] == -1:
        print("All zones selected")
        for i, zone in enumerate(response.json()["result"]):
            zones_selection_enriched.append({
                "id": zone['id'],
                "name": zone['name']
            })
else:
    zs = response.json()["result"]
    for z in zones_selection:
        if z < 0:
            print("ERROR: Index cant be negative!")
            exit(1)
        else:
            zones_selection_enriched.append({
                "id": zs[z]['id'],
                "name": zs[z]['name']
            })          

for zone in zones_selection_enriched:
    zone_export = {
        "a_records": [],
        "aaaa_records": [],
        "cname_records": [],
        "txt_records": [],
        "mx_records": [],
        "srv_records": [],
        "other_records": [],
    }

    print(f"Exporting {zone['name']} {zone['id']}...")

    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone['id']}/dns_records",
        headers={"Authorization": f"Bearer {token}"},
        params={"per_page":100})
    data = response.json()

    if response.status_code != 200:
        print(f"ERROR: {data}")
        exit(1)
    else:
        print(f"Exporting {data['result_info']['total_count']} records")
        #print(data)

    for page in range(1, data['result_info']['total_pages'] + 1):
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone['id']}/dns_records",
            headers={"Authorization": f"Bearer {token}"},
            params={"page":page, "per_page":100})
        content = response.json()
        
        if response.status_code != 200:
            print(f"ERROR: {content}")     
            exit(1)   
        
        #print(content)

        for record in content['result']:
            name = str.replace(record["name"], "." + record["zone_name"], "")
            if name == record["zone_name"]:
                name = "@"

            if record["type"] in ["A", "AAAA", "CNAME", "TXT"]:
                zone_export[f"{str.lower(record['type'])}_records"].append({
                    "type": record["type"],
                    "name": name,
                    "full_name": record["name"],
                    "value": record["content"],
                    "raw_info": record
                })
            elif record["type"] == "MX":
                zone_export[f"{str.lower(record['type'])}_records"].append({
                    "type": record["type"],
                    "name": name,
                    "full_name": record["name"],
                    "value": record["content"],
                    "priority": record["priority"],
                    "raw_info": record
                })    
            elif record["type"] == "SRV":
                zone_export[f"{str.lower(record['type'])}_records"].append({
                    "type": record["type"],
                    "name": name,
                    "full_name": record["name"],
                    "value": record["content"],
                    "priority": record["priority"],
                    "weight": record["data"]["weight"],
                    "port": record["data"]["port"],
                    "raw_info": record
                })                    
            else:
                zone_export["other_records"].append({
                    "type": record["type"],
                    "name": name,
                    "full_name": record["name"],
                    "value": record["content"],
                    "raw_info": record
                })
        
        print(f"{content['result_info']['count']} records exported!")
        
    file_name = zone['name'] + ".yaml"
    f = open(file_name, "w")
    f.write(yaml.dump(zone_export))
    f.close()

    print(f"{zone['name']} exported to {file_name}")