"""営業日の計算（土日・日本の祝日・年末年始の休場を考慮。2026-11-24承認）。

日本の祝日（国民の祝日に関する法律）:
    元日1/1、成人の日（1月第2月曜）、建国記念の日2/11、天皇誕生日2/23、春分の日、昭和の日4/29、憲法記念日5/3、みどりの日5/4、
    こどもの日5/5、海の日（7月第3月曜）、山の日8/11、敬老の日（9月第3月曜）、秋分の日、スポーツの日（10月第2月曜）、
    文化の日11/3、勤労感謝の日11/23。
    振替休日: 日曜の祝日の次の、祝日でない最初の日。国民の休日: 前後が祝日の平日（日曜を除く）。
    春分の日・秋分の日は 1980〜2099年の近似式で求める。
取引所の休場: 上の祝日、土日、12/31・1/1〜1/3（年末年始）。
2021年の海の日・スポーツの日など、特例で移動した年（過去）は考慮しない（2026年以降の予想の用途）。
"""

from datetime import date, timedelta


def _nth_monday(year: int, month: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(0 - d.weekday()) % 7)  # 最初の月曜
    return d + timedelta(weeks=n - 1)


def _equinox(year: int, base: float) -> int:
    return int(base + 0.242194 * (year - 1980) - ((year - 1980) // 4))


def _base_holidays(year: int) -> dict[date, str]:
    h = {
        date(year, 1, 1): "元日",
        _nth_monday(year, 1, 2): "成人の日",
        date(year, 2, 11): "建国記念の日",
        date(year, 3, _equinox(year, 20.8431)): "春分の日",
        date(year, 4, 29): "昭和の日",
        date(year, 5, 3): "憲法記念日",
        date(year, 5, 4): "みどりの日",
        date(year, 5, 5): "こどもの日",
        _nth_monday(year, 7, 3): "海の日",
        date(year, 8, 11): "山の日",
        _nth_monday(year, 9, 3): "敬老の日",
        date(year, 9, _equinox(year, 23.2488)): "秋分の日",
        _nth_monday(year, 10, 2): "スポーツの日",
        date(year, 11, 3): "文化の日",
        date(year, 11, 23): "勤労感謝の日",
    }
    if year >= 2020:
        h[date(year, 2, 23)] = "天皇誕生日"
    return h


def japanese_holidays(year: int) -> dict[date, str]:
    """その年の祝日（振替休日・国民の休日を含む）。"""
    h = _base_holidays(year)
    # 国民の休日: 前後が祝日の平日（日曜を除く）
    for d in sorted(h):
        mid = d + timedelta(days=1)
        if mid not in h and (mid + timedelta(days=1)) in h and mid.weekday() != 6 and mid.weekday() != 5:
            h[mid] = "国民の休日"
    # 振替休日: 日曜の祝日の次の、祝日でない最初の日
    for d in sorted(list(h)):
        if d.weekday() == 6:
            sub = d + timedelta(days=1)
            while sub in h:
                sub += timedelta(days=1)
            h[sub] = "振替休日"
    return h


def is_market_holiday(d: date) -> bool:
    """土日以外の休場日（祝日・年末年始）。"""
    if (d.month, d.day) in ((12, 31), (1, 1), (1, 2), (1, 3)):
        return True
    return d in japanese_holidays(d.year)


def is_business_day(d: date) -> bool:
    return d.weekday() < 5 and not is_market_holiday(d)


def next_business_day(d: date) -> date:
    """土日・祝日・年末年始を飛ばした翌営業日。"""
    nxt = d + timedelta(days=1)
    while not is_business_day(nxt):
        nxt += timedelta(days=1)
    return nxt
