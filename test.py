script_template = """#!/bin/bash
sudo apt update
sudo apt upgrade
sudo apt install apache2 -y
sudo a2enmod rewrite
sudo systemctl restart apache2
sudo apt install mysql-server -y
sudo apt install php php-cli php-common php-curl php-zip php-gd php-mysql php-xml php-mbstring php-json php-intl -y
sudo systemctl restart apache2
sudo apt install curl
cd /tmp
curl -s https://api.github.com/repos/PrestaShop/PrestaShop/releases/latest | grep "browser_download_url.*zip" | cut -d : -f 2,3 | tr -d \" | wget -qi -
sudo apt install unzip
sudo unzip prestashop_*.zip -d /var/www/prestashop/
sudo chown -R www-data: /var/www/prestashop/
sudo bash -c 'cat <<EOF > /etc/mysql/my.cnf
[client]
host={rds_proxy_endpoint}
user={db_user}
password={db_password}
EOF'
sudo a2ensite prestashop.conf
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
"""

# Replace placeholders with actual values
script_with_values = script_template.format(
    rds_proxy_endpoint="YOUR_RDS_PROXY_ENDPOINT",
    db_user="YOUR_DB_USER",
    db_password="YOUR_DB_PASSWORD"
)

# Print or save the modified script
print(script_with_values)
