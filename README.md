# Jornada Digital CAIXA| Devops | #1148

## Projeto do Modulo 2: *Conteinerização*

- Autor: Romulo Alves | c153824

### Descrição

A Solução proposta utiliza o docker-compose para subir os serviços na ordem esperada.

Os containers foram separados por serviços (Minio, RabbitMQ e Redis) e aplicação em python (criaamb, producer e consumer)

As rotinas dos scripts estão descritas a seguir:

1. 'criaamb.py': configura o ambiente de serviços
2. 'producer.py': inicia o producer que gera requests aleatórios a partir da API do [Mockaroo](https://mockaroo.com/)
3. 'consumer.py': cria o consumidor de eventos, verifica se pode ser considerado fraudulento, gera o relatorio para os que foram considerados e disponibiliza pelo Minio para download

Os critérios para a flag de antifraude foram configuradas nesta ordem:

1. Verifica se o cookie está vencido
2. Compara sessões entre países diferentes e timestamp menor que 2 horas 
3. Verifica se o tempo de resposta é maior que 5 segundos

Informações importantes:

- O producer faz uma consulta a API do Mockaroo a cada 30 segundos
- Devido a limitação de consultas a uma API gratuita no Mockaroo (200 requests por dia), criei 3 contas com o mesmo schema apresentado abaixo e está sendo aplicado um balanceamento de carga randômico até que o limite de todas as APIs sejam atingidas.


### Schema Utilizado para os requests

![mockaroo-schema](images/mockaroo-schema.png?raw=true "mockaroo-schema")

### Pré-requisitos

- docker
- docker compose
- git

## Instruções

1. Clonar o repositório

```
git clone https://github.com/romulow22/adadevopsmod2.git
```

2. Executar o ambiente 

```
cd adadevopsmod2
sudo docker compose -f docker-compose.yml up -d --build
```  

3. Verificar os logs pelos containeres 
```
sudo docker logs --follow criaambapp
sudo docker logs --follow producerapp
sudo docker logs --follow consumerapp
```  

4. Remover o laboratório.  
```
sudo docker compose -f docker-compose.yml down
sudo docker rmi $(sudo docker images --format '{{.Repository}}:{{.Tag}}'| grep adadevopsmod2)
sudo docker rmi minio/mc:RELEASE.2024-03-07T00-31-49Z minio/minio:RELEASE.2024-03-07T00-43-48Z redis/redis-stack:7.2.0-v8 rabbitmq:3-management 
``` 