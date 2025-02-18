#! /bin/bash

# This script is used to catch up my development db from the production db.
# You may delete this file if you are running this locally.
read -p "Are you Sure? Will erase this machine's db " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Copying production db to development db..."
    scp der0r0@hackclub.app:/home/der0r0/isotope/data/data.db /Users/rorozee/Documents/Programming\ Projects/Python/isotope/data/
    echo "Finished copying production db to development db."
fi