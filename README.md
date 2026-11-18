# Projeto BD

## Para rodar local
1. Clone o repositório
2. No diretório do projeto: 

```sh
python3 -m venv venv
source ./venv/bin/activate
```
3. Verifique se apareceu (venv) na linha de comando, se sim:
```sh
python3 -m pip install -r ./backend/requirements.txt
python3 ./backend/main.py
```
4. Entre no seu localhost:8000 no browser e pronto. 

(quando quiser sair do venv usa `deactivate` e pra entrar dnv `source ./app/bin/activate`)

## Para conectar com o BD

1. No PgAdmin, se ainda não criou o server: 
> Crie um server novo com o nome ProjetoBD e hostname localhost (usuario: postgres e senha definida quando instalou)
2. Clica com o direito no server e criar Database, coloque o nome de ProjetoBD tbm.
3. Clica com o direito no novo database criado e CREATE Script.
4. Copia tudo do script que ta nesse repositório e da execute script (F5).
