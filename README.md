# FPL_IR_Metadata_QC
 A series of scripts and AWS processes to ensure that infrared imagery has appropriate GPS metadata. The results are recorded in AirTable. 
 
 AWS Configurations:
 fpl_ir_metadata_qc.py - Lambda function:
    S3 trigger - Event type: ObjectCreatedByPut
                 Prefix: "hardening/"
                 Suffix: ".JPG"
 
 fpl_ir_metadata_qc_airtable.py - Lambda function:
    SQS trigger - Batch size: 1
