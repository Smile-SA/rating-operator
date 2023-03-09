# **Installation**

## Introduction

In this document we show how to set up a test/minimal local instance of Rating Operator.

## Pre-requisites

## Virtual box installation

On a local machine, install virtualbox to launch three nodes for cluster  

```console
sudo apt-get install virtualbox
```

## Cluster creation using vagrant
```console
sudo apt-get install vagrant
```

Here is the script to launch one master and two worker nodes

Vagrantfile
```console

Vagrant.configure("2") do |config|
  # Set up the master node
  config.vm.define "master" do |master|
    master.vm.box = "ubuntu/jammy64"
    master.vm.network "public_network", ip: "192.168.56.10"
    master.vm.provision "shell", inline: <<-SHELL
      curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -
    SHELL
  end

  # Set up the worker nodes
  (1..2).each do |i|
    config.vm.define "worker#{i}" do |worker|
      worker.vm.box = "ubuntu/jammy64"
      worker.vm.network "public_network", ip: "192.168.56.#{10 + i}"
      worker.vm.provision "shell", inline: <<-SHELL
        curl -sfL https://get.k3s.io | K3S_URL=https://192.168.56.10:6443 K3S_TOKEN=token sh -
      SHELL
    end
  end
end
```
then,
```
vagrant up
```

This should launch three local vms with k3s configured, we can get the cluster configuration file from master node at '/etc/rancher/k3s/k3s.yaml' and add it to local machine './kube/config'


Don't forget to include namespace in the config file:

```
contexts:
- context:
    cluster: default
   **namespace: rating**
    user: default
  name: default
current-context: default
```

# Rating Operator Installation

Once we have the local cluster ready, we need to clone rating operator and follow the installation steps mentioned [here](/documentation/INSTALL.md)

