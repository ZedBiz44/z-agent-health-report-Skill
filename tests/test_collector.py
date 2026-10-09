import importlib.util
from pathlib import Path
import unittest
import datetime as dt
from types import SimpleNamespace
from zoneinfo import ZoneInfo

spec=importlib.util.spec_from_file_location('collector',Path(__file__).resolve().parents[1]/'scripts/collect-discord-reports.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def msg(i,text,who='terry',bot=True):
    return {'id':str(i),'content':text,'author':{'id':who,'username':who+'-openclaw','bot':bot},'timestampMs':1791480000000}
head='# Agent Health Report\n**Agent:** Terry\n**Mode:** Daily\n**Overall:** Healthy\n'
tail='\n'.join('## '+s+'\n- None' for s in c.SECTIONS)+'\nNo changes were made.'

class Tests(unittest.TestCase):
    def test_hermes_chunk_footer(self):
        row=next(r for r in c.assemble([msg(1,head+tail+' (2/2)')],'daily') if r['agent']=='Terry')
        self.assertEqual(row['collection'],'complete')
    def test_agent_profile_suffix(self):
        rows=c.assemble([msg(1,head.replace('**Agent:** Terry','**Agent:** Terry (`main`)')+tail)],'daily')
        self.assertEqual(next(r for r in rows if r['agent']=='Terry')['status'],'Healthy')
    def test_continuation_and_interleaved_other_bot(self):
        rows=c.assemble([msg(1,head),msg(2,'unrelated','victor'),msg(3,tail)],'daily')
        row=next(r for r in rows if r['agent']=='Terry')
        self.assertEqual(row['status'],'Healthy');self.assertEqual(row['messageIds'],['1','3'])
    def test_incomplete_not_healthy(self):
        self.assertEqual(next(r for r in c.assemble([msg(1,head)],'daily') if r['agent']=='Terry')['status'],'Unknown')
    def test_forwarded_not_accepted(self):
        self.assertTrue(all(r['status']=='Unknown' for r in c.assemble([msg(1,head+tail,'victor')],'daily')))
    def test_read_error_visible(self):
        r=c.collect('daily',call=lambda *a,**k:SimpleNamespace(returncode=1,stdout=''),now=dt.datetime(2026,10,8,tzinfo=ZoneInfo('America/Edmonton')))
        self.assertTrue(r['errors']);self.assertEqual(r['counts']['Unknown'],16)
    def test_pagination_and_boundary(self):
        import json
        old=msg(0,'old');old['timestampMs']=1
        pages=[[msg(3,tail)],[msg(1,head),old]];calls=[]
        def call(argv,**kw):
            calls.append(argv);return SimpleNamespace(returncode=0,stdout=json.dumps({'payload':{'ok':True,'messages':pages.pop(0)}}))
        r=c.collect('daily',call=call,now=dt.datetime(2026,10,8,tzinfo=ZoneInfo('America/Edmonton')))
        self.assertEqual(r['complete'],1);self.assertIn('--before',calls[1])

if __name__=='__main__':unittest.main()
