import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import urllib.parse
import boto3

s3 = boto3.client('s3')
s3r = boto3.resource('s3')
sqs_client = boto3.client('sqs')

def process_image(KEY):
    filename_split = KEY.split('/')
    my_file = filename_split[-1]
    local_file_name = '/tmp/' + my_file
    #s3.Bucket('rf-training-1').download_file(KEY, local_file_name)
    s3r.meta.client.download_file('rf-training-1', KEY, local_file_name)
    img_path = '/tmp/' + my_file
    lat = ''
    lon = ''
    lat_ref = ''
    lon_ref = ''
    yaw_degree = ''
    rel_alt = ''
    exif_table = {}
    fd = open(img_path, 'rb')
    d= fd.read()
    xmp_start = d.find(b'<x:xmpmeta')
    xmp_end = d.find(b'</x:xmpmeta')
    xmp_str = d[xmp_start:xmp_end+12]
    xmp_str = str(xmp_str)
    xmp_str = xmp_str.split('<drone-dji:')
    for line in xmp_str:
        if line.startswith('GimbalYawDegree'):
            yaw_degree = line
            yaw_degree = yaw_degree.replace('GimbalYawDegree>', '')
            yaw_degree = yaw_degree.replace('</drone-dji:', '')
        if line.startswith('RelativeAltitude'):
            rel_alt = line
            rel_alt = rel_alt.replace('RelativeAltitude>', '')
            rel_alt = rel_alt.replace('</drone-dji:', '')
                    
    exif_table = {}
    image = Image.open(img_path)
    info = image.getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exif_table[decoded] = value
    gps_info = {}
    for key in exif_table['GPSInfo'].keys():
        decode = GPSTAGS.get(key,key)
        gps_info[decode] = exif_table['GPSInfo'][key]
    for key in gps_info:
        lat_ref = gps_info.get("GPSLatitudeRef")
        lat = gps_info.get("GPSLatitude")
        lon_ref = gps_info.get("GPSLongitudeRef")
        lon = gps_info.get("GPSLongitude")
        
    if lon is None or lat is None or lon_ref is None or lat_ref is None or rel_alt is None or yaw_degree is None:
        if lon is None:
            lon = str('MISSING LON')
        if lat is None:
            lat = str('MISSING LAT')
        if lon_ref is None:
            lon_ref = str('MISSING LON REF')
        if lat_ref is None:
            lat_ref = str('MISSING LAT REF')
        if rel_alt is None:
            rel_alt = str('MISSING ALT')
        if yaw_degree is None:
            yaw_degree = str('MISSING HEAD')
            
            
        sqs_response = sqs_client.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/637137674144/fpl_ir_metadata_qc',
            MessageBody=json.dumps({'object': KEY, 'lon': lon, 'lat': lat, 'lon_ref': lon_ref, 'lat_ref': lat_ref, 'alt': rel_alt, 'head': yaw_degree}))
    else:
        pass

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    KEY = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    split_key = KEY.split('/')
    if str("02_IR") in split_key:
        my_message = str('Good to go!')
        process_image(KEY)
    else:
        my_message = str('wrong folder buddy')
        
    
    return {
        'statusCode': 200,
        'body': my_message
    }
