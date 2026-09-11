"""Compile fixed, assistant-authored synthetic scenarios. No LLM/network calls."""
import csv
import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / 'simulation'

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def money(v):
    return str(D(v).quantize(D('0.01'), rounding=ROUND_HALF_UP))

def main():
    seed = json.loads((SIM / 'seed_scenarios.json').read_text())
    assert seed['simulationOnly'] is True
    tables = {k: [] for k in ['organizations', 'customers', 'accounts', 'products', 'transactions', 'ledger_entries', 'daily_balances', 'credit_facilities', 'holdings', 'calendar']}
    tables['organizations'] = seed['organizations']
    tables['products'] = [{k:p[k] for k in ['productId','productName','family','status']} for p in seed['products']]
    start, end = (date.fromisoformat(seed['period'][k]) for k in ['from','to'])
    dates = [start + timedelta(days=i) for i in range((end-start).days)]
    for dt in dates:
        tables['calendar'].append({'businessDate':str(dt),'calendarVersion':'SIM-CAL-1','calendarDay':True,'businessDay':dt.weekday()<5})
    for i, c in enumerate(seed['customers'],1):
        tables['customers'].append({k:c[k] for k in ['customerId','syntheticName','orgId','industryCode']})
        for account in c['accounts']:
            aid, ccy = account['accountId'], account['currency']
            tables['accounts'].append({'accountId':aid,'customerId':c['customerId'],'currency':ccy,'openingBalance':account['openingBalance'],'validFrom':str(start),'validTo':str(end)})
            daily = {dt:D('0') for dt in dates}
            for j,(day,amt) in enumerate(account['events'],1):
                tid=f'SIM-TX-{aid.removeprefix("SIM-")}-{j:02d}'
                dt=start+timedelta(days=day-1)
                value=D(amt);daily[dt]+=value
                tables['transactions'].append({'transactionId':tid,'accountId':aid,'businessDate':str(dt),'signedAmount':money(value),'currency':ccy,'eventRef':f'{aid}/events/{j-1}'})
                # Bank's liability ledger: customer deposit increase = credit.
                side='CREDIT' if value>=0 else 'DEBIT'
                for k,ledger,direction in [(1,aid,side),(2,'SIM-CLEARING-'+ccy,'DEBIT' if side=='CREDIT' else 'CREDIT')]:
                    tables['ledger_entries'].append({'entryId':f'{tid}-E{k}','transactionId':tid,'ledgerAccount':ledger,'direction':direction,'amount':money(abs(value)),'currency':ccy})
            balance=D(account['openingBalance'])
            for dt in dates:
                closing=balance+daily[dt]
                tables['daily_balances'].append({'accountId':aid,'businessDate':str(dt),'openingBalance':money(balance),'netMovement':money(daily[dt]),'closingBalance':money(closing),'currency':ccy,'snapshotId':seed['snapshotId']})
                balance=closing
        tables['credit_facilities'].append({'facilityId':f'SIM-F{i:03d}','customerId':c['customerId'],**c['credit'],'asOf':str(end)})
        tables['holdings'].append({'holdingId':f'SIM-H{i:03d}','customerId':c['customerId'],'productId':c['holdingProductId'],'validFrom':str(start),'validTo':str(end)})
    for name, rows in tables.items():
        path=SIM/'tables'/f'{name}.csv';path.parent.mkdir(exist_ok=True)
        with path.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    sources=json.loads((SIM/'source_catalog.json').read_text())
    for s in sources:
        s['contentHash']=sha(ROOT/s['path'])
    dump(SIM/'source_catalog.json',sources)
    nodes=[{'nodeId':c['customerId'],'nodeType':'Customer','sourceRef':'simulation/tables/customers.csv','simulationOnly':True} for c in seed['customers']]
    nodes += [{'nodeId':p['productId'],'nodeType':'Product','sourceRef':'simulation/tables/products.csv','simulationOnly':True} for p in seed['products']]
    edges=[{'edgeId':h['holdingId'],'from':h['customerId'],'to':h['productId'],'predicate':'holdsProduct','sourceRef':'simulation/tables/holdings.csv','sourceRecordId':h['holdingId'],'projectionVersion':'SIM-GRAPH-1','validFrom':h['validFrom'],'validTo':h['validTo'],'simulationOnly':True} for h in tables['holdings']]
    for name,records in [('nodes',nodes),('edges',edges)]:
        (SIM/'graph'/f'{name}.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in records),encoding='utf-8')
    # Independent hand-computable oracle, not derived from generated daily balances.
    expected=money(D('3000000')+D('100000')*D(25)/D(30)-D('200000')*D(15)/D(30))
    dump(SIM/'oracles'/'expected.json',{'simulationOnly':True,'metricId':'SIM.METRIC.CUSTOMER_AVG_DEPOSIT','customerId':'SIM-C001','period':seed['period'],'currency':'CNY','expectedValue':expected,'derivation':'3000000 + 100000*25/30 - 200000*15/30; RoundHalfUp(2)','nominalUnusedCredit':'8000000.00','drawableAmount':None,'eligibility':'UNKNOWN','industryLabelsStatus':'EXPERT_REVIEW_PENDING'})
    paths=sorted(p for p in SIM.rglob('*') if p.is_file() and p.name!='dataset_manifest.json')
    dump(SIM/'dataset_manifest.json',{'simulationOnly':True,'version':'1.0.0','snapshotId':seed['snapshotId'],'generationMethod':seed['generationMethod'],'externalModelApiCalled':False,'tableCounts':{k:len(v) for k,v in tables.items()},'documentCount':len(sources),'graphNodes':len(nodes),'graphEdges':len(edges),'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in paths]})
    print(json.dumps({'tableCounts':{k:len(v) for k,v in tables.items()},'documents':len(sources),'oracle':expected},ensure_ascii=False))

if __name__=='__main__':main()
