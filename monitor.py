#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import signal
import time
import socket
import threading
import commands

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from engine import db,app
from table import Cp as CP
from table import Cproute as RR
from table import IptableWl

config = {}
config["log_file"] = "/root/BGP/bgp/monitor.log"
config["pid_file"] = "/root/BGP/bgp/monitor.pid"

prefixes = []

IPversion = {
    True: socket.AF_INET,
    False: socket.AF_INET6,
}

# 加载地址库
last_reload = 0
def process_outside():
    global last_reload
    current = time.time()
    if current > last_reload - 5:
        threading.Timer(30, process_timer).start()
        last_reload = current + 30

def process_timer():    
    app.app_context().push()
    db.session.query(IptableWl).delete()
    
    for rr in db.session.query(RR).all():
        wl = IptableWl()
    	wl.ip_start = rr.ip_start
        wl.ip_end = rr.ip_end
        x = rr.prefix.find("/")
        wl.ipnet = rr.prefix[0:x]
        wl.mask = rr.length
        wl.netlink_id = 2
        db.session.merge(wl)

    db.session.commit()
    logging.info("database sync done")
    try:
        s,_ = commands.getstatusoutput('/home/coredns/bin/coredns -conf /home/coredns/conf/Corefile -pidfile=/home/coredns/logs/coredns.pid -reload')
        logging.info("coredns reload status: %d" % s)
    except OSError, e:
        logging.info('core dns reload failed: %s' % e)

def IP2int(ip):
    packed = socket.inet_pton(IPversion['.' in ip], ip)
    value = 0L
    for byte in packed:
        value <<= 8
        value += ord(byte)
    return value

# 邻居状态更新
def process_state(prefix):
    if not (prefix["state"] == "up" or prefix["state"] == "down"):
        return True

    name = prefix["neighbor"]

    index = 0
    exist_cp = db.session.query(CP).filter_by(neighbor = name).first()
    if exist_cp:
        index = exist_cp.id
 
    if prefix["state"] == "up":
        db.session.query(RR).filter_by(neighbor = name).delete()
        process_outside()

        cp = CP()
        cp.id = index
        cp.neighbor = name
        cp.time = "0000-00-00 00:00:00"
        cp.prefixes = 0
        cp.status = 1
        cp.updown = 0
        cp.lastup = prefix["time"]
        db.session.merge(cp)
        db.session.commit()
        return True

    if prefix["state"] == "down":
        db.session.query(RR).filter_by(neighbor = name).delete()
        process_outside()
        
        cp = CP()
        cp.id = index
        cp.neighbor = name
        cp.time = "0000-00-00 00:00:00"
        cp.prefixes = 0
        cp.status = 0
        cp.updown = 0
        cp.lastdown = prefix["time"] 
        db.session.merge(cp)
        db.session.commit()
        return True

    return False

# 邻居路由更新
def process_route(prefix):  
    if prefix["state"] == "announce":
        for i in range(0, len(prefix["route"])):
            if prefix["ip_type"] != 4:
                continue

            rr = RR()
            rr.neighbor = prefix["neighbor"]
            rr.prefix = prefix["route"][i]
            rr.length = prefix["subnet"][i]
            rr.ip_start = prefix["ip_start"][i]
            rr.ip_end = prefix["ip_end"][i]
            rr.aspath = prefix["as-path"]
            rr.nexthop = prefix["next-hop"]
            rr.community = prefix["community"]
            rr.extended_community = prefix["extended-community"]
            rr.origin = prefix["origin"]
            rr.originas = prefix["originas"]
            rr.time = prefix["time"]

            exist_rr = db.session.query(RR).filter_by(prefix=rr.prefix, neighbor=rr.neighbor).first()
            if exist_rr:
                rr.id = exist_rr.id
            db.session.merge(rr)

        db.session.commit()
        process_outside()
        return True

    if prefix["state"] == "withdraw":
        for i in range(0, len(prefix["route"])):
            if prefix["ip_type"] != 4:
                continue

            logging.info(prefix["route"][i])
            db.session.query(RR).filter_by(neighbor=prefix["neighbor"], prefix=prefix["route"][i]).delete()

        db.session.commit()
        process_outside()
        return True

    return False

# 报文解析
def process_message(line, receiver):
    logging.info(line)
    prefix_json = json.loads(line)

    prefix_keys = prefix_json.keys()
    prefix = {}
    prefix_neighbor_keys = {}
    Processing = True

    # 1. Valid header
    if "exabgp" not in prefix_keys:
        Processing = False
    else:
        prefix["time"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # 2. Neighbor state
    if Processing and "neighbor" in prefix_keys:
        prefix_neighbor_keys = prefix_json["neighbor"].keys()
        if "type" in prefix_keys and prefix_json["type"] == "state" and "state" in prefix_neighbor_keys:
            prefix["state"] = prefix_json["neighbor"]["state"]
        else:
            prefix["state"] = prefix_json["type"]
        
        prefix["neighbor"] = prefix_json["neighbor"]["address"]["peer"]
    else:
        return

    # 3. Message Process 
    if Processing and "message" in prefix_neighbor_keys:
        prefix_message_keys = prefix_json["neighbor"]["message"].keys()
    else:
        Processing = False

    # 3.1. Prefix Update
    if Processing and "update" in prefix_message_keys and "address" in prefix_neighbor_keys:
        prefix["neighbor"] = prefix_json["neighbor"]["address"]["peer"]
        prefix_message_update_keys = prefix_json["neighbor"]["message"]["update"].keys()
        if "." in prefix["neighbor"]:
            prefix["ip_type"] = 4
        else:
            prefix["ip_type"] = 6
    else:
        Processing = False

    # 3.2. Prefix Initial 
    if Processing:
        prefix["route"] = {}
        prefix["subnet"] = {}
        prefix["ip_start"] = {}
        prefix["ip_end"] = {}

    # 3.3. Prefix Withdrawal
    if Processing and "withdraw" in prefix_message_update_keys:
        prefix["state"] = "withdraw"
        prefix_message_update_withdraw_keys = prefix_json["neighbor"]["message"]["update"]["withdraw"].keys()
        prefix_inet = prefix_message_update_withdraw_keys[0]
        prefix_message_update_withdraw_routes_keys = prefix_json["neighbor"]["message"]["update"]["withdraw"][prefix_inet]

        i = 0
        for route_map in prefix_message_update_withdraw_routes_keys:
            route = route_map["nlri"]
            prefix["route"][i] = route
            x = route.find("/")
            prefix["subnet"][i] = int(route[x + 1:])
            i += 1
            
        Processing = False

    # 3.4. Prefix Announcement
    elif Processing and "announce" in prefix_message_update_keys:
        prefix["state"] = "announce"
        prefix_message_update_announce_keys = prefix_json["neighbor"]["message"]["update"]["announce"].keys()
        prefix_inet = prefix_message_update_announce_keys[0]
        prefix_message_update_announce_nexthop_keys = prefix_json["neighbor"]["message"]["update"]["announce"][prefix_inet].keys()

        if "null" in prefix_message_update_announce_nexthop_keys:
            prefix["state"] = "unknown"
            Processing = False
        else:
            prefix["next-hop"] = prefix_message_update_announce_nexthop_keys[0]
            prefix_message_update_announce_routes_key = prefix_json["neighbor"]["message"]["update"]["announce"][prefix_inet][prefix["next-hop"]]

            i = 0
            for route_map in prefix_message_update_announce_routes_key:
                route = route_map["nlri"]
                prefix["route"][i] = route
                x = route.find("/")
                prefix["subnet"][i] = int(route[x + 1:])
                prefix["ip_start"][i] = IP2int(route[:x])
                if prefix["ip_type"] == 4:
                    prefix["ip_end"][i] = prefix["ip_start"][i] + (2 ** (32 - prefix["subnet"][i])) - 1
                else:
                    prefix["ip_end"][i] = prefix["ip_start"][i] + (2 ** (128 - prefix["subnet"][i])) - 1
                i += 1

    # 3.5. Prefix Unknown
    else:
        if not (prefix["state"] == "connected" or prefix["state"] == "up" or prefix["state"] == "down" or prefix["state"] == "shutdown"):
            # if not announce and not withdraw then state is unknown
            prefix["state"] = "unknown"
            Processing = False

    # 3.6 Prefix Attribute
    if Processing and "attribute" in prefix_message_update_keys:
        prefix_message_update_attribute_keys = prefix_json["neighbor"]["message"]["update"]["attribute"].keys()
    else:
        Processing = False

    if Processing and "origin" in prefix_message_update_attribute_keys:
        prefix["origin"] = prefix_json["neighbor"]["message"]["update"]["attribute"]["origin"]
    else:
        prefix["origin"] = ""

    if Processing and "atomic-aggregate" in prefix_message_update_attribute_keys:
        prefix["atomic-aggregate"] = prefix_json["neighbor"]["message"]["update"]["attribute"]["atomic-aggregate"]
    else:
        prefix["atomic-aggregate"] = ""

    if Processing and "aggregator" in prefix_message_update_attribute_keys:
        prefix["aggregator"] = prefix_json["neighbor"]["message"]["update"]["attribute"]["aggregator"]
    else:
        prefix["aggregator"] = ""

    if Processing and "community" in prefix_message_update_attribute_keys:
        community_tmp = prefix_json["neighbor"]["message"]["update"]["attribute"]["community"]
        prefix["community"] = ""

        for i in range(0, len(community_tmp)):
            prefix["community"] += str(community_tmp[i][0]) + ":" + str(community_tmp[i][1])
            if i < (len(community_tmp) - 1):
                prefix["community"] += " "
    else:
        prefix["community"] = ""

    if Processing and "extended-community" in prefix_message_update_attribute_keys:
        extended_community_tmp = prefix_json["neighbor"]["message"]["update"]["attribute"]["extended-community"]
        prefix["extended-community"] = ""

        for i in range(0, len(extended_community_tmp)):
            prefix["extended-community"] += str(extended_community_tmp[i])
            if i < (len(extended_community_tmp) - 1):
                prefix["extended-community"] += " "
    else:
        prefix["extended-community"] = " "

    if Processing and "as-path" in prefix_message_update_attribute_keys:
        as_path_tmp = prefix_json["neighbor"]["message"]["update"]["attribute"]["as-path"]
        prefix["as-path"] = ""

        for i in range(0, len(as_path_tmp)):
            prefix["as-path"] += str(as_path_tmp[i])

            if i < (len(as_path_tmp) - 1):
                prefix["as-path"] += " "
            else:
                prefix["originas"] = str(as_path_tmp[i])
    else:
        prefix["as-path"] = ""
        prefix["originas"] = prefix_json["neighbor"]["asn"]["peer"]

    if Processing and "as-set" in prefix_message_update_attribute_keys:
        as_set_tmp = prefix_json["neighbor"]["message"]["update"]["attribute"]["as-set"]
        prefix["as-set"] = ""

        for i in range(0, len(as_set_tmp)):
            prefix["as-set"] += str(as_set_tmp[i])

            if i < (len(as_set_tmp) - 1):
                prefix["as-set"] += " "
    else:
        prefix["as-set"] = ""

    if Processing and "med" in prefix_message_update_attribute_keys:
        prefix["med"] = prefix_json["neighbor"]["message"]["update"]["attribute"]["med"]
    else:
        prefix["med"] = ""

    # 4. Update State
    process_state(prefix)

    # 5. Update Prefix
    process_route(prefix)

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, filename=config["log_file"], format='%(asctime)s %(levelname)s: %(message)s')
    logging.info("Looking glass receiver start")
    print(os.getcwd())

    while True:
        line = sys.stdin.readline().strip()
        if line != "":
            process_message(line, True)
