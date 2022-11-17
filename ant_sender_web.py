#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import pandas as pd
import datetime
import time
import pickle
from pyzabbix import ZabbixMetric, ZabbixSender
import datetime

ip_address = [#'192.168.100.16',
              #'192.168.100.17',
              #'192.168.1.37',
              #'192.168.1.38',
              #'192.168.2.14',
              #'192.168.2.24',
              #'192.168.2.18',
	      #'192.168.99.232',	
	      #'192.168.99.233',
	      #'192.168.99.240',	
              ]
#ip_address = ['192.168.100.3', '192.168.100.4', '192.168.100.5']
ant_param = []
ant_param_all = []
d = time.time()
s = '00000 00000 000x000x  00000 -00--00'
sc = s.count('x')
Bad_Chips = 0
interval = 90


def Value_Extract(df_value):
    if df_value != df_value: return '0'
    else: return df_value

while True:
    try:
        for ip in ip_address:
            now = datetime.datetime.now()
            print('\n')
            print('IP: ', ip)
            print('Time:', now.isoformat(),'\n')
            quote_page = 'http://' + ip + '/cgi-bin/minerStatus.cgi'
            try:
                page = requests.get(quote_page, auth=HTTPDigestAuth('user', 'pass'), timeout = 15)
            except requests.exceptions.RequestException as err:
                print (err)
                print (ip, ' Connection error')
                continue
            

            #print('all ', ant_param_all, '\n')

            dfs = pd.read_html(page.text)

            ch6_hw = 0
            ch6_t = 0
            ch6_ghs_rt = 0

        
            ch7_hw = 0
            ch7_t = 0
            ch7_ghs_rt = 0

            ch8_hw = 0
            ch8_t = 0
            ch8_ghs_rt = 0

            bad_str = ''
            ch_mark = 0
        
            try:
                #ant_param.append(ip)       #Device IP
                time_req = time.time()      #Time of request
                time_up = dfs[0].loc[2,0]   #Up-Time
                ghs_rt = dfs[0].loc[2,1]    #GH/S(RT)
                ghs_avg = dfs[0].loc[2,2]   #GH/S(AVG)
                l_work = dfs[0].loc[2,4]    #LocalWork
                util = dfs[0].loc[2,5]      #Utility

                #for g in [dfs[2].loc[2][0]
                print(len(dfs[2].index))
                print(dfs[2])
                g = 0
                while g < len(dfs[2].index):            #Check for visible chains
                    if dfs[2].loc[g,0] == '6':
                        #print('\n', dfs[2].loc[g,5], '\n')
                        ch6_hw = dfs[2].loc[g,5]
                        ch6_t = dfs[2].loc[g,7]
                        ch6_ghs_rt = dfs[2].loc[g,4]
                        bad_str =  bad_str + dfs[2].loc[g,8]
                        ch_mark = 1
                    elif dfs[2].loc[g,0] == '7':
                        #print('\n', dfs[2].loc[g,4], '\n')
                        ch7_hw = dfs[2].loc[g,5]
                        ch7_t = dfs[2].loc[g,7]
                        ch7_ghs_rt = dfs[2].loc[g,4]
                        bad_str =  bad_str + dfs[2].loc[g,8]
                        ch_mark = 1
                    elif dfs[2].loc[g,0] == '8':
                        #print('\n', dfs[2].loc[g,4], '\n')
                        ch8_hw = dfs[2].loc[g,5]
                        ch8_t = dfs[2].loc[g,7]
                        ch8_ghs_rt = dfs[2].loc[g,4]
                        bad_str =  bad_str + dfs[2].loc[g,8]
                        ch_mark = 1
                    #else:
                    #    print('No chain found, maybe miner rebooting')
                
                    g += 1
                    #print(g)
                if ch_mark == 0:
                    print('\n', 'No chain found, maybe miner rebooting, retry: ')
                    continue
                
                print(bad_str)
                #ch6_hw = Value_Extract(dfs[2].loc[2,5])  #Ch6 HW
                #ch7_hw = Value_Extract(dfs[2].loc[3,5])  #Ch7 HW
                #ch8_hw = Value_Extract(dfs[2].loc[4,5])  #Ch8 HW

                #for i in [Value_Extract(dfs[2].loc[2,8]), Value_Extract(dfs[2].loc[3,8]), Value_Extract(dfs[2].loc[4,8])]:
                Bad_Chips = bad_str.count('x') + bad_str.count('-')
                b_chips = Bad_Chips                     #Bad ASIC's
                print(Bad_Chips)
            
            
                #ch6_ghs_rt = Value_Extract(dfs[2].loc[2,4])  #Ch6 GH/S RT
                #ch7_ghs_rt = Value_Extract(dfs[2].loc[3,4])  #Ch7 GH/S RT
                #ch8_ghs_rt = Value_Extract(dfs[2].loc[4,4])  #Ch8 GH/S RT

                #print(ch8_ghs_rt)
                #print(dfs[2])
            
                #ch6_t = Value_Extract(dfs[2].loc[2,7])  #Ch6 T
                #ch7_t = Value_Extract(dfs[2].loc[3,7])  #Ch7 T
                #ch8_t = Value_Extract(dfs[2].loc[4,7])  #Ch8 T

                #in_fan = dfs[3].loc[1,3]                #FAN In RPM
		in_fan = dfs[3].loc[1,5]                #FAN In RPM
                out_fan = dfs[3].loc[1,6]               #FAN Out RPM
                #out_fan = dfs[3].loc[1,10]               #Error test
            except KeyError as err:
                print(err)
                print('Data read error, retry:')
                continue
                
            
            # Send metrics to zabbix trapper
            packet = [
              ZabbixMetric(ip, 'time_up', time_up),
              ZabbixMetric(ip, 'ghs_rt', ghs_rt),
              ZabbixMetric(ip, 'ghs_avg', ghs_avg),
              ZabbixMetric(ip, 'l_work', l_work),
              ZabbixMetric(ip, 'util', util),
              ZabbixMetric(ip, 'ch6_hw', ch6_hw),
              ZabbixMetric(ip, 'ch7_hw', ch7_hw),
              ZabbixMetric(ip, 'ch8_hw', ch8_hw),
              ZabbixMetric(ip, 'b_chips', b_chips),
              ZabbixMetric(ip, 'ch6_ghs_rt', ch6_ghs_rt),
              ZabbixMetric(ip, 'ch7_ghs_rt', ch7_ghs_rt),
              ZabbixMetric(ip, 'ch8_ghs_rt', ch8_ghs_rt),
              ZabbixMetric(ip, 'ch6_t', ch6_t),
              ZabbixMetric(ip, 'ch7_t', ch7_t),
              ZabbixMetric(ip, 'ch8_t', ch8_t),
              ZabbixMetric(ip, 'in_fan', in_fan),
              ZabbixMetric(ip, 'out_fan', out_fan),
          
            ]

            try:
                result = ZabbixSender('192.168.100.15').send(packet)
            except TimeoutError as err:
                #handle this specific error
                print('Timeout in ZabbixSender')
                continue
            except Exception as err:
                #handle all other errors
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
