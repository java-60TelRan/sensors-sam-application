from logger import logger
import os
SENSORS_NORMAL_VALUES: dict = {
"123": (30, 60),
"124": (10, 80),
"125": (20, 30),
"126": (60, 120)
} 
LOG_MESSAGE_BASE =  'invoked sensor-data-provider with request for values range for'     
def lambda_handler(event: dict, __):
    sensorId = event.get('sensorId')
    resp = processSensorRequest(sensorId) if sensorId else response(400)
    logger.debug(f"to return: {resp}")  
    return resp 

def processSensorRequest(sensorId):
    logger.debug(f"{LOG_MESSAGE_BASE} {sensorId}")
    data = SENSORS_NORMAL_VALUES.get(sensorId)
    if not data:
        logger.error(f"no data for sensor {sensorId}")
        resp = response(404, sensorId)
    else:
        logger.debug(f"data to be returned is {data}")
        resp = response(200, sensorId, data)
    return resp         

def response(code: int,  sensorId: str = "", values: list[int] = [])->dict:
    resp: dict = {"code": code}
    if code == 404:
        resp["message"] = f"not found data about sensor {sensorId}"
    elif code == 400:
        resp["message"] = f"wrong invocation: missing sensorId key in event"
    else:
        resp["sensorId"] = sensorId
        resp["values"] = values
    return resp    
        
    
    
                