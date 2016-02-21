#!/bin/bash

cat decisao.log | sed -nr  's/.*(\[NEW ABV\].*)/\1/p' | sort | uniq

# http://www.grymoire.com/Unix/Sed.html#uh-15