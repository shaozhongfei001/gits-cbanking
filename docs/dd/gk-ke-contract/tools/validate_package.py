"""Offline author self-check. Does NOT test GITS/KERT services or approve releases."""
import copy
import csv
import hashlib
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import jsonschema

R=Path(__file__).resolve().parents[1]
RESULTS=[]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def digest(v):return hashlib.sha256(canonical(v)).hexdigest()
def record(name,ok,detail=''):
    RESULTS.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
def table(name):
    with (R/'simulation/tables'/f'{name}.csv').open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def schema_error(name,value):
    return bool(list(jsonschema.Draft202012Validator(read(f'schemas/{name}.schema.json')).iter_errors(value)))

def map_errors(m,registry):
    errors=[];nodes={n['nodeId']:n for n in m['nodes']}
    if len(nodes)!=len(m['nodes']):errors.append('DUPLICATE_NODE')
    known={(x['assetId'],x['version']) for x in registry if x['lifecycle']=='PUBLISHED'}
    for n in m['nodes']:
        if n['nodeType'] in ('Asset','Capability') and (n['ref']['id'],n['ref']['version']) not in known:errors.append('DEPENDENCY_UNRESOLVED')
    if any(e not in nodes for e in m['entryNodes']):errors.append('ENTRY_UNRESOLVED')
    graph=defaultdict(list)
    for e in m['edges']:
        if e['from'] not in nodes or e['to'] not in nodes:errors.append('EDGE_UNRESOLVED');continue
        a,b=nodes[e['from']]['nodeType'],nodes[e['to']]['nodeType']
        allowed={'requires':a=='Task' and b in ('Asset','Capability'),'optional':a=='Task' and b in ('Asset','Capability'),'uses':a=='Capability' and b=='Asset','dependsOn':a in ('Asset','Capability') and b in ('Asset','Capability'),'covers':a=='KnowledgeDomain' and b=='Asset','relatedTo':a in ('KnowledgeDomain','Asset') and b in ('KnowledgeDomain','Asset')}
        if not allowed[e['relation']]:errors.append('EDGE_TYPE_VIOLATION')
        if e['relation'] in ('requires','uses','dependsOn'):graph[e['from']].append(e['to'])
    visited=set();active=set()
    def dfs(n):
        if n in active:return True
        if n in visited:return False
        active.add(n)
        for nxt in graph.get(n,[]):
            if dfs(nxt):return True
        active.remove(n);visited.add(n);return False
    if any(dfs(n) for n in list(nodes)):errors.append('DEPENDENCY_CYCLE')
    return errors

def evidence_errors(a):
    errors=[]
    for e in a['evidence']:
        p=(R/e['path']).resolve()
        if not p.is_relative_to(R) or not p.is_file():errors.append('SOURCE_UNRESOLVED');continue
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=e['sourceHash']:errors.append('SOURCE_HASH_MISMATCH')
        if hashlib.sha256(e['quote'].encode()).hexdigest()!=e['quoteHash']:errors.append('QUOTE_HASH_MISMATCH')
        if e['quote'] not in raw.decode('utf-8'):errors.append('QUOTE_NOT_LOCATED')
    return errors

def release_errors(rel,review):
    e=[]
    if digest(rel['payload'])!=rel['payloadHash']:e.append('PAYLOAD_HASH_MISMATCH')
    if review['targetHash']!=rel['payloadHash'] or review['targetId']!=rel['payload']['releaseId']:e.append('APPROVAL_MISMATCH')
    if review['decision']!='APPROVED' or review['reviewerPrincipal']==review['authorPrincipal']:e.append('INVALID_APPROVER')
    if review['purpose'] not in rel['payload']['purposeFlags']:e.append('PURPOSE_MISMATCH')
    map_review=read('simulation/map_review_decision.json')
    if map_review['decisionId'] not in rel['approvalRefs'] or map_review['reviewerRole']!='MAP_OWNER' or map_review['targetHash']!=rel['payloadHash']:e.append('MAP_REVIEW_MISSING')
    states={x['kind']:x['state'] for x in rel['projectionStates']}
    if any(states.get(k)!='READY' for k in rel['payload']['requiredProjectionKinds']):e.append('REQUIRED_PROJECTION_NOT_READY')
    for a in rel['payload']['artifactRefs']:
        if digest(read(a['path']))!=a['hash']:e.append('ARTIFACT_HASH_MISMATCH')
    return e

def avg_deposit(customer,accounts,balances):
    accts={a['accountId']:a for a in accounts if a['customerId']==customer}
    if not accts:raise ValueError('POPULATION_EMPTY')
    if any(a['currency']!='CNY' for a in accts.values()):raise ValueError('CURRENCY_POLICY_REQUIRED')
    seen={};days={str(date(2026,9,1)+timedelta(days=i)) for i in range(30)}
    for b in balances:
        if b['accountId'] not in accts:continue
        key=(b['accountId'],b['businessDate'])
        if key in seen:raise ValueError('GRAIN_VIOLATION')
        if b['currency']!=accts[b['accountId']]['currency']:raise ValueError('CURRENCY_MISMATCH')
        seen[key]=D(b['closingBalance'])
    required={(a,d) for a in accts for d in days}
    if set(seen)!=required:raise ValueError('DATA_INCOMPLETE')
    return str((sum(seen.values())/D(30)).quantize(D('0.01'),rounding=ROUND_HALF_UP))

def expect_error(name,fn,expected):
    try:fn();record(name,False,'expected '+expected)
    except ValueError as e:record(name,str(e)==expected,str(e))

def main():
    for p in sorted((R/'schemas').glob('*.schema.json')):
        name=p.name.removesuffix('.schema.json');s=json.loads(p.read_text())
        jsonschema.Draft202012Validator.check_schema(s)
        record('schema-positive:'+name,not schema_error(name,read(f'examples/positive/{name}.json')))
    for case in read('examples/schema_cases.json'):
        record('schema-negative:'+case['path'],schema_error(case['schema'],read(case['path'])),case['reason'])
    for a in read('simulation/registry_snapshot.json'):
        record('registry-schema:'+a['assetId'],not schema_error('AssetVersion',a))
        record('registry-content-hash:'+a['assetId'],hashlib.sha256((R/a['contentRef']).read_bytes()).hexdigest()==a['contentHash'])
    registry=read('simulation/registry_snapshot.json');m=read('examples/positive/KnowledgeMap.json')
    record('map-reference-closure',not map_errors(m,registry))
    bad=copy.deepcopy(m);bad['nodes'][1]['ref']['id']='SIM-MISSING'
    record('map-missing-capability-reject','DEPENDENCY_UNRESOLVED' in map_errors(bad,registry))
    bad=copy.deepcopy(m);bad['edges'].append({'edgeId':'SIM-CYCLE','from':'N-PRODUCT','to':'N-SKILL','relation':'dependsOn','reason':'bad','designDecisionRef':'SIM-D'})
    record('map-dependency-cycle-reject','DEPENDENCY_CYCLE' in map_errors(bad,registry))
    a=read('examples/positive/Assertion.json');record('assertion-source-quote',not evidence_errors(a))
    bad=copy.deepcopy(a);bad['evidence'][0]['quote']='期限不得超过 18 个月。';bad['evidence'][0]['quoteHash']=hashlib.sha256(bad['evidence'][0]['quote'].encode()).hexdigest()
    record('plausible-quote-not-in-source-reject','QUOTE_NOT_LOCATED' in evidence_errors(bad))
    rel=read('examples/positive/ReleaseManifest.json');review=read('examples/positive/ReviewDecision.json')
    record('release-fixture-hash-and-review',not release_errors(rel,review),'simulation fixture only; no real approval')
    bad=copy.deepcopy(rel);bad['approvalRefs']=['SIM-REVIEW-001']
    record('content-approval-without-map-approval-reject','MAP_REVIEW_MISSING' in release_errors(bad,review))
    bad=copy.deepcopy(rel);bad['payload']['purposeFlags'].append('RECOMMENDATION')
    record('post-approval-change-reject','PAYLOAD_HASH_MISMATCH' in release_errors(bad,review))
    bad=copy.deepcopy(review);bad['reviewerPrincipal']=bad['authorPrincipal']
    record('self-approval-reject','INVALID_APPROVER' in release_errors(rel,bad))
    bad=copy.deepcopy(rel);bad['projectionStates'][0]['state']='PENDING'
    record('partial-publish-reject','REQUIRED_PROJECTION_NOT_READY' in release_errors(bad,review))
    plan=read('examples/positive/ActivationPlan.json');pc={k:v for k,v in plan.items() if k not in ('planId','planHash')}
    record('plan-canonical-hash',digest(pc)==plan['planHash'])
    # Digest ignores object key order but preserves semantically meaningful array order.
    record('plan-key-order-invariant',digest(pc)==digest(dict(reversed(list(pc.items())))))
    customers=table('customers');accounts=table('accounts');products=table('products');txs=table('transactions');balances=table('daily_balances');ledger=table('ledger_entries')
    cs={x['customerId'] for x in customers};ps={x['productId'] for x in products};ac={x['accountId']:x for x in accounts};ts={x['transactionId']:x for x in txs}
    record('primary-keys',len(cs)==len(customers) and len(ps)==len(products) and len(ac)==len(accounts) and len(ts)==len(txs))
    record('foreign-keys',all(x['customerId'] in cs for x in accounts) and all(x['accountId'] in ac for x in txs) and all(x['customerId'] in cs and x['productId'] in ps for x in table('holdings')))
    record('same-name-different-identity',customers[0]['syntheticName']==customers[10]['syntheticName'] and customers[0]['customerId']!=customers[10]['customerId'])
    movement=defaultdict(lambda:D(0))
    for t in txs:movement[t['accountId'],t['businessDate']]+=D(t['signedAmount'])
    rolling={k:D(a['openingBalance']) for k,a in ac.items()};ok=True
    for b in sorted(balances,key=lambda x:(x['accountId'],x['businessDate'])):
        aid=b['accountId'];n=movement[aid,b['businessDate']]
        ok &= D(b['openingBalance'])==rolling[aid] and D(b['netMovement'])==n and D(b['closingBalance'])==rolling[aid]+n
        rolling[aid]=D(b['closingBalance'])
    record('daily-balance-rollforward',ok)
    sums=defaultdict(lambda:D(0));counts=defaultdict(int);ok=True
    for x in ledger:
        counts[x['transactionId']]+=1;sums[x['transactionId']]+=D(x['amount'])*(1 if x['direction']=='DEBIT' else -1)
        ok &= x['transactionId'] in ts and x['currency']==ts[x['transactionId']]['currency'] and D(x['amount'])==abs(D(ts[x['transactionId']]['signedAmount']))
    record('ledger-balanced',ok and set(counts)==set(ts) and all(v==2 for v in counts.values()) and all(v==0 for v in sums.values()))
    record('currency-row-consistency',all(t['currency']==ac[t['accountId']]['currency'] for t in txs))
    oracle=read('simulation/oracles/expected.json')
    record('metric-independent-oracle',avg_deposit('SIM-C001',accounts,balances)==oracle['expectedValue'])
    with sqlite3.connect(':memory:') as db:
        db.executescript('CREATE TABLE customers(customerId TEXT PRIMARY KEY,orgId TEXT); CREATE TABLE accounts(accountId TEXT PRIMARY KEY,customerId TEXT); CREATE TABLE account_day_cents(accountId TEXT,businessDate TEXT,snapshotId TEXT,balance_cents INTEGER,PRIMARY KEY(accountId,businessDate,snapshotId));')
        db.executemany('INSERT INTO customers VALUES (?,?)',[(x['customerId'],x['orgId']) for x in customers])
        db.executemany('INSERT INTO accounts VALUES (?,?)',[(x['accountId'],x['customerId']) for x in accounts])
        db.executemany('INSERT INTO account_day_cents VALUES (?,?,?,?)',[(x['accountId'],x['businessDate'],x['snapshotId'],int(D(x['closingBalance'])*100)) for x in balances])
        query=(R/'simulation/avg_deposit.sql').read_text()
        params={'customerId':'SIM-C001','authorizedOrgId':'SIM-O01','periodFrom':'2026-09-01','periodTo':'2026-10-01','snapshotId':'SIM-SNAPSHOT-20261001'}
        row=db.execute(query,params).fetchone()
        record('registered-sql-fixture-oracle',str((D(row[0])/D(100)/D(30)).quantize(D('0.01'),rounding=ROUND_HALF_UP))==oracle['expectedValue'] and row[1:]==(60,2),'SQLite fixture; excludes live authorization service')
        params['authorizedOrgId']='SIM-O02';row=db.execute(query,params).fetchone()
        record('registered-sql-org-predicate',row[0] is None and row[1]==0)
    bad=balances+[copy.deepcopy(balances[0])];expect_error('duplicate-account-day-reject',lambda:avg_deposit('SIM-C001',accounts,bad),'GRAIN_VIOLATION')
    bad=balances[1:];expect_error('missing-day-reject',lambda:avg_deposit('SIM-C001',accounts,bad),'DATA_INCOMPLETE')
    expect_error('cross-currency-reject',lambda:avg_deposit('SIM-C002',accounts,balances),'CURRENCY_POLICY_REQUIRED')
    # Same balances on two different accounts must BOTH contribute; no SUM(DISTINCT balance).
    eq=[{'accountId':'X1','customerId':'X','currency':'CNY'},{'accountId':'X2','customerId':'X','currency':'CNY'}]
    eqb=[{'accountId':a['accountId'],'businessDate':str(date(2026,9,1)+timedelta(days=i)),'currency':'CNY','closingBalance':'100.00'} for a in eq for i in range(30)]
    record('equal-balance-two-accounts',avg_deposit('X',eq,eqb)=='200.00')
    facilities=table('credit_facilities');f=facilities[0]
    record('credit-and-drawable-separation',D(f['approvedAmount'])-D(f['usedAmount'])==D(oracle['nominalUnusedCredit']) and oracle['drawableAmount'] is None)
    record('credit-bounds',all(D('0')<=D(x['usedAmount'])<=D(x['approvedAmount']) for x in facilities))
    sources=read('simulation/source_catalog.json')
    record('source-hashes-and-synthetic-mark',len(sources)==18 and all(s['simulationOnly'] and hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['contentHash'] and '虚构模拟材料' in (R/s['path']).read_text() for s in sources))
    nodes=[json.loads(l) for l in (R/'simulation/graph/nodes.jsonl').read_text().splitlines()];edges=[json.loads(l) for l in (R/'simulation/graph/edges.jsonl').read_text().splitlines()];ids={n['nodeId'] for n in nodes}
    record('graph-source-closure',all(e['from'] in ids and e['to'] in ids and e['sourceRecordId'] in {h['holdingId'] for h in table('holdings')} for e in edges))
    for item in read('simulation/dataset_manifest.json')['files']:
        record('dataset-file-hash:'+item['path'],hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256'])
    for item in read('CONTRACT_INDEX.json')['contracts']:
        record('contract-document-hash:'+item['contractId'],hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256'])
    report={'scope':'OFFLINE_AUTHOR_SELF_CHECK','independentQa':'NOT_PERFORMED','serviceE2E':'NOT_PERFORMED','kuzuIntegration':'NOT_PERFORMED','lightRagIntegration':'NOT_PERFORMED','actualHumanApproval':'NOT_PERFORMED','checks':RESULTS,'passed':sum(x['status']=='PASS' for x in RESULTS),'failed':sum(x['status']=='FAIL' for x in RESULTS)}
    (R/'acceptance/package_self_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
    for x in RESULTS:
        if x['status']=='FAIL':print(x)
    return 1 if report['failed'] else 0

if __name__=='__main__':sys.exit(main())
