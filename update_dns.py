#!/usr/bin/env python

import os
import g_dyndns
from datetime import datetime

CACHE_FILE_NAME = 'ip_cache'
LOG_FILE_NAME = 'action_log'
self_path = None

def init_self_path():
    global self_path
    self_path = os.path.split(os.path.abspath(__file__))[0]

def relpath(*paths):
    return os.path.join(self_path, *paths)

def get_prev_ip():
    if not os.path.exists(relpath(CACHE_FILE_NAME)):
        return None
    f_h = open(relpath(CACHE_FILE_NAME), 'r')
    ret = f_h.read()
    f_h.close()
    return ret

def update_cache(ip):
    f_h = open(relpath(CACHE_FILE_NAME), 'w')
    ret = f_h.write(ip)
    f_h.close()

def update_log(msg=None, ip=''):
    if msg == None:
        return
    data = []
    if os.path.exists(relpath(LOG_FILE_NAME)):
        f_h = open(relpath(LOG_FILE_NAME), 'r')
        data = f_h.readlines()
        f_h.close()
    f_h = open(relpath(LOG_FILE_NAME), 'w')
    if msg == 'IP':
        msg = ip
    message = "%-20s - %s\n" %(msg, datetime.now().isoformat())
    data.append(message)
    f_h.writelines(data[-2000:])
    f_h.close()

def update_ip(key, domain, record, ip):
    zone_id = g_dyndns.get_zoneid_by_domain(key, domain)
    old_version_id = g_dyndns.api.domain.zone.info(key, zone_id)['version']
    version_id = g_dyndns.create_new_zone_version(key, zone_id)
    g_dyndns.update_record(key, zone_id, version_id, record, 'A', ip)
    g_dyndns.api.domain.zone.version.set(key, zone_id, version_id)
    g_dyndns.api.domain.zone.version.delete(key, zone_id, old_version_id)
    update_cache(ip)

def consider_update_ip(should_update_gandi=True, *args):
    current_ip = g_dyndns.get_public_ipv4()
    if current_ip and (current_ip != get_prev_ip()):
        try:
            if should_update_gandi:
                update_ip(*args, ip = current_ip)
            update_log('IP',current_ip)
        except:
            update_log('Update error')
    else:
        update_log('No IP found')

if __name__ == "__main__":
    key = os.environ.get('gandi_key')
    domain = os.environ.get('gandi_domain')
    record = os.environ.get('gandi_record')
    should_update_gandi = bool(int(os.environ.get('gandi_update','0')))
    init_self_path()
    if key and domain and record:
        consider_update_ip(should_update_gandi, key, domain, record)
