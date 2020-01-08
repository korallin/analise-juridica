#!/bin/bash

# to run this script do 'time bash ../automation_scripts/run_crawler_and_post_processing.sh' inside scrapy directory

# decisoes="acordao decisao_monocratica"
log_dir="/home/jackson/analise-juridica/scrapy_logs/"
if [ ! -d $log_dir ]; then
  mkdir -p $log_dir;
fi
decisoes="acordao"
for decisao in $decisoes
    do
    for i in {2001..2020..2}
        do
            echo "Coletando stf_$decisao dos anos $i and $((i+1))"
            J=$((i+2))
            init_day="0102"
            last_day="0101"
            anoI=$i$init_day
            anoF=$J$last_day
            if ((J > 2018)); then
                J="2020"
                last_day="0101"
                anoF=$J$last_day
            fi;
            acordaoLogFileName=$log_dir$decisao"_$i-$((i+1)).log"
            scrapy crawl -a "iDate=$anoI" -a "fDate=$anoF" -a "page"=1 -a "index"=1 stf_$decisao --logfile=$acordaoLogFileName
            wait ${!}
    done
done

if [ "$?" -ne "0" ]; then
    echo "Erro na execução do scraper" | mail -s "Erro na execução do scraper" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
    exit 1
else
    # - Envia e-mail quando scraper acabar
    echo "Scraping realizado com sucesso!" | mail -s "Scraping realizado com sucesso!" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
fi

# sh get_new_abbreviations.sh
# echo "return status is $?"
# wait ${!}
#
# python ../Scripts/create_citations_graphs.py
# echo "return status is $?"
# wait ${!}
# python ../Scripts/download_remaining_inteiros_teores.py
# echo "return status is $?"
# wait ${!}
# python ../Scripts/remove_inteiros_teores_estranhos.py
# echo "return status is $?"
# wait ${!}
# python ../Scripts/matriz_perplexidade_cortes_stf.py
# echo "return status is $?"
# wait ${!}
#
# mv abreviacoes_nao_previstas.txt inspecionar_abreviacoes.txt matriz_perplexidade.txt ../logs_para_melhorar_analises
# echo "return status is $?"
# wait ${!}
#
# # - Envia e-mail quando script inteiro acabar
# echo 'Scripts de processamento realizados.\nConferir resultado.' | mail -s "Scripts de processamento realizados" -r "Jackson<jackson@ime.usp.br>" jackson@ime.usp.br
