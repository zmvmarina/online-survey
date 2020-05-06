#!/bin/bash
# Must be logged in as non-root sudo user
sudo apt update
sudo apt install nginx python3 python3-pip python3-dev ufw git
# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
pip3 install --user pipenv
cd ~
# # To use python packages from console
echo "PYTHON_BIN_PATH='$(python3 -m site --user-base)/bin'
PATH='$PATH:$PYTHON_BIN_PATH'" >> .bashrc 
# Source .bashrc won't work in a script
mkdir .venv # Sets pipenv to put everything in .venv
python3 -m pipenv install -e . # install from setup.py
cd ..
# gunicorn --preload means that we load our app before launching workers. This makes workers share multiprocessing locks
echo "[Unit]
Description=Gunicorn instance to serve online-survey
After=network.target
[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/online-survey
Environment="PATH=/home/$USER/online-survey/.venv/bin"
ExecStart=/home/$USER/online-survey/.venv/bin/gunicorn --preload --workers 3 --bind unix:online-survey.sock -m 007 wsgi:app
[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/online-survey.service # Create service to run app on startup
echo "server {
    listen 443 ssl;
    listen [::]:443 ssl;
    ssl_certificate /etc/letsencrypt/live/online-survey.oatmeal.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/online-survey.oatmeal.cc/privkey.pem;
    server_name online-survey.oatmeal.cc;
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/$USER/online-survey/online-survey.sock;
    }
}
server {
    listen 80;
    listen [::]:80;
    server_name online-survey.oatmeal.cc;
    return 302 https://$server_name$request_uri;
}" | sudo tee /etc/nginx/sites-available/online-survey # Nginx will catch all requests and forward them to unischeduler_web
sudo ln -s /etc/nginx/sites-available/online-survey /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl start online-survey
sudo systemctl enable online-survey
sudo systemctl restart nginx
