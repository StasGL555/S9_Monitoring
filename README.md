# S9_Monitoring
Scripts recive info from ASIC Bitmain S9 an send it to Zabbix server for monitoring.
Web version of script uses lib pandas to parse table on web page, then with lib PyZabbix sends info to Zabbix server.
API version uses API interface on device, parse info and then send it to zabbix server.
