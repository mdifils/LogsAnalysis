# -*- mode: ruby -*-
# vi: set ft=ruby :

# Installation script
$script = <<SCRIPT
echo "updating package lists ..........."
sudo apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

echo "installing postgres ............."
sudo apt-get -y install postgresql postgresql-contrib

echo "creating vagrant role and database news ..........."
sudo su postgres -c "createuser -dRS vagrant"
sudo su vagrant -c "createdb"
sudo su vagrant -c "createdb news"
sudo su vagrant -c 'psql news -f /vagrant/newsdata.sql'

echo "installing pip .................."
sudo apt-get -y install python3-pip
pip3 install --upgrade pip

vagrantTip="[35m[1mThe shared directory is located at /vagrant\\nTo access your shared files: cd /vagrant[m"
echo -e $vagrantTip > /etc/motd

echo "Done installing your virtual machine!"
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_version = "= 20180831.0.0"
  config.vm.synced_folder ".", "/vagrant"

  config.vm.provision "shell", inline: $script
end
