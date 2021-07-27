# FPL_IR_Metadata_QC
 A series of scripts and AWS processes to ensure that infrared imagery has appropriate GPS metadata. The results are recorded in AirTable. 
 
 AWS Configurations:
 fpl_ir_metadata_qc.py - Lambda function:
    S3 trigger - Event type: ObjectCreatedByPut
                 Prefix: "hardening/"
                 Suffix: ".JPG"
 
 fpl_ir_metadata_qc_airtable.py - Lambda function:
    SQS trigger - Batch size: 1

Workflow:
Pilot uploads RGB and IR imagery folders to S3. As soon as the image has uploaded, a Lambda function ("fpl_ir_metadata_qc.py") is triggered that checks whether the image has been uploaded to the RGB folder or the IR folder. If the image is in the RGB folder, the Lambda function exits. The average runtime for this check is about 1.5 seconds, so checking each image the pilot uploads shouldn't cost that much. If the image is in the IR folder, the Lambda function continues to check for the following GPS metadata attributes: latitude, latitude reference, longitude, longitude reference, relative altitude, and heading. If any of these fields are missing, the S3 path to the image, as well as a list of all GPS attributes that are present and missing, are sent to an SQS queue. As soon as a message is sent to the SQS queue, another Lambda function ("fpl_ir_metadata_qc_airtable.py") is triggered. This Lamabda function will read the message from the SQS queue and write the results of the first Lambda function to an AirTable view. After the results have been written to the table, the SQS message is deleted. With the results written to AirTable, we could either check this table daily to see which images need recollect, or have it set up to send updates to a Slack channel where management can be updated. 
