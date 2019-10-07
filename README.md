# Brazilian Supreme Court (STF) analysis decisions repository

This repository contains code used to analyze the Brazilian Supreme Court decisions.  
The source code used here is meant to support my master project at IME-USP.

## REQUIREMENTS to setup the environment used to run the analysis

The instructions should are meant for those who use Debian and other Debian-like Linux distributions.

- Python 3.6 or pyenv[1]
- pipenv python module[2]
- Linux packages
    - `build-essential`
    - `libxml2-dev`
    - `libxslt1-dev`
    - `libmpfr-dev`
    - `libmpc-dev`
    - `libssl-dev`
    - `libffi-dev`
    - `python-dev`
- Mongo 3.2+ SGBD[3]

This is a non-exhaustive list of requirements. If you identify some requirements not listed here, contact-me please.


## Setup the environment to run the experiments

In this project we use pipenv Python module[2] to create and manage virtual environments where is installed the set of Python modules required to crawl the decisions and do analyses.  
To create and use the environment you have to:

Create the environment and install the set of Python modules required to run the project typing:  
`(analise-juridica) ~/analise-juridica/$ pipenv sync --dev`

Enter the virtual environment typing:  
`(analise-juridica) ~/analise-juridica/$ pipenv shell`

Turn off the virtual environment when work is done typing:  
`(analise-juridica) ~/analise-juridica/$ exit`


## How to crawl STF data

### Set up environment variables to crawl STF decisions

To crawl decisions data you need to enter the virtual environment and set some virtual environments used by some scripts to insert data in mongo databases.

Set `MONGO_URI` and `MONGO_DATABASE` environment variables like in the example below  
`(analise-juridica) ~/analise-juridica/$ export MONGO_URI=mongodb://mongo_username:mongo_username_password@xxx.xxx.xxx.xxx:yyyyy`  
`(analise-juridica) ~/analise-juridica/$ export MONGO_DATABASE=DJs`

xxx.xxx.xxx.xxx is the IP address. When running mongo locally usually the IP address is 127.0.0.1
yyyyy is the port used to access mongo database. The standard port is 27017.

I recommend chose a non standard port and a user and password different of `admin` to prevent undesired access in the database[5].

### How to run the crawler

Decisions crawling uses the Scrapy Python module[6]. It's a framework to extract data from websites.  
We crawled collegiate decisions from STF called "acórdão" from 01/01/2001 to 30/06/2019.
When the crawling finishes the script is configured to send an e-mail to inform about the completion of decisions crawling.

The crawling triggered by the `run_crawler_and_post_processing.sh` bash script typing as follows:  
`(analise-juridica) ~/analise-juridica/scrapy$ ../automation_scripts/run_crawler_and_post_processing.sh`


## How to run PageRank experiment

This experiment consists of evaluating STF decision network robustness by perturbating the network removing 10%, 20% and 30% of network decisions.
In each perturbation the PageRank algorithm is ran 10 times for each PageRank model, PR_1 and PR_2, as informed at JURIX submitted article.

The script runs all PageRank executions in separate process to speed up experiment running and distribute all executions in 12 processes.
To use a different number of processes is necessary to modify the `makePageRankedGraph.py` script.

To run the experiment just type as follows:  
`(analise-juridica) jackson@lingcomp:~/analise-juridica$ python analysis_programs/makePageRankedGraph.py`


<!-- ## How to analysis PageRank results -->



**References**

[1] https://github.com/pyenv/pyenv  
[2] https://github.com/pypa/pipenv  
[3] https://docs.mongodb.com/manual/installation/  
[4] http://stf.jus.br/portal/jurisprudencia/pesquisarJurisprudencia.asp  
[5] https://www.dailybulletin.com/2019/07/24/7-million-student-records-leaked-from-k12-com-which-connects-students-to-online-schools/  
[6] https://scrapy.org

**About me:**

http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id=K8458830Y5  
https://www.linkedin.com/in/jacksonjsouza/
