Pairs
=====

Pair programming session providing service

Installation
------------

    ## repo clone to your local
    $ git clone git@github.com:woojing/pairgramming.git pairs
    
    ## change directory to git repo
    $ cd pairs
    
    ## pip package install
    $ pip install -r dj_backend/requirements.pip
    
    ## make your own local setting file
    ## you should change SECRET_KEY. do not use default.
    $ echo '# -*- coding: utf-8 -*-
    ALLOWED_HOSTS = []
    SECRET_KEY = "your_own_random_string_secret_key"
    ' > dj_backend/dj_backend/local_settings.py
    
    ## database initialize
    $ python dj_backend/manage.py syncdb
    
    ## run tornado server
    $ python dj_backend/sock_serv.py &
    
    ## run django server
    $ python dj_backend/manage.py runserver 0:8000
    
  open your browser and connect to http://YOUR_IP:8000
