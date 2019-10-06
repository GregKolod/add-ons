# HomeAssistant
konfiguracja własna do HA

sudo nano /etc/systemd/system/rtl_433.service


sudo systemctl --system daemon-reload

sudo systemctl enable rtl_433.service

sudo systemctl start rtl_433.service
