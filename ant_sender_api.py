#!/usr/bin/env python3
import socket
import sys
import json
from pyzabbix import ZabbixMetric, ZabbixSender
import time
import datetime

hosts = [#'192.168.2.21',
	 '192.168.99.197',
	 '192.168.99.179',
	 #'192.168.2.26',
	 '192.168.100.50',
	 '192.168.100.48',
 	 '192.168.1.51',
	 ##'192.168.99.196',
	 ##'192.168.99.197',
	 ##'192.168.99.195',
	 ##'192.168.99.184',
	 ]
PORT = 4028
interval = 60

#m = '{\"id\":0,\"jsonrpc\":\"2.0\",\"method\":\"miner_getstat1\"}'
#m = '{\"id\":0,\"jsonrpc\":\"2.0\",\"command\":\"stats\"}'
m = '{\"command\":\"stats\"}'
# jsonObj = json.loads(m)


# data = jsonObj

# Create a socket (SOCK_STREAM means a TCP socket)
while True:
    # time.sleep(interval)
    for i in hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)

            try:
                # Connect to server and send data
                sock.connect((i, PORT))
                sock.sendall(m.encode('ascii'))

                # Receive data from the server and shut down
                received = sock.recv(2048)
                received_1 = sock.recv(2048)
                received_2 = sock.recv(2048)
                received_3 = sock.recv(2048)
                rec_fin = received + received_1 + received_2 + received_3
            except socket.error:
                print(i, 'Connection error')
                continue
            finally:
                sock.close()

            str_1 = format(rec_fin.decode())
            start_index = str_1.find('{"STATS":0')
            end_index = len(str_1) - 10
            str_crop = str_1[start_index:end_index]
            now = datetime.datetime.now()
            print('\n')
            print('IP: ', i)
            print('Time: ', now.isoformat())
            print('\n', "Sent:     {}".format(m))
            #print('\n', "Received: {}".format(rec_fin.decode()))

            parsed_string = json.loads(str_crop)
            print(parsed_string['temp2_6'])
            print(parsed_string['temp2_7'])
            print(parsed_string['temp2_8'])
            print(parsed_string['fan5'])
            print(parsed_string['fan6'])
            print(parsed_string['GHS 5s'])
            print('\n', 'Parsed: ', parsed_string, '\n')

            # Send metrics to zabbix trapper
            packet = [
                ZabbixMetric(i, 'time_up', parsed_string['Elapsed']),
                ZabbixMetric(i, 'ghs_rt', parsed_string['GHS 5s']),
                ZabbixMetric(i, 'ghs_avg', parsed_string['GHS av']),
                #ZabbixMetric(i, 'l_work', l_work),
                #ZabbixMetric(i, 'util', util),
                ZabbixMetric(i, 'ch6_hw', parsed_string['chain_hw6']),
                ZabbixMetric(i, 'ch7_hw', parsed_string['chain_hw7']),
                ZabbixMetric(i, 'ch8_hw', parsed_string['chain_hw8']),
                #ZabbixMetric(i, 'b_chips', b_chips),
                #ZabbixMetric(i, 'ch6_ghs_rt', ch6_ghs_rt),
                #ZabbixMetric(i, 'ch7_ghs_rt', ch7_ghs_rt),
                #ZabbixMetric(i, 'ch8_ghs_rt', ch8_ghs_rt),
                ZabbixMetric(i, 'ch6_t', parsed_string['temp2_6']),
                ZabbixMetric(i, 'ch7_t', parsed_string['temp2_7']),
                ZabbixMetric(i, 'ch8_t', parsed_string['temp2_8']),
                ZabbixMetric(i, 'in_fan', parsed_string['fan5']),
                ZabbixMetric(i, 'out_fan', parsed_string['fan6']),

            ]

            try:
                result = ZabbixSender('192.168.100.15').send(packet)
            except TimeoutError as err:
                # handle this specific error
                print('Timeout in ZabbixSender')
                continue
            except Exception as err:
                # handle all other errors
                print('Other errors in ZabbixSender')
                continue

            print('\n')
            print('Send packet to Zabbix')
            print('Result:', result)
        except Exception as err:
            print('Other error in programm')
            print('Error:', err)
            continue

    print('\n')
    print('Pause: ', interval, 'sec')
    time.sleep(interval)