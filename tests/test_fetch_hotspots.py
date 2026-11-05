import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("fetch_hotspots", Path(__file__).resolve().parents[1] / "scripts/fetch_hotspots.py")
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)

class FetchContractTests(unittest.TestCase):
    def test_missing_key_does_not_call_network_or_write(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            output = Path(tmp) / "result.json"
            with patch.object(sys, "argv", ["fetch", "--output", str(output)]), patch.object(fetch.urllib.request, "urlopen") as network, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fetch.main(), 2)
                network.assert_not_called()
            self.assertFalse(output.exists())

    def test_response_dedup_metadata_and_reflection_redaction(self):
        row = {"hotId":"event-a", "platName":"抖音", "title":"示例话题", "maxHotScore":12345, "maxPosition":4, "topOfTheDayTime":"2", "firstRankTime":"2026-01-01 01:00:00", "latestRankDate":"2026-01-01 02:00:00", "url":"https://example.com/topic"}
        payload = {"code":2000,"data":[{"hotSpotList":[row,row]},{"hotSpotList":[dict(row,platName="微博")]}],"diagnostic":"test-value-not-a-real-key"}
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps(payload).encode()
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{"REDFOX_API_KEY":"test-value-not-a-real-key"}):
            output=Path(tmp)/"result.json"
            with patch.object(sys,"argv",["fetch","--output",str(output)]),patch.object(fetch.urllib.request,"urlopen",return_value=Response()),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fetch.main(),0)
            text=output.read_text(encoding="utf-8")
            result=json.loads(text)
            self.assertEqual((result["raw_count"],result["unique_count"]),(3,2))
            self.assertEqual(result["hotspots"][0]["maxPosition"],4)
            self.assertEqual(result["hotspots"][0]["firstRankTime"],row["firstRankTime"])
            self.assertNotIn("test-value-not-a-real-key",text)

    def test_invalid_interval_never_calls_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(sys,"argv",["fetch","--hours","169","--output",str(Path(tmp)/"result.json")]),patch.object(fetch.urllib.request,"urlopen") as network,contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit): fetch.main()
                network.assert_not_called()

if __name__ == "__main__": unittest.main()
