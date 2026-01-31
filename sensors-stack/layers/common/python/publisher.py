import boto3
import json

sns = boto3.client("sns")
def publish(message:dict, topicArn: str): 
    dataJson = json.dumps(message)
    response = sns.publish( TopicArn=topicArn,
    Message=dataJson)
    return response