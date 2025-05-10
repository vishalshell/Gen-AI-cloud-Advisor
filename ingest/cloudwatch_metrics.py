"""Pull average CPU & Memory utilisation for demo purposes."""

import os
import datetime
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

v_client = boto3.client('cloudwatch', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))

def get_metric(v_ns, v_metric, v_dim_name, v_dim_val, v_start, v_end):
    return v_client.get_metric_statistics(
        Namespace=v_ns,
        MetricName=v_metric,
        Dimensions=[{'Name': v_dim_name, 'Value': v_dim_val}],
        StartTime=v_start,
        EndTime=v_end,
        Period=86400,
        Statistics=['Average']
    )

def main():
    v_instance_id = os.getenv('DEMO_INSTANCE_ID', 'i-1234567890abcdef0')
    v_end = datetime.datetime.utcnow()
    v_start = v_end - datetime.timedelta(days=7)

    v_cpu = get_metric('AWS/EC2', 'CPUUtilization', 'InstanceId', v_instance_id, v_start, v_end)
    v_rows = []
    for obj_pt in v_cpu['Datapoints']:
        v_rows.append({'timestamp': obj_pt['Timestamp'], 'cpu_util': obj_pt['Average'], 'mem_util': 45})  # fake mem

    v_df = pd.DataFrame(v_rows)
    os.makedirs('data', exist_ok=True)
    v_df.to_csv('data/metrics_week.csv', index=False)
    print("Wrote metrics -> data/metrics_week.csv")

if __name__ == '__main__':
    main()
