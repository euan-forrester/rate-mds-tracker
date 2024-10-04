import boto3
from botocore.exceptions import ClientError
import logging

class EmailHelper:

  '''
  Wraps the functionality of sending an email using SES
  '''

  def __init__(self, region):
    self.ses = boto3.client('ses', region_name=region)
   
  def send_email(self, from_email_address, to_email_address, cc_email_address, subject_line, body_text):
    # Object structure described at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses/client/send_email.html#
    send_args = {
      'Source': from_email_address,
      'Destination': {
        'ToAddresses': [to_email_address],
      },
      'Message': {
        'Subject': {'Data': subject_line},
        'Body': {'Text': {'Data': body_text}}
      }
    }
    
    if cc_email_address is not None:
      send_args['Destination']['CcAddresses'] = [cc_email_address]

    try:
      response = self.ses.send_email(**send_args)
      message_id = response['MessageId']
      logging.info(f"Successfully sent mail '{message_id}' from '{from_email_address}' to '{to_email_address}'")
    except ClientError:
      logging.exception(f"Could not send mail from '{from_email_address}' to '{to_email_address}'")
      raise
