library(pdftools)
text <- pdf_text("7f620e1dcf223c2e5b5c38c890f8379b13e2d86a.asp?idDocumento=4026354")
text[[1]]

# exibe linhas praticamente como aparecem no pdf
text2 <- strsplit(text, "\n")

primeiro índice corresponde à página do pdf e segundo corresponde à linha do pdf
text2[[1]][[2]]

# table of contents
toc = pdf_toc("7f620e1dcf223c2e5b5c38c890f8379b13e2d86a.asp?idDocumento=4026354")


# pela estrutura do pdf o índice 2 é onde está presente o conteúdo de interesse
# o segundo índice contém as strings de interesse
toc[[2]][[1]][[1]]

info <- pdf_info("7f620e1dcf223c2e5b5c38c890f8379b13e2d86a.asp?idDocumento=4026354")
info$pages
info$created



# https://medium.com/@CharlesBordet/how-to-extract-and-clean-data-from-pdf-files-in-r-da11964e252e
# https://ropensci.org/blog/2016/03/01/pdftools-and-jeroen/
# https://github.com/ropensci/pdftools

# Processamento de linguagem natural
# https://github.com/pedrobalage/Portuguese-Natural-Language-Processing-with-Python
# https://likegeeks.com/nlp-tutorial-using-python-nltk/
# http://www.nyu.edu/projects/politicsdatalab/localdata/workshops/NLTK_Presentation.pdf
# https://towardsdatascience.com/machine-learning-nlp-text-classification-using-scikit-learn-python-and-nltk-c52b92a7c73a
# https://blog.hyperiondev.com/index.php/2018/01/15/nlp-tutorial-python-natural-language-processing/
# https://pythonprogramming.net/graph-live-twitter-sentiment-nltk-tutorial/?completed=/twitter-sentiment-analysis-nltk-tutorial/
# http://www.nltk.org/book_1ed/ch01.html
# http://www.nltk.org/howto/portuguese_en.html

# adicionar linha abaixo no /etc/apt/sources.list
# deb https://vps.fmvz.usp.br/CRAN/bin/linux/debian xenial/
# https://cran.r-project.org/bin/linux/ubuntu/
# seguir instruções da seção "Secure APT" no link acima
# sudo apt update
# sudo apt install r-base r-base-dev

# Para pdftools
# sudo apt install libpoppler-cpp-dev
# Para tesseract
# sudo apt install libxml2-dev libcurl4-openssl-dev libtesseract-dev libleptonica-dev tesseract-ocr-por
# install.packages("pdftools")
# install.packages("tesseract")
# install.packages("png")

# swig swig3.0 libpulse-dev
# https://github.com/kba/awesome-ocr
# https://github.com/tesseract-ocr/tesseract
# https://github.com/tesseract-ocr/tesseract/wiki/ImproveQuality#noise-removal

library("png")
pdf <- 'AP300.pdf'
img <- pdf_render_page(
  pdf = pdf,    # caminho do arquivo
  page = 2,     # índice da página
  dpi = 300     # resolução (pontos por polegada)
)

# salvando imagem num arquivo png
png::writePNG(img, 'AP300.png')

library(tesseract)
txt <- ocr('AP300.png', tesseract("por"))
