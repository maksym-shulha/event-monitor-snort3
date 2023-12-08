import json
import os

import django
from django.http import Http404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Rule


def update_pulled_pork(file: str) -> int:
    """
    Update rules from pulledpork3 and dump them into a file and
    get data from file in current directory and return count of new added rules
    """
    # updating rules
    exit_code = os.system("/usr/local/bin/pulledpork3/pulledpork.py -c /usr/local/etc/pulledpork3/pulledpork.conf")
    if exit_code != 0:
        raise RuntimeError('Update was not executed')
    # dump rules
    exit_code = os.system(
        f"snort -c /usr/local/etc/snort/snort.lua --dump-rule-meta --plugin-path /usr/local/etc/so_rules/ > {file}")
    if exit_code != 0:
        raise RuntimeError('Dump was not executed')

    with open(file, encoding="utf8", errors='ignore') as f:
        data = f.readlines()

    # post rules
    count = 0
    for line in data:
        rule = json.loads(line)
        try:
            Rule.get_by_sid_and_rev(rule['sid'], rule['rev'])
        except Http404:
            Rule(sid=rule['sid'], rev=rule['rev'], action=rule['action'], message=rule['msg'], data_json=rule).save()
            count += 1
    print(f'Added {count} new rules.')

    return count


if __name__ == '__main__':
    update_pulled_pork('rules.txt')
