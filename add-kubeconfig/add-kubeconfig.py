#!/bin/python3

import sys
import os
import yaml

print("Hi! I'm utility that can take one kubeconfig and merge it's content with another kubeconfig!")

if len(sys.argv) == 1:
    print("At least one argument is expected!")
    print("Example usage: add-kubeconfig PATH_TO_KUBECONFIG [PATH_TO_TARGET_KUBECONFIG|$HOME/.kube/config]")    
    exit(1)
if len(sys.argv) > 2:
    print("At no more than 2 arguments are allowed!")
    print("Example usage: add-kubeconfig PATH_TO_KUBECONFIG [PATH_TO_TARGET_KUBECONFIG|$HOME/.kube/config]")    
    exit(1)

kubeconfig=sys.argv[1]
target_kubeconfig="$HOME/.kube/config" if len(sys.argv) == 2 else sys.argv[2]

def popen(command:str) -> str:
    with os.popen(command) as p:
        result = p.read()
        return result

with open(kubeconfig) as stream:
    try:
        kubeconfig_dict = yaml.safe_load(stream)
        if len(kubeconfig_dict["clusters"]) != 1 or len(kubeconfig_dict["contexts"]) != 1 or len(kubeconfig_dict["users"]) != 1:
            print("Sorry, your kubeconfig must contain exactly one clusters,contexts and users entries =(")
            exit(2)
    except yaml.YAMLError as exc:
        print(exc)
        exit(2)

if "127.0.0.1" in kubeconfig_dict["clusters"][0]["cluster"]["server"]:
    yes_no = input(f"Your kubeconfig points to localhost! It is likely that it would not work! Proceed anyway? (y/N): ")
    if yes_no == "n" or yes_no == "N" or yes_no == "":
        print("Operation canceled")
        exit(1)

target_kubeconfig_path = popen(f"ls {target_kubeconfig}").strip()

yes_no = input(f"We will merge data from {kubeconfig} into {target_kubeconfig_path}. Is that ok? (Y/n): ")

if yes_no == "Y" or yes_no == "y" or yes_no == "":
    name = input(f"How would we name the cluster (existing cluster with the same name will be overwritten)?: ")

    with open(target_kubeconfig_path) as stream:
        try:
            target_kubeconfig_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit(3)

        kubeconfig_dict["users"][0]["name"] = name
        kubeconfig_dict["contexts"][0]["context"]["cluster"] = name
        kubeconfig_dict["contexts"][0]["context"]["user"] = name
        kubeconfig_dict["contexts"][0]["name"] = name
        kubeconfig_dict["clusters"][0]["name"] = name

        # Delete duplicate
        target_kubeconfig_dict["users"] = [u for u in target_kubeconfig_dict["users"] if u["name"] != name]
        target_kubeconfig_dict["contexts"] = [u for u in target_kubeconfig_dict["contexts"] if u["context"]["cluster"] != name]
        target_kubeconfig_dict["clusters"] = [u for u in target_kubeconfig_dict["clusters"] if u["name"] != name]
        # Add new
        target_kubeconfig_dict["users"].append(kubeconfig_dict["users"][0])
        target_kubeconfig_dict["contexts"].append(kubeconfig_dict["contexts"][0])
        target_kubeconfig_dict["clusters"].append(kubeconfig_dict["clusters"][0])

        with open(target_kubeconfig_path, 'w', encoding='utf8') as outfile:
            yaml.dump(target_kubeconfig_dict, outfile, default_flow_style=False, allow_unicode=True)  

        print("All done!")
else:
    print("Exiting...")
    exit(1)
