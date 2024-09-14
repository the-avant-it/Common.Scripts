#!/usr/bin/python3

import requests
import re
import os
import yaml

print("This code uses nmap and curl to check host name availability and if it responds it thinks that it is open.\nSooo.... it may falselly assume that host is closed if you use bot protection\nSooooo.... you have to disable Super Bot Fight Mode during check")

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
    #print(f"p.read(): {p.read()}")
    wait_status = p.close()
    status = os.waitstatus_to_exitcode(wait_status) if wait_status != None else None
    #print(f"status: {status}")
    return status == 0 or status == None

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
        print("CF SIDE PROBE | ORIGIN SIDE PROBE | RECORD")

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

            if record["type"] in ["A", "AAAA", "CNAME"] and record['name']:
                #print(f"Checking {record['name']} => {record['content']}")

                if record["proxied"]:
                    upstream_opened = False
                    cf_opened = False

                    nmap_upstream_80_opened = popen(f"nmap -T5 -p 80 {record['content']} -Pn 2> /dev/null | grep -E 'open|closed'")
                    if not nmap_upstream_80_opened:
                        nmap_upstream_443_opened = popen(f"nmap -T5 -p 443 {record['content']} -Pn 2> /dev/null | grep -E 'open|closed'")
                    if nmap_upstream_80_opened or nmap_upstream_443_opened:
                        upstream_opened = True
                    # 403 = ip filtration or auth
                    # 530 = Origin DNS error
                    # 525 = SSL handshake failed
                    # 401 = Basic auth
                    closed = popen(f"curl --silent --output /dev/stderr --write-out \"%{{http_code}}\" https://{record['name']} 2> /dev/null | grep -E '403|530|525|401'")
                    if closed:
                        pass
                    else:
                        cf_opened = True

                    print(f"{'OPENED!' if cf_opened else '-------'} {'OPENED!' if upstream_opened else '-------'} {record['name']}")
                else:
                    upstream_opened = False

                    nmap_upstream_well_known_opened = popen(f"nmap -n -T5 --max-rtt-timeout 1s --min-parallelism 100 -p 80,443,22,5432,6432,6379,9092,9094,8080,3000,8083,8082,9000,9001,3306,5000,9090,9100,9187,9200,8001 {record['content']} -Pn 2> /dev/null | grep -E 'open|closed'")
                    if not nmap_upstream_well_known_opened:
                        any_opened = popen(f"nmap -n -T5 --max-rtt-timeout 1s --min-parallelism 100 {record['content']} -Pn 2> /dev/null | grep -E 'open|closed'")
                    if nmap_upstream_well_known_opened or any_opened:
                        upstream_opened = True
                    
                    print(f"------- {'OPENED!' if upstream_opened else '-------'} {record['name']}")
        
#print(f"Hosts to delete {len(records_to_delete)}: {' '.join(records_to_delete)}")