import time
from monitor import process_message

str_s = '{"counter": 4, "pid": "6216", "exabgp": "3.4.8", "host": "localhost", "neighbor": {"ip": "192.168.1.105", "state": "up", "asn": {"peer": "7675", "local": "7676"}, "address": {"peer": "192.168.1.105", "local": "192.168.1.103"}}, "time": 1492497700, "ppid": "6214", "type": "state"}'

str_a = '{"counter": 6, "pid": "6383", "exabgp": "3.4.8", "host": "localhost", "neighbor": {"ip": "192.168.1.105", "message": {"update": {"announce": {"ipv4 unicast": {"null": {"eor": {"afi": "ipv4", "safi": "unicast"}}}}}}, "asn": {"peer": "7675", "local": "7676"}, "address": {"peer": "192.168.1.105", "local": "192.168.1.103"}}, "time": 1492499944, "ppid": "6381", "type": "update"}'



process_message(str_s, '')
process_message(str_s, '')

