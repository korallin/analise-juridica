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

echo -n "Enter your MongoDB user name and press [ENTER]: "
read mongo_user
echo -n "Enter your MongoDB password and press [ENTER]: "
read -s mongo_password
echo -n "Enter your MongoDB port and press [ENTER]: "
read mongo_port

init_message="Esta é uma mensagem automática

Oi Marcelo,
Eu comecei a executar as simulações do PageRank.
Assim que elas acabarem você será avisado via e-mail.

Abraços,
Jackson
"
echo -e "$init_message" | mail -s "Comecei a executar a simulação do PageRank" -r "Jackson Souza<jackson@ime.usp.br>" mfinger@ime.usp.br


# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 90 S "" stf_pr_1_acordaos_90 1
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 90 S "" stf_pr_2_acordaos_90 2
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 80 S "" stf_pr_1_acordaos_80 1
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 80 S "" stf_pr_2_acordaos_80 2
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 70 S "" stf_pr_1_acordaos_70 1
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 70 S "" stf_pr_2_acordaos_70 2
# run_script python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 90 N "" stf_pr_1_acordaos_90 1
# run_script pipenv run ../analysis_programs/makePageRankedGraph.py $mongo_user $mongo_password $mongo_port DJs acordaos 90 S "" stf_pr_1_acordaos_90_no_similars 1 N

# python makePageRankedGraph.py $mongo_user $mongo_password DJs acordaos 90 N "" stf_pr_2_acordaos_90 2
pipenv run ../analysis_programs/makePageRankedGraph.py $mongo_user $mongo_password $mongo_port DJs acordaos 90 S "" stf_pr_2_acordaos_90_no_similars 2 N
wait ${!}
if [ "$?" -ne "0" ]; then
    echo "Erro na execução do page ranker" | mail -s "Page ranker falhou" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
    exit 1
else
end_message="Esta é uma mensagem automatica.\n
Marcelo, todas as simulacoes do PageRank
foram executadas com sucesso.\n
Pode desligar ou reiniciar a maquina se precisar.\n
Abracos,\nJackson"

    # - Envia e-mail quando scraper acabar
    echo "Todos os page rankers foram corretamente executados!" | mail -s "Todos os page rankers foram corretamente executados!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
    echo -e "$end_message" | mail -s "Todos os page rankers foram corretamente executados!" -r "Jackson Souza<jackson@ime.usp.br>" mfinger@ime.usp.br
fi
