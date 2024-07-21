# Projeto ETL com Dagster e Fast API

Este projeto implementa uma Rest API utilizando Fast API e um pipeline de ETL (Extract, Transform, Load) utilizando o Dagster para orquestração.

O pipeline extrai dados de um banco de dados PostgreSQL fonte, realiza transformações e carrega os dados processados em um banco de dados alvo, também PostgreSQL.
Também foi criado um script individual, que pode ser executado de forma independente ao Dagster.

A aplicação utiliza Docker para a criação e gerenciamento dos containeres, sendo eles:
  - API
  - DB1 (Fonte)
  - DB2 (Alvo)
  - Dagster

Assim que iniciada, a API **`recriará as duas bases de dados para uma execução limpa dos testes necessários`**, além de popular a base de dados Fonte com **`dados aleatórios`** com frequencia de **`1 minuto`** e intervalo de **`10 dias`**, tendo como base **`5 dias anteriores`** à data atual de execução.

Se a aplicaçao, por exemplo, for executada no dia **`20/07/2024`**, a **`data inicial`** dos dados gerados aleatoriamente será **`15/07/2024`** e a **`data limite`** será **`25/07/2024`**.

---

## Pré-requisitos

- Python 3.11+
- Docker

---

## Execução da API, Databases e Dagster

#### 1. Clone o projeto

Clone o projeto e navegue para o diretório principal do projeto com o comando: `cd .\fastapi_dagster_etl`

```bash
git clone https://github.com/huanfrancischinelli/fastapi_dagster_etl.git
```

#### 2. Execute o script Docker Compose

```bash
docker compose up --build
```


---

## Execução do Script ETL no Dagster

#### Endereço Dagster


Foram criados `2 Assets`, com um `1 Job especifico para cada Asset`, além de `um Resource para cada banco de dados`.

O Job **`etl_daily`** tem como objetivo a execução diaria por meio do Schedule **`etl_daily_schedule`**, tendo parametros fixos para que o Script ETL busque sempre todos os dados referente ao `dia anterior`, compilados com frequencia de `10 minutos` e valores de `média`, `mínima`, `máxima` e `desvio padrão` referente ao `periodo compilado`.
Os dados serão salvos no banco de dados alvo, na tabela Data.

Já o Job **`etl`** permite a customização da execução através dos parametros:
  - start_date: Data com formatação `YYYY-MM-DD`, que indica a data de inicio de busca na base de dados.
  - end_date: Data com formatação `YYYY-MM-DD`, que indica a data limite de busca na base de dados.
  - variables: Métricas a serem consideradas no processo de ETL. 

### Execução do Job **`etl`**
#### 1. Acesse o endereço Dagster
```
http://localhost:8000
```
#### 2. Navegue até **`Jobs`** e acesse o job **`etl`**
#### 3. Em **`Launchpad`** customize o arquivo de configuração
```yml
ops:
  etl_script:
    config:
      api_url: http://api:5000/source/data/read
      end_date: 2024-07-18
      start_date: 2024-07-17
      variables:
      - wind_speed
      - power
      - ambient_temperature
resources:
  db1:
    config:
      database_url: postgresql://admin:admin@db1/db1
  db2:
    config:
      database_url: postgresql://admin:admin@db2/db2
```
#### 4. Execute em **`Launch Run`**

### Schedule do Job **`etl_daily`**
#### 1. Acesse o endereço Dagster
```
http://localhost:8000
```
#### 2. Navegue até **`Schedules`** e acesse o schedule **`etl_daily_schedule`**
#### 3. Ative o Schedule na flag **`Running`**

---

## Execução do Script ETL pelo Console

É altamente recomendável criar um ambiente virtual `(venv)` para instalar as dependências necessárias. Isso ajuda a manter as dependências organizadas e evita conflitos com outras bibliotecas do sistema.

`Caso não deseje criar um ambiente virtual para a execução do script, os passos 2 e 3 podem ser ignorados.`

#### 1. No console, navegue até o diretório do script

```bash
cd .\etl\
```

#### **`Opcional`** 2. Crie o ambiente virtual Python `(venv)`

```bash
python -m venv venv
```

#### **`Opcional`** 3. Ative o ambiente virtual Python `(venv)`

- **Windows:**

    ```bash
    venv\Scripts\activate
    ```

- **macOS e Linux:**

    ```bash
    source venv/bin/activate
    ```

#### 4. Instale as dependencias

```bash
python -m pip install -r requirements.txt
```

#### 5. Modifique as configurações de execução dentro do Script **`etl_script.py`** conforme necessario.

#### 6. Execute o script.

```bash
python .\etl_script.py
```


---

## Rotas da API

### DB Fonte
#### 1. Ler dados tabela Data

```
http://localhost:5000/source/data/read
```
Retorna os dados presentes na tabela Data no DB Fonte, com base nos parametros de data e metricas necessarias, passadas no parametro `variables`.

Se nenhum parametro de data for informado, todos os dados serão retornados.

Parametros:
  - **`Opcional`** **start_date:** String em formato `YYYY-MM-DDThh:mm:ss` que indica a data de inicio de busca na base de dados.
  - **`Opcional`** **end_date:** String em formato `YYYY-MM-DDThh:mm:ss` que indica a data limite de busca na base de dados.
  - **`Opcional`** **variables:** Array de Strings que indicará quais variáveis (colunas de metrica presentes na tabela) o usuario deseja retornar, caso não seja especificado a requisição retornará todas as métricas.

Exemplo:
```
http://localhost:5000/source/data/read?start_date=2024-07-01T00:00:00&end_date=2024-07-31T23:59:59&variables=wind_speed&variables=power
```

#### 2. Gerar dados aleatórios tabela Data

```
http://localhost:5000/source/data/randomize
```
Gera dados aleatorios na tabela Data, com base nos parametros de data inicial, periodo e minutagem das amostras. 

Opcionalmente tambem é possivel informar a data inicial e a final, sem que seja necessário informar o periodo, mas obrigatoriamente um dos dois parametros deve ser enviado.

Parametros:
  - **start_date:** String em formato `YYYY-MM-DD` que indica a data de inicio para a criação dos dados.
  - **period:** Integer que indica o periodo de tempo em dias das amostras a serem geradas.
  - **minutes:** Integer que indica o intervalo de tempo em minutos entre as amostras a serem geradas.
  - **`Opcional`** **end_date:** String em formato `YYYY-MM-DD` que indica a data limite para a criação dos dados.

Exemplo:
```
localhost:5000/source/data/randomize?start_date=2024-07-15&period=10&minutes=1
```

#### 3. Excluir todos os dados tabela Data

```
http://localhost:5000/source/data/reset
```
Exclui todos os registros presentes na tabela Data. 


### DB Alvo
#### 1. Ler dados tabela Signal

```
http://localhost:5000/target/signal/read
```
Retorna os dados presentes na tabela Signal no DB Alvo.

#### 2. Ler dados tabela Data

```
http://localhost:5000/target/data/read
```
Retorna os dados presentes na tabela Data no DB Alvo.

#### 3. Excluir todos os dados tabela Signal

```
http://localhost:5000/target/signal/reset
```
Exclui todos os registros presentes na tabela Signal no DB Alvo.

#### 4. Excluir todos os dados tabela Data

```
http://localhost:5000/target/data/reset
```
Exclui todos os registros presentes na tabela Data no DB Alvo.

---

## Estrutura do Projeto

```bash
.
├── app
│   ├── db1
│   │   ├── models
│   │   │   └── data.py
│   │   ├── routes
│   │   │   └── source_data_routes.py
│   │   └── schemas
│   │       └── data.py
│   ├── db2
│   │   ├── models
│   │   │   ├── data.py
│   │   │   └── signal.py
│   │   ├── routes
│   │   │   ├── target_data_routes.py
│   │   │   └── target_signal_routes.py
│   │   └── schemas
│   │       ├── data.py
│   │       └── signal.py
│   ├── routes
│   │   └── main_routes.py
│   ├── __init__.py
│   ├── main.py
│   ├── db.py
│   ├── scripts.py
│   ├── Dockerfile.app
│   └── requirements.txt
├── dagster
│   ├── db1
│   │   └── models
│   │       └── data.py
│   ├── db2
│   │   └── models
│   │       ├── data.py
│   │       └── signal.py
│   ├── resources.py
│   ├── assets.py
│   ├── schedules.py
│   ├── jobs.py
│   ├── pipeline.py
│   ├── config.yaml
│   ├── Dockerfile.dag
│   └── requirements.txt
├── etl
│   ├── models
│   │   ├── data.py
│   │   └── signal.py
│   ├── __init__.py
│   ├── db.py
│   ├── etl_script.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```
