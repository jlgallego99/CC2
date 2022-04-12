#!/bin/bash
PROM_COMMANDS="--web.enable-lifecycle --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/etc/prometheus/console_libraries --web.console.templates=/etc/prometheus/consoles --storage.tsdb.retention.time=7d"
EXPORTER_COMMANDS="--path.procfs=/host/proc --path.rootfs=/rootfs --path.sysfs=/host/sys"

echo "MODALIDAD CONTENEDORES SIN ORQUESTADOR"

if [ $1 == "stop" ];
then
    echo "PARANDO CONTENEDORES"
    docker stop node-prom
    docker stop node1-exporter
    docker stop node2-exporter
    docker stop node-grafana
    docker stop node-haproxy
    docker rm node-prom
    docker rm node1-exporter
    docker rm node2-exporter
    docker rm node-grafana
    docker rm node-haproxy
elif [ $1 == "run" ]; 
then
    echo "CREANDO VOLUMENES"
    docker volume create prometheus-data
    docker volume create grafana-data

    echo "CREANDO RED DE CONTENEDORES"
    docker network create cc_p1_network

    echo "EJECUTANDO CONTENEDORES"
    docker run -it -d --name node-prom -v $(pwd)/prometheus:/etc/prometheus -v prometheus-data:/prometheus -p 9090:9090 --network cc_p1_network prom/prometheus:latest $PROM_COMMANDS
    docker run -it -d --name node1-exporter -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /:/rootfs:ro --expose 9100 --network cc_p1_network prom/node-exporter $EXPORTER_COMMANDS
    docker run -it -d --name node2-exporter -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /:/rootfs:ro --expose 9100 --network cc_p1_network prom/node-exporter $EXPORTER_COMMANDS
    docker run -it -d --name node-grafana -v $(pwd)/grafana/provisioning/:/etc/grafana/provisioning/ -v grafana-data:/var/lib/grafana -p 3000:3000 --network cc_p1_network grafana/grafana-oss
    docker run -it -d --name node-haproxy -v $(pwd)/haproxy:/haproxy-override -v $(pwd)/haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro -p 8080:80 --network cc_p1_network haproxy:1.6
fi
