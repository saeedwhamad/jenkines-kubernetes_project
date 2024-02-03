import time
from pathlib import Path
from detect import run
import yaml
from loguru import logger
import os
import boto3
import json
import requests
from botocore.exceptions import ClientError
import flask


logger.info("fuck u ! ")

app = flask.Flask(__name__)




images_bucket = os.environ['BUCKET_NAME']
queue_name = os.environ['SQS_QUEUE_NAME']

sqs_client = boto3.client('sqs', region_name='us-west-2')
logger.info("yolo bot starts !!")

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']


def consume():
    logger.info("consume methode starts !! ")
    while True:
        response = sqs_client.receive_message(QueueUrl=queue_name, MaxNumberOfMessages=1, WaitTimeSeconds=5)
        #logger.info(f'response = {response}')

        if 'Messages' in response:
            logger.info("there is a message ")
            message = response['Messages'][0]['Body']
            receipt_handle = response['Messages'][0]['ReceiptHandle']

            logger.info(f"there is a message {message}")

            # Use the ReceiptHandle as a prediction UUID
            prediction_id = response['Messages'][0]['MessageId']

            logger.info(f'prediction: {prediction_id}. start processing')
            logger.info({message})

            # Receives a URL parameter representing the image to download from S3
            message_data = json.loads(message)
            img_name = message_data.get("img_name") # TODO extract from `message`
            chat_id = message_data.get("chat_id")# TODO extract from `message`

            original_img_path = f'{prediction_id}_{img_name}.png'  # TODO download img_name from S3, store the local image path in original_img_path
            # Download image from S3 bucket
            try:
                s3 = boto3.client('s3')
                s3.download_file(images_bucket, img_name, original_img_path)
                logger.info(f'prediction: {prediction_id}/{original_img_path}. Download img completed')

            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logger.error(f'The object {img_name} does not exist in the bucket {images_bucket}.')
                else:
                    logger.error(f'Error downloading image {img_name}: {e}')
                return False


           # Predicts the objects in the image
            run(
                weights='yolov5s.pt',
                data='data/coco128.yaml',
                source=original_img_path,
                project='static/data',
                name=prediction_id,
                save_txt=True
            )

            logger.info(f'prediction: {prediction_id}/{original_img_path}. done')

            # This is the path for the predicted image with labels
            # The predicted image typically includes bounding boxes drawn around the detected objects, along with class labels and possibly confidence scores.
            predicted_img_path = Path(f'static/data/{prediction_id}/{original_img_path}')

            # TODO Uploads the predicted image (predicted_img_path) to S3 (be careful not to override the original image).
            s3.upload_file(predicted_img_path,images_bucket, f'imagesafterprediction/{img_name}_predicted')
            logger.info(f'Prediction ID: {prediction_id}. Predicted image uploaded to S3.')
            try:
            # Parse prediction labels and create a summary
                pred_summary_path = Path(f'static/data/{prediction_id}/labels/{prediction_id}_{img_name}.txt')
                logger.info(f"the path is {pred_summary_path}")
                if pred_summary_path.exists():
                    logger.info("prediction summary exists !! ")
                    with open(pred_summary_path) as f:
                        labels = f.read().splitlines()
                        labels = [line.split(' ') for line in labels]
                        labels = [{
                            'class': names[int(l[0])],
                            'cx': float(l[1]),
                            'cy': float(l[2]),
                            'width': float(l[3]),
                            'height': float(l[4]),
                        } for l in labels]

                    logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

                    prediction_summary = {
                        'prediction_id': prediction_id,
                        'original_img_path': str(original_img_path),
                        'predicted_img_path': str(predicted_img_path),
                        'labels': labels,
                        'time': time.time()
                    }

                    # TODO store the prediction_summary in a DynamoDB table

                    def store_prediction_summary(prediction_id, prediction_summary):
                        logger.info("store_prediction_summary starts ")
                        # Initialize DynamoDB client using the default session and IAM role
                        dynamodb = boto3.resource('dynamodb','us-west-2')
                        table_name = 'saeed_aws_project_table'
                        table = dynamodb.Table(table_name)
                        Item = {
                            'prediction_id': str(prediction_id),
                            'prediction_summary': {'S': str(prediction_summary)}
                        }
                        response = table.put_item(Item=Item)
                        logger.info(f'the response state is " {response}')


                    store_prediction_summary(prediction_id, prediction_summary)

                    # TODO perform a GET request to Polybot to `/results` endpoint
                    logger.info("sending get to results !! ")
                    url=f"http://saeedAwsLoadBalancer-1054870717.us-west-2.elb.amazonaws.com:80/results?chat_id={chat_id}&prediction_id={prediction_id}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        logger.info("get request was sucssfull")
                    else:
                        logger.info("get request failed !! ")




            except FileNotFoundError as e:
                logger.error(f'File not found error: {e}')
                # Handle the error, perhaps log a message or take appropriate action

            except Exception as e:
                logger.error(f'Error occurred while processing the file: {e}')
            # Delete the message from the queue as the job is considered as DONE
            sqs_client.delete_message(QueueUrl=queue_name, ReceiptHandle=receipt_handle)





@app.route('/is_alive', methods=['GET'])
def index():
    return 'Ok',200
@app.route('/is_ready', methods=['GET'])
def readiness():
    return 'OK',200


if __name__ == "__main__":
    consume()
    app.run(host='0.0.0.0', port=8008)

