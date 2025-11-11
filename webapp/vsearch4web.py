#executar no ubuntu  -> cd webapp/;python3 vsearch4web.py
#         no browser -> http://127.0.0.1:5000/ ou /entry - pg principal
#                       http://127.0.0.1:5000/login 
#                       http://127.0.0.1:5000/logout
#                       http://127.0.0.1:5000/
#                       http://127.0.0.1:5000/viewlogTXT
#                       http://127.0.0.1:5000/viewlogDB

#executar com DB -> sudo service mysql start
#                -> sudo mysqladmin -p -u root version
#                -> sudo mysql -u root -p <enter>"Mre112233"  
#                -> sudo mysql -u vsearch -p <enter>"mree"  
#                -> show databases;  use vsearchlogDB;  show tables;   select * from log;

from flask import Flask, render_template, request, redirect, escape, session, copy_current_request_context
from vsearch import search4letters  #importa funcao "mymodules/vsearch.py"
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in
from threading import Thread
from time import sleep

app = Flask(__name__)  #captura a instancia do Flask

app.config['dbconfig'] = { 'host': 'localhost',    #parametros DB
                 'user': 'vsearch',     
                 'password': 'mree',    
                 'database': 'vsearchlogDB', }

app.secret_key='YouWillNeverGuessMySecretKey'

#--------------------------------------------------------------------------------------------------------
#chama HTML principal "entry"
@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')
        
#esta funcao eh chamada pela pagina principal HTML "entry" ou "index"
@app.route('/search4', methods=['POST'])  #informa o servidor q tipo de metodo ira utilizar para a URL, se nao informa nada o padrao eh GET
def do_search() -> 'html': # informa q esta funcao ira devolver HTML
    #Extract the posted data; perform the search; return results
    
    @copy_current_request_context #salva contexto HTTP para utilizar na thread
    def log_request(req: 'flask_request', res: str) -> None:
    # Log details of the web request and the results
    #raise Exception("Something awful just happened.") lança uma exception se quiser debugar
        sleep(15) #this makes log_request really slow ...
        #grava DB
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL="""insert into log
                    (phrase, letters, ip, browser_string, results)
                    values (%s, %s, %s, %s, %s)"""
                cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))
        except ConnectionError as err:
            print('(1)Is your database switched on? Error - ',str(err))
        except Exception as err:
            print('(1)DB Logging failed with this error-',str(err))

        #grava TXT
        try:
            with open('vsearch.log', 'a') as log: #para alimentar arquivo Log
              print(req.form['phrase'], req.form['letters'], req.remote_addr, req.user_agent.browser, res, file=log, sep=';') #sep='|'  #pega dados do form HTML e tb informacoes do request
              print('\n') 
        except Exception as err:
            print('(2)TXT Logging failed with this error-',str(err))
    
    phrase = request.form['phrase'] #pega do form HTML estes campos
    letters = request.form['letters']
    title = 'Here are your results:'
    
    #chama funcao "log_request" q grava o LOG em DB e TXT utiliza THREAD
    results = str(search4letters(phrase, letters))  #chama a funcao do "mymodules/vsearch.py"
    try:        
        t=Thread(target=log_request,args=(request,results))
        t.start()
        #log_request(request, request,results) codigo antes da thread
    except Exception as err:
        print('(2)Logging failed with this error-',str(err))

    #ao final exibe HTML "results"
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results,) #ultima virgula nao tem problema pro python

@app.route('/login')   #atribui a URL para a instancia ativa
def do_login() -> str:
    session['logged_in']=True
    return 'You are logged in.'

@app.route('/logout')
def do_logout() -> str:
    if 'logged_in' in session:
        session.pop('logged_in')
    return 'You are now logged out.'

#---------Display the contents of the log file as a HTML table - TXT    
@app.route('/viewlogTXT')
@check_logged_in
def view_the_logTXT() -> 'html':
    try:    
        contents = []
        with open('vsearch.log', 'r', encoding="utf-8") as log:
            for line in log:
                columns = line.strip().split(';')
                contents.append(columns)
        titles = ('Phrase', 'Letters', 'Remote addr', 'User agent', 'Results')
        return render_template('viewlog.html', the_title='View Log - TXT', the_row_titles=titles, the_data=contents,)
    except Exception as err:
        print('TXT - Something went wrong-',str(err))
        return 'Error->'+str(err)

#---------Display the contents of the log file as a HTML table - DB    
@app.route('/viewlogDB')
@check_logged_in
def view_the_logDB() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL="""select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contents=cursor.fetchall()
            titles=('Phrase','Letters','Remote addr','User_agent','Results')    
            return render_template('viewlog.html',
                            the_title='View Log - DB',
                            the_row_titles=titles,
                            the_data=contents,)
    except ConnectionError as err:
        print('Is your database switched on? Error - ',str(err))
        return 'Error->'+str(err)
    except CredentialsError as err:
        print('DB User-id/password issues. Error - ',str(err))
        return 'Error->'+str(err)
    except SQLError as err:
        print('Is your query correct? Error - ', str(err))
        return 'Error->'+str(err)
    except Exception as err:
        print('DB Something went wrong-',str(err))
        return 'Error->'+str(err)

#essa parte do codigo deve ser estar no final do arquivo !!!!
#o codigo abaixo inicia a Instancia do Flask no WebServer e possibilita roda-lo de qq lugar ex.Cloud
#pra subir pra Cloud tem q estudar o Appendix B do Headfirst
print('We start off in:', __name__)
if __name__ == '__main__':
    # teve q por o host para funcionar dentro de container
    #app.run(host='0.0.0.0', debug=True)
    print('And end up in:', __name__)
    app.run(debug=True) #deixar debug so para testes, para PROD desabilitar

# Here’s a quick and dirty explanation of the various HTTP status codes that can be sent
#from a web server (e.g., your Flask webapp) to a web client (e.g.,your web browser).
#There are five main categories of status code: 100s, 200s, 300s,400s, and 500s.

#Codes in the 100–199 range are informational messages: all is OK, and the server is providing
#details related to the client’s request.

#Codes in the 200–299 range are success messages: the server has received, understood, and
#processed the client’s request. All is good.

#Codes in the 300–399 range are redirection messages: the server is informing the client
#that the request can be handled elsewhere.

#Codes in the 400–499 range are client error messages: the server received a request from the client
#that it does not understand and can’t process. Typically, the client is at fault here.

#Codes in the 500–599 range are server error messages: the serverreceived a request from the client,
#but the server failed while trying to process it. Typically, the server is at fault here

#msg de erros mais comuns de HTML
#Códigos de Informação (início com 1): quer dizer que solicitação do cliente está sendo processada e ainda não foi concluída.
#Códigos de Sucesso (início com 2): aponta que a solicitação do cliente foi recebida e processada com sucesso pelo servidor
#Códigos de Redirecionamento (início com 3): indica que a solicitação do cliente precisa ser redirecionada para outro local para ser concluída
#Códigos de Erro do Cliente (início com 4): quer dizer que ocorreu um erro na solicitação do cliente, como uma página não encontrada (404 Not Found) ou uma permissão negada (403 Forbidden)
#Códigos de Erro do Servidor (início com 5): significa que ocorreu um erro no servidor ao processar a solicitação do cliente, como uma falha interna no servidor (500 Internal Server Error) ou um tempo de espera excedido (504 Gateway Timeout)
