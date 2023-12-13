# Event monitor Snort3
## RUN
```docker compose up```
### How to control daemons:
Open another window in bash:

```docker exec -it snort bash```

You can use:
```
supervisorctl status
supervisorctl status process_name
supervisorctl restart process_name
supervisorctl stop process_name
supervisorctl start process_name
```
Notice, that we have 3 processes: **server**, **snort** and **watcher**.

### You can test it with .pcap file:
1. Download it: http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/PCAPs/Thursday-WorkingHours.pcap
2. Uncomment **volumes** in **docker-compose.yml**.
3. Up docker compose.
4. Open bash in snort container, stop **snort** process and run it:
```
snort -c /usr/local/etc/snort/snort.lua -r /root/snort/test.pcap -k none -l /var/log/snort
```
