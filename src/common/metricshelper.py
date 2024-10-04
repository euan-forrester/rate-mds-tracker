import boto3
from botocore.config import Config

class MetricsHelper:

    '''
    Wraps the functionality of sending metrics to CloudWatch
    '''

    def __init__(self, environment, region, metrics_namespace):
        self.environment        = environment
        self.metrics_namespace  = metrics_namespace
        self.cloudwatch         = boto3.client('cloudwatch', region_name=region)
   
    def send_time(self, metric_name, time_in_seconds):
        self._send_metric(metric_name, time_in_seconds, "Seconds")

    def send_count(self, metric_name, count):
        self._send_metric(metric_name, count, "Count")

    def increment_count(self, metric_name, inc_amount=1):
        self._send_metric(metric_name, inc_amount, "Count")

    def _send_metric(self, metric_name, value, units):

        response = self.cloudwatch.put_metric_data(
            MetricData = [
                {
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': self.environment
                        },
                    ],
                    'Unit': units,
                    'Value': value
                },
            ],
            Namespace = self.metrics_namespace
        )
