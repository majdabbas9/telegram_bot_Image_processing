import boto3
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError


class DynamoDBDatabaseHandler:
    def __init__(self, session_table_name, objects_table_name):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        self.prediction_sessions_table = self.dynamodb.Table(session_table_name)
        self.detection_objects_table = self.dynamodb.Table(objects_table_name)

        self.init_db()

    def init_db(self):
        try:
            self.prediction_sessions_table.load()
            self.detection_objects_table.load()
        except ClientError as e:
            raise RuntimeError("One or more DynamoDB tables do not exist") from e


    def get_predicted_image(self, uid):
        response = self.prediction_sessions_table.get_item(Key={'uid': uid})
        item = response.get('Item')
        return item.get('predicted_image') if item else None