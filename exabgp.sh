#!/bin/bash
#
source /root/BGP/bin/activate
cd /root/BGP/bgp
exec exabgp exabgp.conf 
