#!/usr/bin/env bash

function device() {
  local module=$1
  local port=$2
  local extra=$3

  echo "port[$port]: $module"
  flask --app devices.$module run --port $port $extra | grep -v "This is a development server" & # who cares

  if command -v dns-sd &> /dev/null; then
    dns-sd -P $module _bbxsrv local. $port localhost 127.0.0.1 &
  fi
}

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# ---
device switchboxd_20190808 5001 --reload
device switchboxd_20200229 5002 --reload
device switchboxd_20200831 5003 --reload
# ---
device switchbox_20180604 5011 --reload
device switchbox_20190808 5012 --reload
device switchbox_20200229 5013 --reload
device switchbox_20200831 5014 --reload
device switchbox_20220114 5015 --reload
# ---
device floodsensor_20200831 5021 --reload
device floodsensor_20210413 5022 --reload
# ---
device windrainsensor_20200831 5031 --reload
device windrainsensor_20210413 5032 --reload
# ---
device wlightbox_20200229 5041 --reload
# ---
MODE=1 VARIANT=segmented            device shutterbox_20190911 5051
MODE=2 VARIANT=nocalib              device shutterbox_20190911 5052
MODE=3 VARIANT=tilt                 device shutterbox_20190911 5053
MODE=4 VARIANT=window               device shutterbox_20190911 5055
MODE=5 VARIANT=material             device shutterbox_20190911 5056
MODE=6 VARIANT=awning               device shutterbox_20190911 5057
MODE=7 VARIANT=screen               device shutterbox_20190911 5058
MODE=8 VARIANT=curtain              device shutterbox_20190911 5059


# --- faulty devices ---
FAULTY=1 MODE=3 VARIANT=tilt-faulty device shutterbox_20190911 5953


while true; do
  sleep 0.1
done
