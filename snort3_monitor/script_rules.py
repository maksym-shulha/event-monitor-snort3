import json
import os

import django
from django.http import Http404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Rule


def update_pulled_pork(file: str) -> int:
    """Get data from file in current directory and return count of new added rules"""
    with open(file, encoding="utf8", errors='ignore') as f:
        data = f.readlines()

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
