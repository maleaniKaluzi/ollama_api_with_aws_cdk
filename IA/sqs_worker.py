import boto3
import base64
import json
import os
import logging
from utils.img_analyzing import describe_image
from utils.embedding_text import embed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue_url = os.environ.get("QUEUE_URL","http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/media-analysis-queue") 
result_queue_url = os.environ.get("QUEUE_URL_RESULT","http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/my-localstack-ia-result-queue") 

# Connexion à SQS LocalStack
sqs = boto3.client('sqs', endpoint_url="http://localhost:4566", region_name="us-east-1")

# Connexion à S3 LocalStack
s3 = boto3.client('s3', endpoint_url="http://localhost:4566", region_name="us-east-1")

def download_image_to_base64(bucket, key):
    """Télécharge l'image depuis S3 et retourne en base64"""
    resp = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = resp['Body'].read()

   
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    return encoded

print("Worker Ollama démarré, en attente de messages SQS...")

while True:
    resp = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    for msg in resp.get('Messages', []):
        data = json.loads(msg['Body'])
        bucket = data['bucket']
        key = data['key']

        print(f"Traitement fichier : s3:// {bucket}/{key}...")

        # Télécharge image et appelle Ollama
        image_base64 = download_image_to_base64(bucket, key)
        
        try:
            result = describe_image(image_base64, type_media='image')
            description_text = result["description"]["data"][0]['summary']
            title_text = result["description"]["data"][0]['title']
            tags_text = " ".join(result["description"]["data"][0]['tags'].upper())
            embedding = embed(title_text+description_text+tags_text)

            print(f"Résultat IA : {result}")

            # Après analyse IA
            sqs.send_message(
                QueueUrl=result_queue_url,  # mettre l'URL de la nouvelle queue
                MessageBody=json.dumps({
                    'bucket': bucket,
                    'key': key,
                    'result_ai': result,
                    'embedding':embedding
                })
            )


            # Supprimer message SQS
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
        except Exception as e:
            logger.error("Erreur IA, message conservé dans SQS", exc_info=True)
        
