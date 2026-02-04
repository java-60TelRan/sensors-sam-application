# HW 56 Definition

## Update code for abnormal-sensor-values lambda function

### See FIXME comments in app.py for abnormal-sensor-values lambda function

Optional (bonus) - introduce STALE_TIME env variable defining period in seconds to invoke data provider lambda function even if SENSORS_NORMAL_VALUES has data about a sensor. Consider tuple (min, max, timestamp) where timestamp when the tuple was inserted

## Write new Lambda function sensor-data-provider inside abnormal-stack folder

Direct invoked with event (dictionary) containing {"sensorId":< sensorId >}<br>
The same dict that was in old version of abnormal-sensor-values (It's only stub / prototype, final solution implies using SQL AWS RDS)

## Update template file

add resource for creating sensor-data-provider lambda function<br>
add permissions for invocation in the role for abnormal-sensor-values

## Notes

### abnormal-sensor-values

lambda_client = boto3.client('lambda')<br>
#invocation<br>
response = lambda_client.invoke( <br>
FunctionName='sensor-data-provider',<br>
InvocationType='RequestResponse',<br>
Payload=json.dumps({"sensorId": < sensorId value >})<br>
)<br>
#response parsing implied min / max values for requested sensor<br>
invoked_response = json.loads(response['Payload'].read())
### sensor-data-provider
handler getting regular dictionary according to a Payload in invocation<br>
def lambda_handler(event, context): event["sensorId"] - sensorId value
