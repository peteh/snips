#!/bin/bash

#I 2019-06-24 20:13:13,507 yowsup.common.http.warequest - b'{"status":"ok","login":"36309040975","type":"new","edge_routing_info":"CAUIAg==","chat_dns_domain":"fb","security_code_set":false}\n'
#{
#    "__version__": 1,
#    "cc": "36",
#    "client_static_keypair": "OMD3Po+z61vPB6Xx2SnNVvZLNDHBU1wMclMWs0pDcntySrdgY0rONGfVhPSD52jssL2wjiaPm61PGK5j+duGEQ==",
#    "expid": "FXXI8jmSRxuMbCFrueWBbA==",
#    "fdid": "29e26262-5df8-4b2b-87c0-1368a20522d4",
#    "id": "R+AoT+0Cmx7CyTGtx1SPZtfVYNY=",
#    "mcc": "216",
#    "mnc": "29",
#    "phone": "36309040975",
#    "sim_mcc": "000",
#    "sim_mnc": "000"
#}
#status: b'ok'
#login: b'36309040975'
#type: b'new'
#edge_routing_info: b'CAUIAg=='


yowsup-cli registration --requestcode sms --config-phone 36309040975 --config-cc 36 --config-mcc 216 --config-mnc 29
