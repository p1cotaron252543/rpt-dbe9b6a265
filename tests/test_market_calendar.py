"""営業日の計算（祝日・年末年始に対応。2026-11-24承認の手計算ケース）。"""

from datetime import date

import pytest

from analysis.market_calendar import is_business_day, japanese_holidays, next_business_day


@pytest.mark.parametrize(
    "d, expected",
    [
        (date(2026, 11, 20), date(2026, 11, 24)),  # 金 → 火（11/21土・11/22日・11/23祝）
        (date(2026, 9, 18), date(2026, 9, 24)),    # 9/21敬老の日・9/22国民の休日・9/23秋分の日
        (date(2026, 5, 1), date(2026, 5, 7)),      # 5/4・5/5・5/6振替休日（5/3が日曜）
        (date(2026, 12, 30), date(2027, 1, 4)),    # 12/31〜1/3は休場
        (date(2026, 12, 29), date(2026, 12, 30)),  # 通常
        (date(2026, 11, 24), date(2026, 11, 25)),  # 通常（火→水）
    ],
)
def test_next_business_day(d, expected):
    assert next_business_day(d) == expected


def test_2026_national_holidays_list():
    h = japanese_holidays(2026)
    assert sorted(h) == [date(2026, m, d) for m, d in (
        (1, 1), (1, 12), (2, 11), (2, 23), (3, 20), (4, 29), (5, 3), (5, 4), (5, 5), (5, 6),
        (7, 20), (8, 11), (9, 21), (9, 22), (9, 23), (10, 12), (11, 3), (11, 23),
    )]
    assert h[date(2026, 5, 6)] == "振替休日" and h[date(2026, 9, 22)] == "国民の休日"


def test_is_business_day():
    assert is_business_day(date(2026, 11, 24)) and not is_business_day(date(2026, 11, 23))
    assert not is_business_day(date(2026, 11, 21)) and not is_business_day(date(2026, 12, 31))
    assert not is_business_day(date(2027, 1, 1)) and is_business_day(date(2027, 1, 4))
