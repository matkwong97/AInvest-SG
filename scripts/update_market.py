#!/usr/bin/env python3
"""Best-effort delayed quote snapshot; never invent values or overwrite with empty data."""
import json, urllib.request, urllib.parse, datetime, pathlib, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'market.json'
SYMBOLS={'^GSPC':'S&P 500','^NDX':'Nasdaq 100','^DJI':'Dow Jones','^FTSE':'FTSE 100','^HSI':'Hang Seng','^STI':'STI','^N225':'Nikkei 225','^GDAXI':'DAX','NVDA':'NVIDIA','AAPL':'Apple','MSFT':'Microsoft','D05.SI':'DBS Group','U11.SI':'UOB','SPY':'S&P 500 ETF','TLT':'Long Treasury ETF','BND':'Total Bond ETF','VTI':'Total Stock ETF'}
try: old=json.loads(OUT.read_text())
except Exception: old={'quotes':{}}
quotes=old.get('quotes',{}).copy()
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
updated=0
for sym,name in SYMBOLS.items():
    try:
        url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(sym,safe='')+'?interval=1d&range=5d'
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 AInvestSG/1.0','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=12) as r: d=json.load(r)
        obj=d['chart']['result'][0]; meta=obj['meta']; price=meta.get('regularMarketPrice'); prev=meta.get('chartPreviousClose') or meta.get('previousClose')
        if not isinstance(price,(int,float)) or price<=0: raise ValueError('no verified price')
        change=(price/prev-1)*100 if isinstance(prev,(int,float)) and prev>0 else None
        quotes[sym]={'name':name,'price':round(price,4),'change_pct':round(change,3) if change is not None else None,'currency':meta.get('currency',''),'asof':datetime.datetime.fromtimestamp(meta.get('regularMarketTime',time.time()),datetime.timezone.utc).isoformat(timespec='seconds'),'fetched_at':now,'source':'Yahoo Finance chart (best effort; may be delayed)'}
        updated+=1
    except Exception as e: print(sym, 'unavailable:',str(e)[:110])
    time.sleep(.2)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({'generated_at':now,'successful_refreshes':updated,'quotes':quotes},indent=2)+'\n')
print('updated',updated,'of',len(SYMBOLS),'retained',len(quotes))
