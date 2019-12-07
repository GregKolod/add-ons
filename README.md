# HomeAssistant
konfiguracja własna do HA

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

