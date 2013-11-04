#!/usr/bin/env python

import os
import g_dyndns


CACHE_FILE_NAME = 'ip_cache'
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

def update_ip(key, domain, record, ip):
    zone_id = g_dyndns.get_zoneid_by_domain(key, domain)
    version_id = g_dyndns.create_new_zone_version(key, zone_id)
    g_dyndns.update_record(key, zone_id, version_id, record, 'A', ip)
    g_dyndns.api.domain.zone.version.set(key, zone_id, version_id)
    update_cache(ip)

def consider_update_ip(*args):
    current_ip = g_dyndns.get_public_ipv4()
    if current_ip != get_prev_ip():
        update_ip(*args, ip = current_ip)

if __name__ == "__main__":
    key = os.environ.get('gandi_key')
    domain = os.environ.get('gandi_domain')
    record = os.environ.get('gandi_record')
    init_self_path()
    if key and domain and record:
        consider_update_ip(key, domain, record)
