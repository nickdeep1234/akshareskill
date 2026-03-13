from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / "skills" / "ashare" / "scripts" / "query_akshare.py"
SPEC = importlib.util.spec_from_file_location("query_akshare", MODULE_PATH)
query_akshare = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = query_akshare
SPEC.loader.exec_module(query_akshare)


class QueryAkshareTests(unittest.TestCase):
    def setUp(self) -> None:
        query_akshare.get_stock_catalog.cache_clear()
        query_akshare.get_stock_spot_df.cache_clear()
        query_akshare.get_index_catalog.cache_clear()
        query_akshare.get_main_index_df.cache_clear()
        query_akshare.get_fund_catalog.cache_clear()
        query_akshare.get_fund_daily_df.cache_clear()

    def test_resolve_stock_symbol_exact_code(self) -> None:
        with mock.patch.object(query_akshare, "call_akshare", return_value=pd.DataFrame([{"code": "000001", "name": "平安银行"}, {"code": "600519", "name": "贵州茅台"}])):
            resolved = query_akshare.resolve_stock_symbol("000001")
        self.assertEqual(resolved.code, "000001")
        self.assertEqual(resolved.name, "平安银行")

    def test_resolve_index_symbol_returns_ambiguous_candidates(self) -> None:
        fake = pd.DataFrame([{"代码": "000300", "名称": "沪深300", "市场分组": "沪深重要指数"}, {"代码": "399300", "名称": "深证300", "市场分组": "深证系列指数"}])
        with mock.patch.object(query_akshare, "get_index_catalog", return_value=fake):
            with self.assertRaises(query_akshare.SkillError) as ctx:
                query_akshare.resolve_index_symbol("300")
        self.assertEqual(ctx.exception.error_type, "ambiguous_symbol")
        self.assertEqual(len(ctx.exception.details["candidates"]), 2)

    def test_resolve_fund_symbol_exact_name(self) -> None:
        fake = pd.DataFrame([{"基金代码": "000001", "基金简称": "华夏成长混合", "基金类型": "混合型"}, {"基金代码": "000002", "基金简称": "华夏成长混合(后端)", "基金类型": "混合型"}])
        with mock.patch.object(query_akshare, "get_fund_catalog", return_value=fake):
            resolved = query_akshare.resolve_fund_symbol("华夏成长混合")
        self.assertEqual(resolved.code, "000001")
        self.assertEqual(resolved.extra["基金类型"], "混合型")

    def test_validate_compact_date_rejects_invalid_value(self) -> None:
        with self.assertRaises(query_akshare.SkillError) as ctx:
            query_akshare.validate_compact_date("2026-03-13", "date")
        self.assertEqual(ctx.exception.error_type, "invalid_argument")

    def test_dataframe_to_rows_normalizes_nan_and_dates(self) -> None:
        rows = query_akshare.dataframe_to_rows(pd.DataFrame([{"日期": pd.Timestamp("2026-03-13"), "值": 1.5, "空值": float("nan")}]))
        self.assertEqual(rows, [{"日期": "2026-03-13T00:00:00", "值": 1.5, "空值": None}])

    def test_missing_dependency_error_is_emitted(self) -> None:
        error = query_akshare.SkillError("missing_dependency", "Python package 'akshare' is not installed.", {"install": "python -m pip install akshare --upgrade"})
        with mock.patch.object(query_akshare, "load_akshare_module", side_effect=error):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = query_akshare.main(["market-overview"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["type"], "missing_dependency")


if __name__ == "__main__":
    unittest.main()
