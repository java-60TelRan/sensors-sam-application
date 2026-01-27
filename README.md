# HW 54 Definition
## Fill placeholder lambda functions with initial logic
### avg-sensor-values
#### based on sensor values received from SNS ingest topic to find average values 
1. Introduce environment variable REDUCING_SIZE defining number probs after which there should be average value computation and publishing into another SNS topic<br>
2. Dictionary: key - sensor id, value - list of the sensor values<br>
3. After reaching reducing size for a sensor<br>
3.1 Compute average value<br>
3.2 Publish dictionary containing sesnsor id, average value , timestamp into SNS average values topic<br>
3.3 Clear list of values
### abnormal-sensor-values
#### based on sensor values received from SNS ingest topic to find abnormal values
1. Introduce dictionary from https://github.com/java-60TelRan/sensor-values-imitator with ranges of normal values for the sensors<br>
2. In the case of received sensor value  less than minimal value to publish into the SNS topic for low values<br>
3. In the case of received sensor value greater than maximal value to publish into the SNS topic for high values
### high-values-processor
1. Prints sensor id , value and timestamp converted to regular date/time received from topic for high values
### low-values-processor
1. Prints sensor id , value and timestamp converted to regular date/time received from topic for low values

### avg-values-processor
1. Prints sensor id, avg value and timestamp converted to regular date/time received from topic for low values
## Component test
1. Start sensor values imitator publishing sensor values into ingest SNS topic<br>
2. See logs for all lambda functions (CloudWatch)<br>
3. See logs of high-values-processor - all the values should be greater than maximal values for appropriate sensors (CloudWatch)<br>
4. See logs of low-values-processor - all the values should be less than minimal values for appropriate sensors (CloudWatch)<br>


