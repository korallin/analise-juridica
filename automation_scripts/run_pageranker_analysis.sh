#!/bin/bash


function run_script {
    "$@"
    wait ${!}
    local status=$?
    if [ $status -ne 0 ]; then
        echo "Erro na execução do page ranker" | mail -s "$3 $4" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
        exit 1
    fi
}


run_script python compare_top_page_rank_decisions.py DJTest stf_pr_1_acordaos > page_rank_1_acordaos.txt
run_script python compare_top_page_rank_decisions.py DJTest stf_pr_2_acordaos > page_rank_2_acordaos.txt
run_script python compare_top_page_rank_decisions.py DJTest stf_pr_1_acordaos_80 > page_rank_1_acordaos_80.txt
run_script python compare_top_page_rank_decisions.py DJTest stf_pr_2_acordaos_80 > page_rank_2_acordaos_80.txt
run_script python compare_top_page_rank_decisions.py DJTest stf_pr_1_acordaos_70 > page_rank_1_acordaos_70.txt
run_script python compare_top_page_rank_decisions.py DJTest stf_pr_2_acordaos_70 > page_rank_2_acordaos_70.txt


file_names=("page_rank_1_acordaos.txt" "page_rank_2_acordaos.txt" "page_rank_1_acordaos_80.txt"
            "page_rank_2_acordaos_80.txt" "page_rank_1_acordaos_70.txt" "page_rank_2_acordaos_70.txt")
for i in {1..10}
do
    run_script python compare_top_page_rank_decisions.py DJTest stf_pr_1_acordaos_90_rel_"$i" > page_rank_1_acordaos_90_rel_"$i".txt
    run_script python compare_top_page_rank_decisions.py DJTest stf_pr_2_acordaos_90_rel_"$i" > page_rank_2_acordaos_90_rel_"$i".txt
    file_names+=("page_rank_1_acordaos_90_rel_"$i".txt" "page_rank_2_acordaos_90_rel_"$i".txt")
done



files_content_to_concat=()
for f in ${file_names[@]}
do
    lines="`tail -1 $f`"
    files_content_to_concat+=("`tail -$lines $f`")
done

# escrever conteúdo do array em um arquivo
printf "%s\n" "${files_content_to_concat[@]}" > page_rank_simulacoes_comparacao.txt

wait ${!}
if [ "$?" -ne "0" ]; then
    echo "Erro na execução da análise" | mail -s "Análise dos resultados do page ranker falhou" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
    exit 1
else
    echo "Análise foi executada corretamente!" | mail -s "Análise foi executada corretamente!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
fi
