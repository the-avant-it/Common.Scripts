Supports pypi-hosted, docker, raw-hosted repo types

# Notes

## All arguments

`sudo python3 sync.py source_url source_docker_url source_username source_password source_repository_name dest_url dest_docker_url dest_username dest_password dest_repository_name`

## Docker example

`sudo python3 sync.py https://old-nexus.example.com old-docker-repository.example.com:8082 OLD_NEXUS_USER OLD_NEXUS_PASSWORD OLD_NEXUS_DOCKER_REPO_NAME https://new-nexus.example.com docker-repository.example.com NEW_NEXUS_USER NEW_NEXUS_PASSWORD NEW_NEXUS_DOCKER_REPO_NAME`

## PyPi example

`sudo python3 sync.py https://old-nexus.example.com 123 OLD_NEXUS_USER OLD_NEXUS_PASSWORD OLD_NEXUS_PYPI_REPO_NAME https://new-nexus.example.com 123 NEW_NEXUS_USER NEW_NEXUS_PASSWORD NEW_NEXUS_PYPI_REPO_NAME`

`123` - is just placeholder value for source_docker_url and dest_docker_url which are not used in this case

## Raw example

`sudo python3 sync.py https://old-nexus.example.com 123 OLD_NEXUS_USER OLD_NEXUS_PASSWORD OLD_NEXUS_RAW_REPO_NAME http://new-nexus.example.com:8081 123 NEW_NEXUS_USER NEW_NEXUS_PASSWORD NEW_NEXUS_RAW_REPO_NAME`

# Possible problems

## Error while uploading to dest 413 Request Entity Too Large

Use direct url to docker repository bypassing whatewer proxy you have in front of nexus. 
For that you would need to add something like `nexus.example.com:8082` to `insecure-registries` in your `/etc/docker/daemon.json`