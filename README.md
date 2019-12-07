# HomeAssistant
konfiguracja własna do HA

sudo nano /etc/systemd/system/rtl_433.service


sudo systemctl --system daemon-reload

sudo systemctl enable rtl_433.service

sudo systemctl start rtl_433.service



#Cron co 15min restart

sudo nano /etc/crontab


*/15 *    * * *   root    systemctl restart rtl_433.service

