import time
from logger import logger
import json
from publisher import publish
import os
import boto3

cache: dict[str, list[int]] = {

}
envLow =  "LOW_VALUES_TOPIC_ARN" #env variable with topic for low values
envHigh= "HIGH_VALUES_TOPIC_ARN"#env variable with topic for low values
envStaleTime = "STALE_TIME"
functionName = os.getenv("INVOKED_FUNCTION_NAME", "sensor-data-provider" )
lambda_client = boto3.client('lambda')
def getStaleTime():
    staleTime = int(os.getenv(envStaleTime, '10000000000000000'))
    return staleTime
def processRecord(record: dict, staleTime: int):
    message = record["Sns"]["Message"]
    logger.debug(f"message from SNS record is {message}")
    messageDict: dict = json.loads(message)
    topicArn, limit = getPublishingTopicAndLimit(messageDict, staleTime)
    if topicArn:
        logger.debug(f"topic to publish is {topicArn}")
        logger.debug(f"message for publishing is {messageDict}")
        messageDict["limit"] = limit
        resp = publish(messageDict, topicArn)
        logger.debug(f"response from publishing is {resp}")
def shouldInvoke(sensorId: str, staleTime)->bool:
    values = cache.get(sensorId)
    staled = False
    if not values:
        logger.debug(f"cache should be populated due to missing values for {sensorId} sensor")
    elif time.time() - values[2] > staleTime:
       staled = True
       logger.debug(f"for sensor {sensorId} cache staled as time greater than {staleTime} seconds")    
    return not values  or  staled
def populateCache(sensorId: str) :
    logger.debug(f"{functionName} to be invoked")
    response = lambda_client.invoke(
        FunctionName=functionName,
        InvocationType="RequestResponse",
        Payload = json.dumps({"sensorId": sensorId})
    )
    invoked_response = json.loads(response['Payload'].read())
    logger.debug(f"response from {functionName} lambda function is {invoked_response}")
    code = invoked_response["code"]
    if code != 200:
        errorMessage = invoked_response["message"]
        logger.error(f"response code: {code}, message: {errorMessage}")
        raise Exception(errorMessage)
    values = invoked_response["values"]
    values.append(time.time())
    cache[sensorId] = values
    logger.debug(f"for sensor {sensorId} populated {cache[sensorId]}")

def getPublishingTopicAndLimit(messageDict: dict, staleTime: int) -> tuple[str | None, int | None]:
    sensorId, value = messageDict["sensorId"], messageDict["value"]
    if shouldInvoke(sensorId, staleTime):
        populateCache(sensorId)
    min = cache[sensorId][0]
    max = cache[sensorId][1]
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
        staleTime = getStaleTime()
        logger.debug(f"cache stale time is {staleTime}")
        logger.debug(f"cache is the dictionary {cache}")
        for record in event["Records"]:     
            processRecord(record, staleTime)
    except Exception as e:
        logger.error(f"ERROR: {str(e)}") 
        raise e         
            