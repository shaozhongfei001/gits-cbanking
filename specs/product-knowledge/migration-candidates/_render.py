import pathlib
t=pathlib.Path('_tables.tpl').read_text()
D={'h2':('VARCHAR','TIMESTAMP WITH TIME ZONE','CLOB','BOOLEAN','TRUE','FALSE'),'mysql':('VARCHAR','DATETIME(6)','LONGTEXT','TINYINT(1)','1','0')}
for d,c in D.items():
    s=t.format(vc=c[0],ts=c[1],txt=c[2],bool=c[3],true=c[4],false=c[5])
    s+=pathlib.Path('_trailer_'+d+'.sql.tpl').read_text()
    pathlib.Path(d,'V023__product_knowledge_objects.sql').write_text(s)
    print(d,len(s.splitlines()),'lines')
