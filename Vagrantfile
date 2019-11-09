VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.network "private_network", ip: "192.168.68.68"
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install python-minimal -y
  SHELL
end
