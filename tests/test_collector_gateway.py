import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec=importlib.util.spec_from_file_location('collector_gateway',Path(__file__).resolve().parents[1]/'scripts/collect-discord-reports.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class GatewayCollectorTests(unittest.TestCase):
    def invoke(self, response=None, error=None, before=False):
        config=json.dumps({'gateway':{'port':3002,'auth':{'token':'test-only-token'}}})
        args=['openclaw','message','read']+(['--before','12345'] if before else [])
        with patch.object(c,'__file__','/test-state/workspace/skills/health/scripts/collect-discord-reports.py'),patch.dict(c.os.environ,{},clear=True),patch.object(c.Path,'read_text',return_value=config),patch.object(c.urllib.request,'urlopen',side_effect=error,return_value=io.BytesIO(json.dumps(response).encode())) as call:
            result=c.read_through_gateway(args)
            return result,call.call_args.args[0]
    def test_resident_read_preserves_pagination(self):
        r,req=self.invoke({'ok':True,'result':{'details':{'ok':True,'messages':[]}}},before=True)
        self.assertEqual(req.full_url,'http://127.0.0.1:3002/tools/invoke')
        body=json.loads(req.data)
        self.assertEqual(body['args']['before'],'12345')
        self.assertEqual(body['args']['target'],c.CHANNEL)
        self.assertTrue(json.loads(r.stdout)['payload']['ok'])
    def test_gateway_failure_is_not_a_cli_fallback(self):
        e=urllib.error.HTTPError('http://local',403,'denied',{},None)
        with self.assertRaisesRegex(ValueError,'HTTP 403'):
            self.invoke(error=e)
    def test_missing_structured_result_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'structured'):
            self.invoke({'ok':True,'result':{'content':[]}})
    def test_refused_read_marks_every_agent_unknown(self):
        with patch.object(c,'read_through_gateway',side_effect=ValueError('resident read unavailable')):
            r=c.collect('daily')
        self.assertEqual(r['counts']['Unknown'],16)
        self.assertTrue(r['errors'])

if __name__=='__main__':unittest.main()
