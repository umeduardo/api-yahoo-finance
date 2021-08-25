# API de Mercado Financeiro do Yahoo
Desenvolvimento de uma API para mercado financeiro utilizando um webcrawler para obter os dados diretamente do site do Yahoo Finance;


# Instalação

### Instale os pacotes necessários
```
1) $ python3.6 -m venv ./venv
2) $ source venv/bin/activate
3) $ pip install -r config/requirements.txt
```
### Defina as variáveis de ambiente e rode o projeto
```
4) $ export FLASK_ENV=development
5) $ export FLASK_APP=main
6) $ cd src && flask run
```

# Métodos
### Consulta por região
- http://127.0.0.1:5000/regions
- http://127.0.0.1:5000/stocks?region=Argentina

# Libraries

- Selenium
- Flask
- Flask Cache
- Typing
- MyPy
- PyTest
- BeautifulSoup