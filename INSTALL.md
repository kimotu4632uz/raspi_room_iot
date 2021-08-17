# I2C有効化
raspi-config コマンドで Interface -> I2C をEnableに


# pigpiod
sudo apt install pigpio
sudo systemctl daemon-reload
sudo systemctl enable pigpiod


# ファイル配置
raspi_room_iot/ -> /var/www/ \
raspi_room_iot.conf -> /etc/nginx/conf.d/ \
uwsgi.service -> /etc/systemd/system/


# ディレクトリ作成
/var/log/uwsgi を作成(uwsgiのログ用フォルダ)


# python仮想環境 for uwsgi
以下、パーミッションの都合で sudo su して実行する \
python -m venv /opt/uwsgienv \
uwsgienvをactivateして pip install uwsgi


# python仮想環境 for raspi_room_iot
以下、パーミッションの都合で sudo su して実行する \
python -m venv /var/www/raspi_room_iot/venv \
venvをactivateして pip install flask pigpio smbus


# chown
/var/www/raspi_room_iot/ : chown -R www-data:www-data \
/var/log/uwsgi/ : chown www-data:www-data


# グループ追加
usermod -aG i2c www-data


# systemd
systemctl enable -> start


# 参考文献
https://www.indoorcorgielec.com/products/rpz-ir-sensor/
https://www.indoorcorgielec.com/resources/raspberry-pi/python-pigpio-infrared/
https://qiita.com/h_kabocha/items/531e9bdd154b50da227b \
https://inari111.hatenablog.com/entry/2016/03/30/232032 \
https://qiita.com/ekzemplaro/items/a570f79de254428a151d \
https://qiita.com/keichiro24/items/52a0e4233200ac03b4d1 \
https://stackoverflow.com/questions/25352357/how-to-collect-error-message-from-stderr-using-a-daemonized-uwsgi