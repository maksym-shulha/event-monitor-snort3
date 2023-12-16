import json
import logging
import os

import django
from django.http import Http404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snort3_monitor.settings")
django.setup()
from monitor.models import Rule


logger = logging.getLogger('rules')
formatter = logging.Formatter('%(name)s -> %(levelname)s : %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


def update_pulled_pork(file: str) -> int:
    """Update Snort3 rules

    Update rules from using PulledPork3 and dump them into a file,
    get data from file in current directory and add them to a
    database if these rules are not exist. Reload Snort3 when
    update ends.

    :param file: Name of file with rules
    :return: Count of new rules
    """
    # updating rules
    exit_code = os.system("/usr/local/bin/pulledpork3/pulledpork.py -c /usr/local/etc/pulledpork3/pulledpork.conf")
    if exit_code != 0:
        raise RuntimeError('Update PulledPork was not executed.')
    # dump rules
    exit_code = os.system(
        f"snort -c /usr/local/etc/snort/snort.lua --dump-rule-meta --tweaks custom > {file}")
    if exit_code != 0:
        raise RuntimeError('Dump rules into file was not executed.')

    with open(file, encoding='latin-1') as f:
        data = f.readlines()

    if not data:
        raise RuntimeError('File is empty!')

    # post rules
    count = 0
    for line in data:
        rule = json.loads(line)
        try:
            try:
                # checking if rule exists
                Rule.get_rule(rule['sid'], rule['rev'], rule['gid'])
            except Http404:
                # creating new rule if it is not exists
                Rule(sid=rule['sid'], rev=rule['rev'], gid=rule['gid'],
                     action=rule['action'], message=rule['msg'], data_json=rule).save()
                count += 1
        except KeyError:
            logger.error(f"Rule's data is not full: {rule}")

    os.system("supervisorctl restart snort")

    return count


if __name__ == '__main__':
    try:
        count = update_pulled_pork('rules.txt')
        logger.info(f'Added {count} new rules.')
    except RuntimeError as e:
        logger.error(e)
