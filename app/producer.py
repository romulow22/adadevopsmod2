import json
import pika
import requests
import random
import time

# Configuração do RabbitMQ
def connect_rabbitmq():
    
    # Getting Secrets
    with open('/run/secrets/rabbitmq_root_usr', 'r') as file:
        rabbitmq_root_usr = file.read().strip()
    with open('/run/secrets/rabbitmq_root_pwd', 'r') as file:
        rabbitmq_root_pwd = file.read().strip()
    
    credentials = pika.PlainCredentials(rabbitmq_root_usr, rabbitmq_root_pwd)
    
    connection_params = pika.ConnectionParameters(host='rabbitmq', port=5672, virtual_host='projetoada', credentials=credentials)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    return connection, channel

def publish_json_to_exchange(channel, exchange_name, routing_key, count):
    
    # Lista de URLs para obter os objetos JSON configurados no mockaroo
    urls = [
        "https://api.mockaroo.com/api/0eee3010?count={count}&key=31e736b0", #romuloww
        "https://api.mockaroo.com/api/6ffc21b0?count={count}&key=e3a906f0", #romuloass
        "https://api.mockaroo.com/api/5174df30?count={count}&key=2c689270"  #romuloa.silva
    ]
    messages_sent = 0
    url_errors = set()
    
    # Loop para enviar as mensagens até conseguir um retorno com sucesso ou tentar todas as URLs
    # devido ao limite de 200 requisições por dia do mockaroo por API
    while len(url_errors) < len(urls):
        
        random_index = random.randint(0, 2)
        url = urls[random_index]
      
        if url in url_errors:
            #Faz nova tentativa já que já está classificada com erro
            continue
        # Faz a requisição e trata os erros
        try:
            url_tratada = url.format(count=count)
            response = requests.get(url_tratada)
            response.raise_for_status()
            json_objects = response.json()
            # Envio das mensagens para o exchange
            for obj in json_objects:        
                message = json.dumps(obj)
                properties = pika.BasicProperties(content_type='application/json')
                channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message, properties=properties)
                messages_sent += 1
            print(f" [x] {messages_sent} Mensagem(s) Enviada(s)")
            return
        except requests.exceptions.RequestException:
            # Adiciona URL com erro a lista
            url_errors.add(url)
    print(f" Limite de requisições a API do Mockaroo atingido. Não foi possível gerar mais requests.")        

def main():
    
    print('Producer iniciado...')
    #Conexão RabbitMQ
    connection, channel = connect_rabbitmq()

    #Producer
    try:
        exchange_name = 'transaction_exchange'
        routing_key = 'transaction_routing_key'
        while True:
            count = random.randint(10, 20)  # Gera um número aleatório entre 10 e 20
            publish_json_to_exchange(channel, exchange_name, routing_key, count)
            time.sleep(60)  # Aguarda 60 segundos antes de publicar novamente
    except KeyboardInterrupt:
        print("Script interrompido pelo usuário")
    finally:
        channel.close()
        connection.close()    

if __name__ == "__main__":
    main()
