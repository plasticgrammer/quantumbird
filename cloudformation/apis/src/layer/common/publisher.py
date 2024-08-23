import boto3
from botocore.exceptions import ClientError
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

ses = boto3.client('ses', region_name='ap-southeast-2')  # SESを使用するリージョンを指定

def send_mail(sendFrom, to, subject, body):
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
        response = ses.send_raw_email(
            Source=sendFrom,
            Destinations=to,
            RawMessage={
                'Data':msg.as_string(),
            },
            #ConfigurationSetName=SEND_MAIL_CONFIG_SET
        )
        
        return response
        
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e

def get_from_address(organization):
    # メール差出人名 <差出人アドレス>
    return '%s <%s>'%(Header(organization['name'].encode('iso-2022-jp'),'iso-2022-jp').encode(), organization['sender'])

def check_verification_status(email_address):
    try:
        response = ses.get_identity_verification_attributes(
            Identities=[email_address]
        )
        status = response['VerificationAttributes'].get(email_address, {}).get('VerificationStatus', 'NotVerified')
        return status
    except ClientError as e:
        print(f'Error checking verification status: {e}')
        raise

def start_verification_process(email_address):
    try:
        ses.verify_email_identity(
            EmailAddress=email_address
        )
    except ClientError as e:
        print(f'Error starting verification process: {e}')
        raise

def start_custom_verification(email_address, template_name):
    try:
        response = ses.send_custom_verification_email(
            EmailAddress=email_address,
            TemplateName=template_name
        )
        print(f"Verification email sent to {email_address}. Message ID: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"Error sending verification email: {e}")
        return False
