sudo yum install python3
sudo yum install firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
sudo yum install git
git clone https://github.com/adarshtri/chord-dht.git
cd chord-dht
mkdir logs
