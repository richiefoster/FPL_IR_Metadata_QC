import json
import boto3
import airtable
from datetime import datetime

client = boto3.client('sqs')

def lambda_handler(event, context):
    now = datetime.now()
    process_datetime = now.strftime('%m-%d-%Y %H:%M:%S')
    process_datetime = process_datetime

    receipt = event['Records'][0]['receiptHandle']
    my_json = event['Records'][0]['body']

    our_json = json.loads(my_json)
    img_name = our_json['object']
    img_name = img_name.split('/')
    img_name = img_name[-1]
    
    circ_name = our_json['object']
    circ_name = circ_name.split('/')
    circ_name = str(circ_name[3])
    
    my_at = airtable.Airtable('appAFFDwSZiGNyeRz' , 'GPS Tracking', 'keyJ0aOnGykSWNh9b')
    my_at.insert({'Image Name': img_name, 'S3 Path': our_json['object'], 'Lat Error': our_json['lat'], 'Lat Ref Error': our_json['lat_ref'], 'Lon Error': our_json['lon'], 'Lon Ref Error': our_json['lon_ref'], 'Alt Error': our_json['alt'], 'Head Error': our_json['head'], 'Date Processed': process_datetime, 'Circuit Name': circ_name})
    
    del_response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/637137674144/fpl_ir_metadata_qc',
        ReceiptHandle=receipt
    )

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
