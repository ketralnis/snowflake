#!/bin/sh

set -e

pkg update

xargs pkg install -y <<PACKAGES
python27
py27-Flask
py27-sqlite3
py27-mako
sudo
vim-lite
sqlite3
PACKAGES

# will attach to python27 now that that's installed
pkg install -y python

cd /snowflake
python ./setup.py develop

SNOWFLAKE="python -m snowflake.cmd -d /var/db/snowflake.db"

if ! [ -f /var/db/snowflake.db ]; then
    $SNOWFLAKE --init
fi

if [ -f /snowflake/samples.txt ]; then
    echo "Importing samples from samples.txt"
    $SNOWFLAKE --import /snowflake/samples.txt
fi

if [ -f /snowflake/labels.txt ]; then
    echo "Importing labels from labels.txt"
    $SNOWFLAKE --labels $(cat /snowflake/labels.txt)
fi

# these won't do anything but it's nice to be sure that they work
$SNOWFLAKE --export
$SNOWFLAKE --export-ratings

cp -p /snowflake/rc.sh /usr/local/etc/rc.d/snowflake
chmod a+x /usr/local/etc/rc.d/snowflake

sysrc snowflake_enable="YES"
sysrc snowflake_db="/var/db/snowflake.db"

service snowflake start
sleep 1 # wait for it to come up

if ! pgrep -fl snowflake; then
    echo "snowflake failed to come up"
    exit 1
fi

echo "*************************"
echo "Installation complete."
echo "You can access the server at:"
echo "http://localhost.localdomain:8080/"
echo "If you are developing you might want to:"
echo "    vagrant rsync-auto"
echo "*************************"