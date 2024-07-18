import boto3
from botocore.exceptions import ClientError
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_mail(sendFrom, to, subject, body, corporationId, userId):
    client = boto3.client('ses', 'ap-southeast-2')

    CHARSET = "utf-8"
    SEND_MAIL_CONFIG_SET = 'CanaryConfig'
    
    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = subject
    msg['From'] = sendFrom
    msg['To'] = ','.join(to)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(body.encode(CHARSET), 'plain', CHARSET)
    msg_body.attach(textpart)
    
    # Attach the multipart/alternative child container to the multipart/mixed
    msg.attach(msg_body)
    
    try:
        #Provide the contents of the email.
        response = client.send_raw_email(
            Source=sendFrom,
            Destinations=to,
            RawMessage={
                'Data':msg.as_string(),
            },
            ConfigurationSetName=SEND_MAIL_CONFIG_SET
        )
        
        return response
        
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e

def send_sns(senderId, phoneNumber, body, corporationId, userId):
    sns = boto3.client("sns")
    response = sns.publish(
        PhoneNumber="+81"+phoneNumber, 
        Message=body,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': senderId 
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'
            }
        }
    )
    
    return response

def get_from_address(corp):
    # メール差出人名 <差出人アドレス>
    return '%s <%s>'%(Header(corp['mail_from_name'].encode('iso-2022-jp'),'iso-2022-jp').encode(), corp['mail_address'])
