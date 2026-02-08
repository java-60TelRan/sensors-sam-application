import time
from logger import logger
import json
from publisher import publish
import os
import boto3
envTopic = "AVG_VALUES_TOPIC_ARN"
envReduceSize = "REDUCING_SIZE"
envTableName = "TABLE_NAME"
dynamodb = boto3.resource(
    "dynamodb"
)
table = dynamodb.Table(os.getenv(envTableName, "sensors-aggregation"))


def getAvgValue(sensorId: str, value: int, reduceSize: int) -> float:
    avgRes: float | None = None
    response = table.get_item(
        Key={
            "sensorId": sensorId
        }
    )
    item = response.get("Item")
    if item:
        sum = item["sum"] + value
        count = item["count"] + 1
        if count >= reduceSize:
            avgRes = sum / count
            table.delete_item(
                Key={"sensorId":sensorId}
            )
        else:
            table.update_item(
                Key={
                    "sensorId": sensorId
                },
                UpdateExpression="SET #s = :new_sum, #c = :new_count",
                ExpressionAttributeNames={"#s": "sum", "#c": "count"},
                ExpressionAttributeValues={
                    ":new_sum": sum, ":new_count": count}
            )
    else:
        table.put_item(
            Item={
                "sensorId":sensorId,
                "sum": value,
                "count": 1
            }
        )    
    
    return avgRes


def publishAvg(sensorId: str, topicArn: str, avg: float):
    avg_value = float(avg)
    resp = publish({"sensorId": sensorId, "value": avg_value,
                   "timestamp": time.time()}, topicArn)
    logger.debug(f"response from publishing is {resp}")


def processRecord(record, topicArn: str, reduceSize: int):
    message = record["Sns"]["Message"]
    logger.debug(f"message from SNS record is {message}")
    messageDict: dict = json.loads(message)
    sensorId, value = messageDict["sensorId"], messageDict["value"]
    avg: float | None = getAvgValue(sensorId, value, reduceSize)
    if avg is not None:
        logger.debug(f"Sensor {sensorId}, avg={avg}")
        publishAvg(sensorId, topicArn, avg)


def lambda_handler(event, context, sns_client=None):
    try:
        topicArn = os.getenv(envTopic)
        if not topicArn:
            raise Exception("missing env. variable for topic arn")
        logger.debug(f"topicARN is {topicArn}")
        reduceSize = int(os.getenv(envReduceSize, 5))
        logger.debug(f"reducing size is {reduceSize}")
        for record in event["Records"]:
            processRecord(record, topicArn, reduceSize)
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        raise e
