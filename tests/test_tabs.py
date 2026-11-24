"""予想と結果を分けるタブ表示（2026-11-24）のテスト。"""

import re
from datetime import date, datetime

from analysis.scoring import RankedCandidate
from report.build_site import build_index
from report.forecast_set import JST, evening_set
from report.generate_report import generate_report
from tracking.predictions_db import WinRateStats
from tracking.previous import PreviousItem, PreviousResults


def _cand(code, name, side):
    return RankedCandidate(code=code, name=name, total_score=3, technical_score=3, earnings_score=0, volume_ratio=1.8,
                           entry_price=995.0, reasons=["x"], side=side, day_close=1000.0, day_open=990, day_high=1010,
                           day_low=985, day_volume=1, daily_return=0.018)


def _page(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    st = WinRateStats(20, 12, 6, 0.5)
    prev = PreviousResults(date(2026, 11, 10), date(2026, 11, 11), [
        PreviousItem(1, "6954", "前日の結果銘柄", 995.0, "win", 0.01, 990, 1005, 0.0152, side="buy", pred_close=1000,
                     target_high=1010, target_low=985, limit_status="win")])
    fs = evening_set(date(2026, 11, 12), date(2026, 11, 13), datetime(2026, 11, 12, 16, 12, tzinfo=JST))
    text = generate_report(
        date(2026, 11, 12), date(2026, 11, 13), [_cand("1111", "本日の買い候補銘柄", "buy")], [_cand("2222", "本日の売り候補銘柄", "sell")],
        st, st, buy_previous=prev, forecast_set=fs,
        exp_buy_candidates=[_cand("3333", "テスト枠の買い銘柄", "buy")], exp_sell_candidates=[],
        exp_buy_stats=st, exp_sell_stats=st,
    )
    (reports / "2026-11-12.md").write_text(text, encoding="utf-8")
    return build_index(reports, tmp_path / "docs", "t").read_text(encoding="utf-8")


def _panel(page, name):
    m = re.search(rf'<div class="tab-panel[^"]*" data-tab="{name}" id="tab-{name}">(.*?)(?=<div class="tab-panel|<section class="glossary|<script)', page, re.S)
    assert m, name
    return m.group(1)


def test_three_tabs_and_default_forecast(tmp_path):
    page = _page(tmp_path)
    assert 'data-tab="forecast">今日の予想</button>' in page and 'data-tab="results">結果・成績</button>' in page
    assert 'data-tab="pnl"' not in page  # 損益のデータが無ければ、損益タブは出さない
    assert '<div class="tab-panel active" data-tab="forecast"' in page


def test_forecast_tab_has_only_candidates(tmp_path):
    f = _panel(_page(tmp_path), "forecast")
    assert "本日の買い候補銘柄" in f and "本日の売り候補銘柄" in f and "テスト枠の買い銘柄" in f
    assert "前日の結果銘柄" not in f and 'class="prev"' not in f   # 前営業日の結果は出ない
    assert 'class="stat-row"' not in f                              # 成績タイルも出ない（テスト枠の成績を含む）
    assert 'id="forecast-list"' in f and 'id="no-active"' in f


def test_results_tab_has_results_and_no_candidate_cards_in_latest_section(tmp_path):
    r = _panel(_page(tmp_path), "results")
    assert "ここに表示される銘柄は、過去の予想です" in r
    first = r.split('<section class="res-section expired-sets"')[0]
    assert "前日の結果銘柄" in first and 'class="stat-row"' in first
    assert "本日の買い候補銘柄" not in first and "本日の売り候補銘柄" not in first and "テスト枠の買い銘柄" not in first
    assert "テスト枠（値動き重視）の成績" in first               # テスト枠の成績は結果タブ
    assert 'id="expired-list"' in r and 'id="res-buy"' in r


def test_pnl_tab_appears_only_with_data(tmp_path):
    from tracking.trade_import import save_daily_pnl

    save_daily_pnl(tmp_path / "trades" / "daily_pnl.json", {"2026-11-10": {"pnl": 100, "trades": 1}})
    page = _page(tmp_path)
    assert 'data-tab="pnl">損益</button>' in page
    assert 'id="pnl-cal"' in _panel(page, "pnl")
