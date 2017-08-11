#!/bin/bash
# make a base virtualbox image that we can use to install the os on
if [ "x$VMBASE" = "x" ]
then
    export VMBASE=`/bin/pwd`/..
fi
export VMDIR="$VMBASE/VirtualBox"
if [ ! -d $VMDIR ]
then
    echo "$VMDIR does not exist"
    exit 1
fi
vmname=$1
if [ "x$vmname" = "x" ]
then
    echo "need a vbox name"
    exit 1
fi

cd $VMBASE
export ISO="$VMBASE/iso/CentOS-6.9-x86_64-minimal.iso" 

VBoxManage createvm --name "$vmname" --basefolder $VMDIR --ostype RedHat_64 --register
if [ $? -ne 0 ]
then
    echo "error creating vm"
    exit 1
fi

# want something lightweight for testing
VBoxManage modifyvm "$vmname" --cpus 1
VBoxManage modifyvm "$vmname" --memory 1024
# advanced programmable interrupt controller - allows more than 14 IRQs
VBoxManage modifyvm "$vmname" --ioapic on
# advanced configuration and power interface
VBoxManage modifyvm "$vmname" --acpi on

VBoxManage modifyvm "$vmname" --boot1 net --boot2 disk --boot3 dvd --boot4 none
VBoxManage modifyvm "$vmname" --nic1 NAT 
# note that giving an absolute path here is ignored - TFTP must be in the ~/.config/VirtualBox directory
VBoxManage modifyvm "$vmname" --nattftpfile1 pxelinux.0
VBoxManage modifyvm "$vmname" --nic2 bridged --bridgeadapter2 eth0
VBoxManage modifyvm "$vmname" --vrdeauthtype null

hddfile="$VMDIR/$vmname/${vmname}-disk01.vdi"
VBoxManage storagectl "$vmname" --name "SATA Controller" --add sata
VBoxManage createvdi --filename $hddfile --size 40000
VBoxManage storageattach "$vmname" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium $hddfile

VBoxManage storagectl "$vmname" --name "IDE Controller" --add ide
VBoxManage storageattach "$vmname" --storagectl "IDE Controller" --port 0 --device 1 --type dvddrive --medium "$ISO"

echo "starting $vmname"
VBoxHeadless --startvm "$vmname" --vrde off

echo "reconfiguring $vmname"
VBoxManage storageattach "$vmname" --storagectl "IDE Controller" --port 0 --device 1 --type dvddrive --medium emptydrive
VBoxManage modifyvm "$vmname" --boot1 disk --boot2 dvd --boot3 net --boot4 none
echo "done"

