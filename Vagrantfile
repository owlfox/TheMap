VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.ssh.insert_key = false

  config.vm.define 'db' do |db|
    db.vm.box = "ubuntu/bionic64"
    db.vm.network "private_network", ip: "192.168.33.11"
    db.ssh.forward_agent = true
    db.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install python-minimal -y
    SHELL
  end

  config.vm.define 'web' do |web|
    web.vm.box = "ubuntu/bionic64"
    web.vm.network "private_network", ip: "192.168.33.10"
    web.ssh.forward_agent = true
    web.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install python-minimal -y
    SHELL
  end
end
