#!/usr/bin/env python3
"""Daily export of AWS Cost Explorer data to CSV."""

import os
import datetime
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

v_client = boto3.client(
    'ce',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)


def get_cost(v_start: str, v_end: str) -> pd.DataFrame:
    v_resp = v_client.get_cost_and_usage(
        TimePeriod={'Start': v_start, 'End': v_end},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
    )
    v_rows = []
    for obj_result in v_resp['ResultsByTime']:
        v_rows.append({
            'date': obj_result['TimePeriod']['Start'],
            'cost_usd': float(obj_result['Total']['UnblendedCost']['Amount'])
        })
    return pd.DataFrame(v_rows)


def main():
    v_today = datetime.date.today()
    v_yesterday = v_today - datetime.timedelta(days=1)
    v_df = get_cost(v_yesterday.isoformat(), v_today.isoformat())

    v_out = os.environ.get('COST_CSV_PATH', 'data/cost_daily.csv')
    os.makedirs(os.path.dirname(v_out), exist_ok=True)
    v_df.to_csv(v_out, index=False)
    print(f"Wrote {len(v_df)} rows -> {v_out}")


if __name__ == '__main__':
    main()
