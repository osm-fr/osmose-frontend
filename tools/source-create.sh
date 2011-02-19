#! /usr/bin/zsh

i=$( psql --tuples-only -d osmose -c "SELECT max(source)+1 FROM dynpoi_source;" osmose | tr -d " \n" )
echo "source=$i"

md=$(dd if=/dev/urandom count=1k bs=1 2> /dev/null | md5sum | cut -d " " -f 1) 
echo "code=$md"
    
echo -n "mail="
read ml
    
echo -n "description="
read ds
    
sq="INSERT INTO dynpoi_source VALUES ($i, '$md', '$ml', '$ds');"
echo $sq
    
psql --tuples-only -d osmose -c "$sq" osmose
