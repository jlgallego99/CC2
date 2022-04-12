#!/bin/bash
PROM_COMMANDS="--web.enable-lifecycle --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/etc/prometheus/console_libraries --web.console.templates=/etc/prometheus/consoles --storage.tsdb.retention.time=7d"
EXPORTER_COMMANDS="--path.procfs=/host/proc --path.rootfs=/rootfs --path.sysfs=/host/sys"

if [ $1 == "stop" ];
then
    echo "PARANDO CONTENEDORES"
    docker stop node-prom
    docker stop node1-exporter
    docker rm node-prom
    docker rm node1-exporter
elif [ $1 == "run" ]; 
then
    echo "CREANDO VOLUMENES"
    docker volume create prometheus-data

    echo "CREANDO RED DE CONTENEDORES"
    docker network create cc_p1_network

    echo "EJECUTANDO CONTENEDORES"
    docker run -it -d --name node-prom -v $(pwd)/prometheus:/etc/prometheus -v prometheus-data:/prometheus -p 9090:9090 --network cc_p1_network prom/prometheus:latest $PROM_COMMANDS
    docker run -it -d --name node1-exporter -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /:/rootfs:ro -p 9100:9100 --network cc_p1_network prom/node-exporter $EXPORTER_COMMANDS
fi
