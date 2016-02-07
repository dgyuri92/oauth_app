#!/bin/bash

# Update your /etc/hosts file for easy access to containers

machine="$1"

if [[ -z $machine ]]; then
  machine="default"
fi

docker_machine_ip="127.0.0.1"

docker_machine_command=$(which docker-machine)
if [[ $? -eq 0 ]]; then
  echo "Using docker-machine..."
  eval `$docker_machine_command env $machine`
  docker_machine_ip=`docker-machine ip $machine`
fi

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
