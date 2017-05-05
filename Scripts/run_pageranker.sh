#!/bin/bash


function run_script {
    "$@"
    wait ${!}
    local status=$?
    if [ $status -ne 0 ]; then
        echo "Erro na execução do page ranker" | mail -s "$6 $7 $8 $9" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
        exit 1
    fi
}

run_script python makePageRankedGraph.py DJTest acordaos 80 S "" stf_pr_1_acordaos_80 1
run_script python makePageRankedGraph.py DJTest acordaos 80 S "" stf_pr_2_acordaos_80 2
run_script python makePageRankedGraph.py DJTest acordaos 70 S "" stf_pr_1_acordaos_70 1
run_script python makePageRankedGraph.py DJTest acordaos 70 S "" stf_pr_2_acordaos_70 2
run_script python makePageRankedGraph.py DJTest acordaos 90 N "" stf_pr_1_acordaos_90 1

python makePageRankedGraph.py DJTest acordaos 90 N "" stf_pr_2_acordaos_90 2
wait ${!}
if [ "$?" -ne "0" ]; then
    echo "Erro na execução do page ranker" | mail -s "Page ranker  falhou" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
    exit 1
else
    # - Envia e-mail quando scraper acabar
    echo "Todos os page rankers foram corretamente executados!" | mail -s "Todos os page rankers foram corretamente executados!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
fi

