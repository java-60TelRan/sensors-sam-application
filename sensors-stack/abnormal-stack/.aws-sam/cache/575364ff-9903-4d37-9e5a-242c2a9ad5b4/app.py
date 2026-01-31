from logger import logger
import json
from publisher import publish
import os
SENSOR_IDS = ["123", "124", "125", "126"]
SENSORS_NORMAL_VALUES = {
SENSOR_IDS[0]: (30, 60),
SENSOR_IDS[1]: (10, 80),
SENSOR_IDS[2]: (20, 30),
SENSOR_IDS[3]: (60, 120)
}
envLow =  "LOW_VALUES_TOPIC_ARN" #env variable with topic for low values
envHigh= "HIGH_VALUES_TOPIC_ARN"#env variable with topic for low values

def processRecord(record: dict):
    message = record["Sns"]["Message"]
    logger.debug(f"message from SNS record is {message}")
    messageDict: dict = json.loads(message)
    topicArn, limit = getPublishingTopicAndLimit(messageDict)
    if topicArn:
        logger.debug(f"topic to publish is {topicArn}")
        logger.debug(f"message for publishing is {messageDict}")
        messageDict["limit"] = limit
        resp = publish(messageDict, topicArn)
        logger.debug(f"response from publishing is {resp}")
    
def getPublishingTopicAndLimit(messageDict: dict) -> tuple[str | None, int | None]:
    sensorId, value = messageDict["sensorId"], messageDict["value"]
    min = SENSORS_NORMAL_VALUES[sensorId][0]
    max = SENSORS_NORMAL_VALUES[sensorId][1]
    logger.debug(f"sensorId is {sensorId} ; value={value} ; min_value={min}; max_value={max}")
    topicArn = ""
    limit = None
    if not (min <= value <= max):
        if value < min:
            topicArn, limit = os.getenv(envLow), min
        else:
            topicArn, limit = os.getenv(envHigh), max
    return topicArn, limit    
    
         
def lambda_handler(event, __):
    try:
        for record in event["Records"]:     
            processRecord(record)
    except Exception as e:
        logger.error(f"ERROR: {str(e)}") 
        raise e         
            