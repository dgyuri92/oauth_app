#!/bin/bash

# Update your /etc/hosts file for easy access to containers

eval `docker-machine env default`
docker_machine_ip=`docker-machine ip default`

echo "Docker machine: $docker_machine_ip"

if [[ ! -z $docker_machine_ip ]]; then
  hostnames=$(cat docker-compose.yml | grep 'hostname' | cut -d':' -f2)
  line="${docker_machine_ip} ${hostnames}"
  sed "s/^$docker_machine_ip //g" /etc/hosts > /tmp/._new_hosts_file
  echo $line >> /tmp/._new_hosts_file
  sudo mv /tmp/._new_hosts_file /etc/hosts
  exit 0
fi

exit 1
