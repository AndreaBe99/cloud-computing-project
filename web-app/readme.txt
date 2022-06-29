Per far girare flask:
  - avere python3 sulla propia macchina
  - installarlo con il comando: pip install flask
  - verificare l'installazione con: python -c "import flask; print(flask.__version__)"
  - per farlo girare usare il comando 'flask run' oppure 'python nomefile.py' da terminale dopodichè verificare corretta esecuzione all'indirizzo 127.0.0.1:5000/

Bisogna avere la seguente configurazione affinchè Flask giri correttamente:
  - cartella principale che contiene il file .py
  - sottocartella chiamata 'templates' che contiene il file html
  - sottocartella chiamata 'static', in questa cartella devono essere anche le (eventuali) immagini
    - sottocartella chiamata 'styles' che contiene il file CSS
  
