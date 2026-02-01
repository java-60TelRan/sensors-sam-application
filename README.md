# HW 55 Definition
## Update code for avg-sensor-values lambda function
### Instead of dictionary (stateful function) introduce DynamoDB (stateless function)
consider table with PK as "sensorId", no SK, sum-value, count<br>
consider methods get_item, put_item, update_item, delete_item
## Update template file 
add resource for creating Dynamodb table intended for finding average values

