#!/bin/bash
scrapy crawl -a "iDate=20120102" -a "fDate=20140101" -a "page"=1 -a "index"=1 stf_decisao_monocratica --logfile='decisao_monocratica_2012-2013.log'
