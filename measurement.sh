#!/bin/bash

collect_sys_info=false

# Retrieve date and set up log directory if it isn't there already
today=$(date +"%Y-%m-%d-%H-%M-%S")

if [ ! -d $HOME/measurement-logs ]; then
  mkdir $HOME/measurement-logs
  collect_sys_info=true
fi

if [ ! -d $HOME/measurement-logs/sysinfo ]; then
  mkdir $HOME/measurement-logs/sysinfo
  collect_sys_info=true
fi

mkdir $HOME/measurement-logs/$today


##### SYSTEM INFO #####

cd $HOME/measurement-logs/sysinfo
sysinfo=sysinfo_$today.log

if [ "$collect_sys_info" = true ]; then

  touch uname_$sysinfo
  sudo uname -a >> uname_$sysinfo 2>&1

  touch lshw_$sysinfo
  sudo lshw >> lshw_$sysinfo 2>&1

  touch lscpu_$sysinfo
  sudo lscpu >> lscpu_$sysinfo 2>&1

  touch lspci_$sysinfo
  sudo lspci >> lspci_$sysinfo 2>&1

  touch dmidecode_$sysinfo
  sudo dmidecode >> dmidecode_$sysinfo 2>&1

fi

cd $HOME/measurement-logs/$today

touch tcp_metrics_$sysinfo
sudo ip tcp_metrics >> tcp_metrics_$sysinfo 2>&1


##### LOCAL CONNECTION INFO #####

cd $HOME/measurement-logs/$today

connecinfo=connecinfo_$today.log
touch $connecinfo
curl ipinfo.io >> $connecinfo


##### IPERF #####

cd $HOME/measurement-logs/$today

if [[ $(iperf3 --version) =~ "not found" ]]; then
   apt install iperf3
fi

# public iperf servers as listed on iperf.fr/iperf-servers.php
declare -a PublicIperfServers=(bouygues.iperf.fr ping.online.net ping6.online.net ping-90ms.online.net ping6-90ms.online.net speedtest.serverius.net iperf.eenet.ee iperf.volia.net iperf.it-north.net iperf.biznetnetworks.com iperf.scottlinux.com iperf.he.net)

length=${#PublicIperfServers[@]}

valid_iperf=false

# run iperf to public servers until one runs correctly
while  [ "$valid_iperf" = false ]; do
   index=$(( RANDOM % $length ))
   server=${PublicIperfServers[$index]}

   logfile=iperf3_${server}_$today.log
   touch $logfile

   # server speedtest.serverius.net listens on port 5002 as opposed to 5001
   if [ $server == speedtest.serverius.net ]; then
	iperf3 -c $server -p 5002 -V --omit 2 --logfile $logfile
   else
	iperf3 -c $server -V --omit 2 --logfile $logfile
   fi

   # check if the iperf got an error message
   # if it didn't, great, end the while loop
   # if it did, delete the log and try again
   if ! [[ $(cat $logfile) =~ "error" ]]; then
	valid_iperf=true
   else
	rm $logfile
   fi

done

##### GET HOSTS #####
readarray -t sites < sites.txt

##### TRACEROUTE TO HOSTS #####
cd $HOME/measurement-logs/$today


##### PINGS TO HOSTS WITH INCREMENTAL TTL #####
cd $HOME/measurement-logs/$today


exit 0
