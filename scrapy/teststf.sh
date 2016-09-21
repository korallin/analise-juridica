#!/bin/bash

# to run this script do time ./teststf.sh

decisoes="acordao decisao_monocratica"
for decisao in $decisoes
    do
    for i in {2001..2016..2}
        do
            echo "Coletando stf_$decisao dos anos $i and $((i+1))"
            J=$((i+2))
            secondDay="0102"
            firstDay="0101"
            anoI=$i$secondDay
            anoF=$J$firstDay
            if ((J > 2016)); then
                J="2016"
                firstDay="0630"
                anoF=$J$firstDay
            fi;
            acordaoLogFileName=$decisao"_$i-$((i+1)).log"
            scrapy crawl -a "iDate=$anoI" -a "fDate=$anoF" -a "page"=1 -a "index"=1 stf_$decisao --logfile=$acordaoLogFileName
            wait ${!}
    done
done
