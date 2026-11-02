"""Offline regression tests for R9.3's null AMFI Option, exact-source cache, rate-limit fail-closed handling.

No network access is required. Source backfill acceptance remains a separate live test.
"""
import datetime as dt, importlib.util, json, tempfile, unittest
from pathlib import Path
from urllib.error import HTTPError

SOURCE=Path("research/stage512/pipelines/r9_lic_gsec_official_amfi_history.py")
spec=importlib.util.spec_from_file_location("r93",SOURCE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class MockResponse:
    status=200
    def __init__(self,payload):self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,cap):return self.payload

def fake_body(start,option):
    records=[{"date":str(start+dt.timedelta(days=i)),"nav":13.5+i*.02,"Option":option} for i in range(6)]
    return json.dumps({"data":{"scheme_name":"LIC MF Nifty 8-13 yr G-Sec ETF",
      "nav_groups":[{"nav_name":"LIC MF Nifty 8-13 yr G-Sec ETF","historical_records":records}]}}).encode()

class R9Regression(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.oldbase,self.oldopen,self.oldsleep=mod.BASE,mod.urlopen,mod.time.sleep
        mod.BASE=Path(self.temp.name)
        mod.time.sleep=lambda _:None
    def tearDown(self):
        mod.BASE,mod.urlopen,mod.time.sleep=self.oldbase,self.oldopen,self.oldsleep
        self.temp.cleanup()
    def test_null_option_accepted_and_cache_protects_raw_sha(self):
        a,b=dt.date(2015,1,5),dt.date(2015,1,12)
        body=fake_body(a,None)
        mod.urlopen=lambda req,timeout:MockResponse(body)
        rows,source=mod.get_one((a,b))
        self.assertEqual(source["status"],"PASS_SOURCE_SEGMENT")
        self.assertEqual(len(rows),6)
        self.assertFalse(source["retrieved_from_committed_cache"])
        def no_network(*args,**kwargs):raise AssertionError("cache not used")
        mod.urlopen=no_network
        rows2,source2=mod.get_one((a,b))
        self.assertEqual(rows2,rows)
        self.assertTrue(source2["retrieved_from_committed_cache"])
        self.assertEqual(source2["sha256"],source["sha256"])
    def test_explicit_dividend_rejected(self):
        a,b=dt.date(2017,1,5),dt.date(2017,1,12)
        mod.urlopen=lambda req,timeout:MockResponse(fake_body(a,"Dividend"))
        rows,source=mod.get_one((a,b))
        self.assertEqual(rows,[])
        self.assertEqual(source["status"],"FAIL")
        self.assertTrue(any("non-growth option" in x for x in source["errors"]))
    def test_rate_limit_fail_closed_without_source_rows(self):
        a,b=dt.date(2022,1,5),dt.date(2022,1,12)
        def blocked(req,timeout):
            raise HTTPError("https://www.amfiindia.com/api/nav-history",429,"Too Many Requests",{},None)
        mod.urlopen=blocked
        rows,source=mod.get_one((a,b))
        self.assertFalse(rows)
        self.assertEqual(len(source["errors"]),3)
        self.assertTrue(all("429" in x for x in source["errors"]))
    def test_windows_contiguous_and_nonoverlapping(self):
        seg=mod.segments()
        self.assertEqual(seg[0][0],dt.date(2014,12,26))
        self.assertEqual(seg[-1][1],dt.date(2026,10,30))
        self.assertEqual(len(seg),24)
        for (a,b),(c,d) in zip(seg,seg[1:]):
            self.assertEqual(c,b+dt.timedelta(days=1))
            self.assertLess((b-a).days,190)

if __name__=="__main__":unittest.main()
