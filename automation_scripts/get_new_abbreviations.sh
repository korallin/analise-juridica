#!/bin/bash

cat decisao_* | sed -nr  's/.*(\[NEW ABV\].*)/\1/p' | sort | uniq > abreviacoes_nao_previstas.txt
cat decisao_* | sed -nr  's/.*(\[LOOK ABBRV\].*)/\1/p' | sort | uniq > inspecionar_abreviacoes.txt

# outras buscas
# "possui mais de 10 documentos na"
# "nao possui inteiro teor!"
# "possui menos de 10 documentos na página"
# "We have a new section called"
# http://www.grymoire.com/Unix/Sed.html#uh-15