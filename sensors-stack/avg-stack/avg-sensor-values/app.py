import time
from logger import logger
import json
from publisher import publish
import os
envTopic = "AVG_VALUES_TOPIC_ARN"
envReduceSize = "REDUCING_SIZE"
sensorsHistory: dict[str, list[int]] = {}
def getAvgValue(sensorId: str, value: int, reduceSize: int) -> float:
    avgRes: float|None= 0
    sensorsHistory.setdefault(sensorId, []).append(value)
    values: list[int] = sensorsHistory[sensorId]
    size: int = len(values)
    if size >= reduceSize:
       avgRes =  sum(values) / size
    return avgRes

def  publishAvg(sensorId: str, topicArn: str, avg: float):
   resp = publish({"sensorId": sensorId, "value":avg, "timestamp": time.time()},topicArn)
   del sensorsHistory[sensorId]
   logger.debug(f"response from publishing is {resp}") 
      
def processRecord(record, topicArn: str, reduceSize: int):
    message = record["Sns"]["Message"]
    logger.debug(f"message from SNS record is {message}")
    messageDict: dict = json.loads(message)
    sensorId, value = messageDict["sensorId"], messageDict["value"]
    avg: float | None = getAvgValue(sensorId, value, reduceSize)
    if avg:
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
