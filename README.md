This repository contains code used to analyze the Brazilian Supreme Court decisions 

Code used here is meant to support my master project at IME-USP. 

Instruction to configure your environment to run the code:
The instructions should are meant for those use Debian and other Linux distributions.

You must have python 2.7 installed and the "libxml2-dev" e "libxslt1-dev" packages.
May be necessary install other packages that I had already installed at my machine.

I advise you create a virtual environment using the virtualenv[1] module.

To install this command at Linux command line type:
pip install virtualenv

To create a virtualenv type choose a directory name you like and type:
virtualenv diretory-name-you-like

Move the repository code to the newly created virtual environment:
cd repository-directory  virtual-environment-directory 

Change to virtual environment directory:
cd virtual-environment-directory-path

Activate environment typing:
source bin/activate

The necessary Python modules are listed to code work are listed
requirements.txt file inrepository-directory.

To install all modules listed at this file type:
pip install -r requirements.txt

If you have any issue installing this code tell me so I can improve the instructions to use this code.

For further details aboute creating a virtualenv check
[1] https://virtualenv.readthedocs.org/en/latest/userguide.html

Thanks!
