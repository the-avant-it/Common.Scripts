#!/bin/python3
import gitlab

gitlab_url = input("Please enter a gitlab_url: ")
print("You entered:", gitlab_url)

branch_name = input("Please enter a branch_name: ")
print("You entered:", branch_name)

private_token = input("Please enter a private_token: ")
print("You entered:", private_token)

# private_SECRET_KEY("Please CI_INFRASTRUCTURE_PROVIDER: ")
# print("You entered:", private_token)

gl = gitlab.Gitlab(gitlab_url, private_token)
groups = gl.groups.list()

subgroup = gl.groups.get('hostname/main/backend')

projects = subgroup.projects.list(all=True)
for project in projects:
    project = gl.projects.get(project.id)
    try:
        print(f"Starting pipeline for project: {project.name} (ID: {project.id}), branch: {branch_name}")
        pipeline = project.pipelines.create(data={
                'ref': branch_name, 
                'variables': []
            }
        )
        # pipeline = project.pipelines.create(data={
        #         'ref': branch_name, 
        #         'variables': [
        #             { 'key': 'CI_INFRASTRUCTURE_PROVIDER', 'value': 'hostname-aws' }
        #         ]
        #     }
        # )
    except:
        print(f"... error")