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

echo -n "Enter your MongoDB user name and press [ENTER]: "
read mongo_user
echo -n "Enter your MongoDB password and press [ENTER]: "
read -s mongo_password

run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_1_acordaos_90 > page_rank_1_acordaos_90.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_90 > page_rank_2_acordaos_90.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_90_par > page_rank_2_acordaos_90_par.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_1_acordaos_80 > page_rank_1_acordaos_80.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_80 > page_rank_2_acordaos_80.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_80_par > page_rank_2_acordaos_80_par.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_1_acordaos_70 > page_rank_1_acordaos_70.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_70 > page_rank_2_acordaos_70.txt
run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_70_par > page_rank_2_acordaos_70_par.txt


file_names=("page_rank_1_acordaos_90.txt" "page_rank_2_acordaos_90.txt" "page_rank_1_acordaos_80.txt"
            "page_rank_2_acordaos_80.txt" "page_rank_1_acordaos_70.txt" "page_rank_2_acordaos_70.txt",
            "page_rank_2_acordaos_80_par.txt" "page_rank_1_acordaos_70_par.txt" "page_rank_2_acordaos_70_par.txt")
for i in {1..10}
do
    run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_1_acordaos_90_rel_"$i" > page_rank_1_acordaos_90_rel_"$i".txt
    run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_90_rel_"$i" > page_rank_2_acordaos_90_rel_"$i".txt
    run_script python compare_top_page_rank_decisions.py $mongo_user $mongo_password DJs stf_pr_2_acordaos_90_par_rel_"$i" > page_rank_2_acordaos_90_par_rel_"$i".txt
    file_names+=("page_rank_1_acordaos_90_rel_"$i".txt" "page_rank_2_acordaos_90_rel_"$i".txt" "page_rank_2_acordaos_90_par_rel_"$i".txt")
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
