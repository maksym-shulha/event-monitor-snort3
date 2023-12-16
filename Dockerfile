FROM kaiall/snort3:latest
WORKDIR /root/snort/

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./snort3_monitor ./snort3_monitor

COPY configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY configs/custom.lua /usr/local/etc/snort/custom.lua

COPY configs/pulledpork.conf /usr/local/etc/pulledpork3/pulledpork.conf

COPY configs/clear_db_weekly /etc/cron.d/clear_db_weekly
RUN crontab /etc/cron.d/clear_db_weekly

ENTRYPOINT export SNORT_HOME_NET=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}') && \
    sed -i "s#^HOME_NET =.*#HOME_NET = '$SNORT_HOME_NET'#" /usr/local/etc/snort/snort.lua && \
    /usr/bin/supervisord