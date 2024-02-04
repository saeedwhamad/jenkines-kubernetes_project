import flask
from flask import request
import os
from bot import ObjectDetectionBot
import json
from loguru import logger
import boto3


app = flask.Flask(__name__)

logger.info("bot app starts running !!")


# TODO load TELEGRAM_TOKEN value from Secret Manager

def get_secret(secret_name):
    logger.info("get secret starts !! ")
    # Initialize a Secrets Manager client using the default session and IAM role
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name='us-west-2')

    try:
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)

        # Parse and return the secret JSON data
        secret_data = json.loads(response['SecretString'])
        return secret_data
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None


telegram_secret_name = 'saeedTelegramCredentials'

# Retrieve the Telegram token from Secrets Manager
telegram_secret = get_secret(telegram_secret_name)
logger.info(f"telegram_secret = {telegram_secret}")

TELEGRAM_TOKEN = telegram_secret.get('TELEGRAM_TOKEN')
logger.info(f"TELEGRAM_TOKEN = {TELEGRAM_TOKEN}")


TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']
logger.info(f'TELEGRAM_APP_URL = {TELEGRAM_APP_URL}')


@app.route('/is_alive', methods=['GET'])
def index():
    return 'Ok',200

@app.route('/is_ready', methods=['GET'])
def readiness():
    return 'OK', 200


@app.route(f'/saeedbot/', methods=['POST'])
def webhook():
    logger.info(f"the request has  arrived to webhok  !!")

    req = request.get_json()
    themsg = req['message']
    logger.info(f'the msg is {themsg}')
    bot.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results/', methods=['GET'])
def results():
    logger.info("results endpoint running !! ")
    prediction_id = request.args.get('prediction_id')


    # TODO use the prediction_id to retrieve results from DynamoDB and send to the end-user
    def retrieve_results(prediction_id):
        logger.info(" retrive results starts !! ")
        # Initialize DynamoDB client using the default session and IAM role
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

        table_name = 'saeed_aws_project_table'

        table = dynamodb.Table(table_name)

        key = {
            'prediction_id': str(prediction_id)
        }

        # Retrieve the item from DynamoDB using its primary key
        response = table.get_item(Key=key)
        logger.info(response)
        return response


    def get_detected_objects(provided_data):
        data = f"'''{provided_data}'''"
        # Extracting 'labels' information using string manipulation
        labels_start = data.find("'labels': ")
        labels_end = data.find("]", labels_start)

        if labels_start != -1 and labels_end != -1:
            labels_str = data[labels_start + len("'labels': "): labels_end + 1]

            # Adjusting quotes for proper JSON format
            labels_str = labels_str.replace("'", '"')

            # Attempting to extract labels as JSON
            try:
                labels_data = json.loads(labels_str)

                # Count occurrences of each class
                class_counts = {}
                for label in labels_data:
                    label_class = label.get('class', '')
                    if label_class in class_counts:
                        class_counts[label_class] += 1
                    else:
                        class_counts[label_class] = 1

                # Create a formatted string of detected objects and their counts on new lines
                detected_objects = "\n".join([f"{k.capitalize()} {v}" for k, v in class_counts.items()])
                return f"Detected objects:\n{detected_objects}"

            except json.JSONDecodeError as e:
                return f"Error parsing JSON for labels: {e}"
        else:
            return "Labels not found in the data."



    chat_id = request.args.get('chat_id')
    textToSend = "faild to detect objects "
    text_results = retrieve_results(prediction_id)
    textToSend=get_detected_objects(text_results)


    bot.send_text(chat_id, textToSend)
    return 'Ok'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
    app.run(host='0.0.0.0', port=8443)















