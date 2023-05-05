Configuration <br>
mqtt_host: 192.168.1.6 <br>
mqtt_port: 1883 <br>
mqtt_user: user<br> 
mqtt_password: pass<br> 
mqtt_topic: rtl_433<br> 
mqtt_retain: true <br> 
protocol: '-R 12 -R 19 -R 30 -R 35'<br> 
discovery_prefix: homeassistant<br> 
discovery_interval: 600<br> 
black_list : "Oregon-CM180"


rtl_433 -f 868M -s 1024k
