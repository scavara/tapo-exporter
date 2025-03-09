# Tapo P100 Prometheus Exporter

## Startup using docker

Create a [docker-compose.yml](docker-compose.yml)

Create tapo.yaml and list P100 ips/names that exporter will be able to reach them.
You can check it in the Tapo App -> the plug -> gear in top right -> "Device info": IP address OR in your router Wifi router DHCP leases) tip: make a lease static
```yml
devices:
  study: "192.168.1.102"
  living_room: "192.168.1.183"
```
Run the exporter
```console
docker compose up -d
```
Add exporter to Prometheus by adding a job (replace 127.0.0.1 with your exporter machine):

```yml
scrape_configs:
  - job_name: 'tapo'
    static_configs:
    - targets: ['127.0.0.1:9333']
      labels:
        machine: 'home'
```
Import Grafana dashboard (JSON) - Energy monitoring-1664376150978.json for latest update, or just import by pasting [id 17104](https://grafana.com/grafana/dashboards/17104-energy-monitoring/)

### Building from srouce
```console
docker build -t tapo-exporter .
```
Create tapo.yaml as above
Run the exporter
```console
docker compose up -d
```
Add to Prometheus and import Grafana
## Exposed Metrics

```
# TYPE tapo_p100_device_count gauge
tapo_p100_device_count 2.0
```

## Configuration

Communications are done directly with the P100 devices, therefore all IP addresses must be provided.

```
devices:
  study: "192.168.1.102"
  living_room: "192.168.1.183"
```


## Disclaimer
This is meant as an alternative independent way to monitor. However, if you are using home automation Home Assistant has HACS integration that is well maintained and if you finda cheap tastoma hardware it better to use that to avoid breaking changes.
