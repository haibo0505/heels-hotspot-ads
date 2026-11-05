"""Fetch Redfox records; credential comes only from REDFOX_API_KEY."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

def main():
    parser=argparse.ArgumentParser(description='Fetch Redfox hotspot records without printing credentials.')
    parser.add_argument('--hours',type=int,default=24,help='Hours ending at the current complete Beijing hour, 1..168')
    parser.add_argument('--start-date',help='Beijing time, YYYY-MM-DD HH:MM:SS; use with --end-date')
    parser.add_argument('--end-date')
    parser.add_argument('--output',type=Path,required=True,help='JSON destination; follow the current workspace storage rules')
    args=parser.parse_args()
    if bool(args.start_date)!=bool(args.end_date): parser.error('Provide both start-date and end-date.')
    try:
        if args.start_date:
            start=datetime.strptime(args.start_date,'%Y-%m-%d %H:%M:%S')
            end=datetime.strptime(args.end_date,'%Y-%m-%d %H:%M:%S')
        else:
            if not 1<=args.hours<=168: parser.error('hours must be 1..168')
            end=datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None,minute=0,second=0,microsecond=0)
            start=end-timedelta(hours=args.hours)
        if not timedelta(0)<end-start<=timedelta(days=7): parser.error('Query interval must be positive and at most 7 days.')
    except ValueError: parser.error('Invalid date format.')
    key=os.environ.get('REDFOX_API_KEY')
    if not key:
        print(json.dumps({'status':'unavailable','reason':'REDFOX_API_KEY is not configured; use public-source fallback.'}))
        return 2
    body={'source':'全平台热搜推荐-GitHub','startDate':start.strftime('%Y-%m-%d %H:%M:%S'),'endDate':end.strftime('%Y-%m-%d %H:%M:%S')}
    request=urllib.request.Request('https://redfox.hk/story/api/hotKeyword/list',data=json.dumps(body).encode('utf-8'),headers={'Content-Type':'application/json','X-API-KEY':key},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=25) as response:
            raw=json.loads(response.read().decode('utf-8').replace(key,'[REDACTED]'))
    except urllib.error.HTTPError as ex:
        print(json.dumps({'status':'error','http_status':ex.code})); return 3
    except (urllib.error.URLError,TimeoutError,json.JSONDecodeError):
        print(json.dumps({'status':'error','reason':'Network timeout, connection or JSON decoding failure.'})); return 3
    if raw.get('code')!=2000:
        print(json.dumps({'status':'error','api_code':raw.get('code'),'reason':'API request was not successful; check account access or quota.'})); return 3
    records=[]
    for group in raw.get('data') or []:
        for row in group.get('hotSpotList') or []:
            if isinstance(row,dict): records.append(dict(row))
    seen={}
    for row in records:
        identity=(row.get('platName'),row.get('hotId') or (row.get('title'),row.get('url')))
        if identity not in seen: seen[identity]=row
    unique=list(seen.values())
    result={'status':'success','fetched_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'query_range':{'start_date':body['startDate'],'end_date':body['endDate'],'timezone':'Asia/Shanghai'},'raw_count':len(records),'unique_count':len(unique),'platform_counts':dict(Counter(row.get('platName','unknown') for row in unique)),'hotspots':unique,'raw_response':raw}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'success','output':str(args.output),'raw_count':len(records),'unique_count':len(unique)},ensure_ascii=False))
    return 0

if __name__=='__main__': sys.exit(main())
