This project is an example of how to combine virtualbox, kickstart and fabric to deploy
a simple web service to multiple environments.

The overall process uses fabric to build virtualbox CentOS images using virtualbox and kickstart to configure 
hosts. These images can then have web services deployed to them.

The fabric/monitor.py script (incomplete) is intended to monitor system performance and start or stop
vms as needed reusing the fabric code in a daemon process. However, everything that monitor.py does can
be done on the command line via fabric.

Directories:
booted/fabric
 - management code using python fabric

booted/inventory (not in repo)
 - temporary inventory of hosts that are (probably) currently live

booted/iso  
 - CentOS iso image used by kickstart script

booted/kickstart  
 - web visible directory with kickstart configuration script

booted/nginx  
 - example nginx configs for serving kickstart script and detecting hosts that have started

booted/service  
 - the web service(s) that are deployed by the fabric scripts

booted/VirtualBox
 - location of images created by virtualbox and used by the fabric scripts


The overall architecture is that there are two types of hosts:
 - load balancers that farm out work to workers and relay responses (work in progress)
 - workers that do the actual work

The booted/fabric/envmanager.py module uses a manually configured environments.py module to define 
groups of images. These images are associated with specific roles and versions of services. 
We are assuming that only one service runs on one host. However, the hosts can share roles.

The booted/fabric/hostbuilder.py module takes care of managing virtualbox images. Cloning images
was found to be problematic so the current working process is to make more images than are needed
ahead of time and enable or disable them as needed. The vbox.sh script runs the virtualbox commands
to make a server image. During the process of being built server images contact a local nginx web
server to get the kickstart/centos-ks.cfg file to configure themselves. 

The booted/fabric/hostmanager.py handles working with a group of live hosts. These hosts are 
discovered via the booted/inventory/booted_log file (defined in the BOOTED_LOG environment variable).
This log is populated by a local nginx process which is contacted by hosts when they start.
The hostmanager.py maintains a hosts.py file which contains the current list of hosts that it 
knows about. This list is not assumed to be static and should be refreshed before being used.

The booted/fabric/deploy.py module handles deploying, setting up and testing services on a group
of hosts previously defined by running a hostmanager goal. It uses the convention of {service}_{op}
to define operations for specific services. When envmanager invokes a deploy goal it takes the
"service" as a parameter.

The booted/fabric/monitor.py script (work in progress) is intended to be an ongoing daemon process
that automates running the envmanager fabric goals to manage a group of hosts for a specific environment.

Complete list of fabric goals:

    env_start_all     spins up all hosts in a group and deploys a service to them
    env_start_min     start minimal number of hosts in a group
    env_start_worker  (re)starts a specific worker image and service
    env_stop          stops all hosts in a group
    hello_deploy      deploy version of the hello service to current hosts
    hello_start       (re)starts the hello service on all servers
    hello_stop        stops the hello service on all servers
    hello_test        do basic sanity check of deployed hello service
    hosts_clear       clear the current env.hosts list
    hosts_filter      get contactable hosts using ping
    hosts_list        list current hosts
    hosts_logged      get all hosts in booted_log
    hosts_reset       do a hard reset of env.hosts
    image_build       create a generic host image using virtualbox
    image_clone       clone an existing image using virtualbox: DO NOT USE
    image_del         manually delete a specific image
    image_list        list all available virtualbox images
    image_start       manually start a specific image
    image_stop        manually stop a specific image
    restart_nginx     restart local nginx and make a new booted log file

Environment variables:
BOOTED_USER, BOOTED_PW, BOOTED_LOG, HELLO_REPO

Gotchas:

VirtualBox's TFTP directory should be copied to ~/.config/VirtualBox or virtualbox's DHCP process will not
see it.

VirtualBox cannot gracefully modify the mac addresses of host (networking won't start). At the moment we
don't try and change the mac address but this has the effect of giving cloned hosts the same IP address.

Currently adding a host name to the host is not implemented.

There are hard coded directories and a default root password ("bootstrap") in the code. The directories may
need to be changed depending on your environment.

To reduce size some files referenced by kickstart and pxe are not included.


Cal Woodruff
cwoodruf@sfu.ca

