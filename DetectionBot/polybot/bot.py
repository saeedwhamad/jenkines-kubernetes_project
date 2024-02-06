import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import uuid
import boto3
import json


class Bot:

    def __init__(self, token, telegram_chat_url):
        logger.info(f'bot start s tokens= {token}')
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        certificate_path="projectALBpublic.pem"
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', certificate=open(certificate_path, 'r'), timeout = 60)


        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        logger.info("photo downlaod starts !! ")
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)


            photo_name=str(uuid.uuid4()) + ".jpg"





            # TODO upload the photo to S3


            try:
                # Upload the file to S3
                s3 = boto3.client('s3', 'us-west-2')
                s3.upload_file(photo_path, "saeedphotobucket", photo_name)
                logger.info("Photo is uploaded successfully!")
            except FileNotFoundError:
                logger.error(f"The file '{photo_path}' was not found.")
            except Exception as e:
                logger.error(f"An error occurred during S3 upload: {str(e)}")

            # TODO send a job to the SQS queue
            # Initialize SQS client without specifying region
            logger.info("sending to sqs starts !! ")
            sqs = boto3.client('sqs','us-west-2')

            # Define your SQS queue URL
            queue_url = 'https://sqs.us-west-2.amazonaws.com/933060838752/saeed_aws-project_SQS'

            chat_id = msg['chat']['id']
            logger.info(f'the chat id is : {chat_id}')

            # Define your job data
            job_data = {

                'chat_id': chat_id,
                'img_name': photo_name

            }


            # Send job data to SQS
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(job_data)
            )

            # Check the response
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("Job sent successfully to SQS.")
                logger.info("sqs is been sent")
            else:
                print("Failed to send job to SQS.")
                logger.info("sqs failed ")

            # TODO send message to the Telegram end-user (e.g. Your image is being processed. Please wait...)
            Bot.send_text(self, msg['chat']['id'], "We recived Your image, we are working on it, just a second  🕵️🕵️🕵️")
