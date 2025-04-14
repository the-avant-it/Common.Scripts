#!/usr/bin/python3

import requests
import re
import os
import yaml

print("This code uses nmap and curl to check host name availability and if it does not respond it thinks that it is not used.\nSooo.... it may assume that host is not used if you use bot protection or execute script from blacklisted IP")

token = input('Input Cloudflare API token: ')

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
zones_selection = input('Enter space separated numbers of zones you want to clean up. Enter -1 to clean up all: ')
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

def popen(command:str) -> bool:
    p = os.popen(command)
    p.read()
    status = p.close()
    return status == 0 or status == None

records_to_delete = []

#def check_records():

for zone in zones_selection_enriched:
    print(f"Checking {zone['name']} {zone['id']}...")

    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone['id']}/dns_records",
        headers={"Authorization": f"Bearer {token}"},
        params={"per_page":100})
    data = response.json()

    if response.status_code != 200:
        print(f"ERROR: {data}")
        exit(1)
    else:
        print(f"Checking {data['result_info']['total_count']} records")
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
        
        for record in content['result']:
            name = str.replace(record["name"], "." + record["zone_name"], "")
            if name == record["zone_name"]:
                name = "@"

            if record["type"] in ["A", "AAAA", "CNAME"]:
                print(f"Checking {record['name']} => {record['content']}")

                if record["proxied"]:
                    nmap_upstream_80_opened = popen(f"nmap -T5 -p 80 {record['content']} -Pn | grep -E 'open|closed'")
                    if not nmap_upstream_80_opened:
                        nmap_upstream_443_opened = popen(f"nmap -T5 -p 443 {record['content']} -Pn | grep -E 'open|closed'")
                        if not nmap_upstream_443_opened: 
                            nmap_cloudflare_80_opened = popen(f"nmap -T5 -p 80 {record['name']} -Pn | grep -E 'open|closed'")
                            if not nmap_cloudflare_80_opened:
                                nmap_cloudflare_443_opened = popen(f"nmap -T5 -p 443 {record['name']} -Pn | grep -E 'open|closed'")                        
                    if not (nmap_upstream_80_opened or nmap_upstream_443_opened or nmap_cloudflare_80_opened or nmap_cloudflare_443_opened):
                        print(f"Nor proxied host {record['name']}, nither its upstream {record['content']}, do not respond on 80,443 proe probe => scheduled for deletion")
                        records_to_delete.append(record['name'])
                    else:
                        curl = popen(f"curl https://{record['name']} -v | grep -E 'error code: 525'")
                        if not curl:
                            print(f"{record['name']} is in use!")
                        else:
                            print(f"Proxied host {record['name']} returns error on curl => scheduled for deletion")
                            records_to_delete.append(record['name'])
                else:
                    nmap_upstream_well_known_opened = popen(f"nmap -n -T5 --max-rtt-timeout 1s --min-parallelism 100 -p 80,443,22,5432,6432,6379,9092,9094,8080,3000,8083,8082,9000,9001,3306,5000,9090,9100,9187,9200,8001 {record['content']} -Pn | grep -E 'open|closed'")
                    if not nmap_upstream_well_known_opened:
                        any_opened = popen(f"nmap -n -T5 --max-rtt-timeout 1s --min-parallelism 100 {record['content']} -Pn | grep -E 'open|closed'")
                    if not (nmap_upstream_well_known_opened or any_opened):
                        print(f"Nor dns-only host {record['name']} does not respond on top 1000 well-known ports => scheduled for deletion")
                        records_to_delete.append(record['name'])
                    else:
                        print(f"{record['name']} is in use!")
            else:
                print(f"{record['name']} skipped because of wrong record type!")
        
print(f"Hosts to delete {len(records_to_delete)}: {' '.join(records_to_delete)}")