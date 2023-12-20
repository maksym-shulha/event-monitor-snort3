# Event Monitor
- Snort3 IPS/IDS
- Django Rest Framework
- Angular
- PostgreSQL

## Quick Start

### Clone the Repository

Clone the repository to your local machine:

```
git clone --recurse-submodules https://github.com/LLkaia/event-monitor-snort3.git
cd event-monitor-snort3
```

### Run the Docker Compose

`docker compose up`

### Open user interface:
`localhost:80`
### Check openapi.yml for RESTAPI documentation
API is available on `localhost:8000`
##
## Managing Daemons
To control daemons within the Snort container, open another bash window:

```docker exec -it snort bash```

Use the following commands to manage processes::
```
supervisorctl status
supervisorctl status process_name
supervisorctl restart process_name
supervisorctl stop process_name
supervisorctl start process_name
```
Notice, that we have 4 processes:
- **server** - DRF and WSGI with RESTAPI functionalities 
- **snort** - Snort3 IDS which looks for traffic on eth0 interface and logs suspicious traffic into _alert_json.txt_
- **watcher** - python script which looks for changes in _alert_json.txt_ and adds them in a database
- **cron** - runs cron with script for auto clearing table with events in database weekly (00:00 of Monday)

## Testing with a .pcap File
1. Download it: [.pcap file](http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/PCAPs/Thursday-WorkingHours.pcap)
2. Uncomment **volumes** in **docker-compose.yml**.
3. Up docker compose.
4. Open bash in snort container, stop **snort** process and run it:
```
snort -c /usr/local/etc/snort/snort.lua -r /root/snort/test.pcap --plugin-path=/usr/local/etc/so_rules/ -k none -l /var/log/snort --tweaks custom
```