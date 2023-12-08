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