# HomeAssistant
konfiguracja własna do HA

http://www.sensorsiot.org/install-rtl_433-for-a-sdr-rtl-dongle-on-a-raspberry-pi/


#instalacja klient mqtt - w hass.io add-on mosquitto

apt-get install mosquitto-clients

#utorzenie serwisu

sudo nano /etc/systemd/system/rtl_433.service


sudo systemctl --system daemon-reload

sudo systemctl enable rtl_433.service

sudo systemctl start rtl_433.service



#Cron co 15min restart

sudo nano /etc/crontab


*/15 *    * * *   root    systemctl restart rtl_433.service

