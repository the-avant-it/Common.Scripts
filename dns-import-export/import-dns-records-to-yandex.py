#!/usr/bin/python3

import requests
import re
import os
import yaml

print("Note, you have to install yandex cli!")

file_path = input('Input path to exported records: ')

records = {}
with open(file_path) as stream:
    try:
        records = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

record_types = ["a", "cname", "aaaa", "txt", "mx", "srv"]
for r in record_types:
    if f"{r}_records" not in records:
        print(f"Incorrect format! {r}_records is missing!")
        exit(1)
print("The file appears to be valid!")

zone_id = input('Enter yandex DNS zone id: ')

# https://www.sobyte.net/post/2021-06/pitfalls-of-os.popen-function-and-pipe-in-python/
def popen(command:str) -> None:
    with os.popen(command) as p:
        result = p.read()
    
        print(f"Command: {command} returned: {result}")

for r in records["a_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} A {r["value"]}" --format=json')

for r in records["aaaa_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} AAAA {r["value"]}" --format=json')

for r in records["txt_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} TXT {r["value"]}" --format=json')

for r in records["cname_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} CNAME {r["value"]}" --format=json')    

for r in records["mx_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} MX {r["priority"]} {r["value"]}" --format=json')

for r in records["srv_records"]:
    popen(f'yc dns zone add-records {zone_id} --record="{r["name"]} SRV {r["priority"]} {r["value"]}" --format=json')