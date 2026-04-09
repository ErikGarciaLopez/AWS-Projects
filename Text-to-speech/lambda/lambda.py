import boto3
import os
import urllib.parse

s3      = boto3.client('s3')
polly   = boto3.client('polly')
sns     = boto3.client('sns')

OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')

def lambda_handler(event, context):
    # Obtener el archivo subido
    record       = event['Records'][0]
    input_bucket = record['s3']['bucket']['name']
    key          = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Leer el texto
    response     = s3.get_object(Bucket=input_bucket, Key=key)
    texto        = response['Body'].read().decode('utf-8')

    # Sintetizar con Polly
    polly_resp   = polly.synthesize_speech(
        Text=texto,
        OutputFormat='mp3',
        VoiceId='Conchita'        # voz en español
    )

    # Guardar el audio en S3
    audio_key    = key.replace('.txt', '.mp3')
    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=audio_key,
        Body=polly_resp['AudioStream'].read(),
        ContentType='audio/mpeg'
    )

    # Notificar por email
    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='Tu audio está listo',
            Message=f'El archivo {audio_key} ya está disponible en S3.'
        )

    return {'statusCode': 200, 'body': 'OK'}