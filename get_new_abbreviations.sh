#!/bin/bash

cat decisao.log | sed -r  's/.*(\[NEW ABV\].*)/\1/' | sort | uniq

# http://www.grymoire.com/Unix/Sed.html#uh-15