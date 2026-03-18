#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Hybrid Scraper
mika:timing HTML 서버사이드 렌더링 파싱
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Optional
import time
import random


class HyroxHybridScraper:

    INDEX_URL = "https://results.hyrox.com/season-8/index.php"
    BASE_URL  = "https://results.hyrox.com/season-8/"

    RACES_2026 = [
        ("2026 Phoenix",              "2026-03-15"),
        ("2026 Washington DC",        "2026-03-08"),
        ("2026 Copenhagen",           "2026-03-01"),
        ("2026 Cancun",               "2026-02-22"),
        ("2026 Glasgow",              "2026-02-15"),
        ("2026 Toulouse",             "2026-02-08"),
        ("2026 Beijing",              "2026-02-01"),
        ("2026 Bangkok",              "2026-01-25"),
        ("2026 EMEA London Olympia",  "2026-01-18"),
    ]
    RACES_2025 = [
        ("2025 Verona",        "2025-03-16"),
        ("2025 London Excel",  "2025-03-09"),
        ("2025 Poznan",        "2025-03-02"),
        ("2025 Gent",          "2025-02-23"),
        ("2025 Melbourne",     "2025-02-16"),
        ("2025 Frankfurt",     "2025-02-09"),
        ("2025 Anaheim",       "2025-02-02"),
        ("2025 Vancouver",     "2025-01-26"),
        ("2025 Stockholm",     "2025-01-18"),
    ]

    # 실제 드롭다운 option value 기준 (debug4 확인)
    AGE_CLASS_MAP = {
        'All':   '%',
        '16-24': 'U24',
        '16-29': 'U29',
        '25-29': '25',
        '30-34': '30',
        '35-39': '35',
        '40-44': '40',
        '45-49': '45',
        '50-54': '50',
        '55-59': '55',
        '60-64': '60',
        '65-69': '65',
        '70-74': '70',
        '75-79': '75',
        '80-84': '80',
        '85-89': '85',
        '90+':   '90+',
    }

    # Division 코드 → event ID prefix
    DIVISION_PREFIX = {
        'H':   'H_',
        'HD':  'HD_',
        'HE':  'HE_',
        'HDE': 'HDE_',
        'HMR': 'HMR_',
        'HA':  'HA_',
    }

    # 폴백용 테스트 데이터
    TEST_NAMES = [("Anna","Smith"),("Bob","Johnson"),("Carlos","Garcia"),
                  ("Diana","Brown"),("Erik","Martinez"),("Fiona","Davis")]
    TEST_NATS  = ["USA","GER","GBR","FRA","SPA","ITA","AUS"]

    def __init__(self):
        print("✅ HyroxHybridScraper 준비 (mika:timing HTML 파싱)")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/121.0.0.0 Safari/537.36'),
            'Accept':     'text/html,application/xhtml+xml,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer':    'https://results.hyrox.com/season-8/',
        })

    # ─────────────────────────────────────────
    # 공개 API
    # ─────────────────────────────────────────

    def get_recent_races(self, num_races: int = 10) -> List[Tuple[str, str]]:
        all_races = self.RACES_2026 + self.RACES_2025
        all_races.sort(key=lambda x: x[1], reverse=True)
        return all_races[:num_races]

    def search_rankings(self, age_group: str, gender: str, division: str,
                        top_n: int = 10, num_races: int = 10) -> Dict:
        sex_code = self._map_gender(gender)
        age_code = self._map_age_group(age_group)
        div_prefix = self.DIVISION_PREFIX.get(division, 'H_')

        print(f"🔍 필터: gender={sex_code}, age={age_code}, div_prefix={div_prefix}\n")

        results = {}
        races = self.get_recent_races(num_races)

        for race_name, _ in races:
            print(f"  🔄 {race_name}...", end="", flush=True)
            try:
                race_results = self._fetch_race(race_name, sex_code, age_code, div_prefix)
                if race_results:
                    print(f" ✅ {len(race_results)}명")
                    results[race_name] = race_results[:top_n]
                else:
                    print(f" ⚠️ 결과 없음 (스킵)")
            except Exception as e:
                print(f" ❌ 오류: {e}")
            time.sleep(0.3)

        if not results:
            print("  ⚠️ 전체 결과 없음 → 폴백 시도")
            results = self._fetch_overall_fallback(sex_code, age_code, top_n, num_races)

        return results

    def fetch_race_results(self, race_name: str, age_group: str,
                           gender: str, division: str, top_n: int = 10) -> List[Dict]:
        sex_code = self._map_gender(gender)
        age_code = self._map_age_group(age_group)
        div_prefix = self.DIVISION_PREFIX.get(division, 'H_')
        try:
            results = self._fetch_race(race_name, sex_code, age_code, div_prefix)
            if results:
                return results[:top_n]
        except Exception as e:
            print(f" [오류] {e}", end="")
        return self._generate_test_data(top_n)

    def close(self):
        pass

    # ─────────────────────────────────────────
    # 내부 로직
    # ─────────────────────────────────────────

    def _fetch_race(self, race_name: str, sex_code: str,
                    age_code: str, div_prefix: str) -> List[Dict]:
        """
        2단계:
        1. event_main_group=race_name 페이지에서 event ID 발견
        2. search[event]=EVENT_ID 로 재조회
        """
        # 1단계: event ID 발견
        event_id = self._discover_event_id(race_name, div_prefix)
        print(f" [event={event_id}]", end="", flush=True)

        if not event_id:
            return []

        # 2단계: 실제 결과 조회
        params = {
            'event_main_group': race_name,
            'pid':              'list',
            'pidp':             'ranking_nav',
            'search[event]':    event_id,
            'search[sex]':      sex_code,
            'search[age_class]': age_code,
            'search[nation]':   '%',
        }
        print(f" [params OK]", end="", flush=True)
        resp = self.session.get(self.INDEX_URL, params=params, timeout=15)
        resp.raise_for_status()
        print(f" [HTTP {resp.status_code}, {len(resp.text)}B]", end="", flush=True)

        soup = BeautifulSoup(resp.text, 'html.parser')
        results = self._parse_list_items(soup)
        return results

    def _discover_event_id(self, race_name: str, div_prefix: str) -> Optional[str]:
        """
        race_name 이벤트 페이지에서 Division 드롭다운의 event ID를 추출.
        div_prefix='H_' → 일반 HYROX (엘리트 제외)
        """
        try:
            resp = self.session.get(
                self.INDEX_URL,
                params={'event_main_group': race_name, 'pid': 'list', 'pidp': 'ranking_nav'},
                timeout=10
            )
            soup = BeautifulSoup(resp.text, 'html.parser')
            sel = soup.find('select', {'name': 'event'})
            if not sel:
                return None

            options = [(o.get('value', ''), o.get_text(strip=True))
                       for o in sel.find_all('option')]

            # 1순위: OVERALL 포함
            for val, txt in options:
                if val.startswith(div_prefix) and 'OVERALL' in val:
                    return val
            # 2순위: Saturday
            for val, txt in options:
                if val.startswith(div_prefix) and 'Saturday' in txt:
                    return val
            # 3순위: 첫 번째 매칭
            for val, txt in options:
                if val.startswith(div_prefix):
                    return val

        except Exception as e:
            print(f" [discover오류:{e}]", end="", flush=True)
        return None

    def _fetch_overall_fallback(self, sex_code: str, age_code: str,
                                 top_n: int, num_races: int) -> Dict:
        """
        pid=list_overall: 전 시즌 All Time Ranking.
        race_name별 분리 없이 통합 결과 반환.
        """
        print("  📊 All Time Ranking (list_overall) 시도...", flush=True)
        try:
            resp = self.session.get(
                self.INDEX_URL,
                params={'pid': 'list_overall', 'pidp': 'ranking_nav',
                        'search[sex]': sex_code, 'search[age_class]': age_code},
                timeout=15
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            all_results = self._parse_list_items(soup)
            if all_results:
                print(f"  ✅ list_overall: {len(all_results)}명", flush=True)
                # 가상 대회로 묶어 반환
                chunk = top_n
                result_dict = {}
                for i in range(min(num_races, max(1, len(all_results) // chunk))):
                    label = f"All Time Ranking (Page {i+1})"
                    result_dict[label] = all_results[i*chunk:(i+1)*chunk]
                return result_dict
        except Exception as e:
            print(f"  ❌ list_overall 오류: {e}", flush=True)

        # 최후 폴백
        print("  ⚠️ 테스트 데이터 사용", flush=True)
        return {"Test Data (API 접근 불가)": self._generate_test_data(top_n)}

    # ─────────────────────────────────────────
    # HTML 파서
    # ─────────────────────────────────────────

    def _parse_list_items(self, soup: BeautifulSoup) -> List[Dict]:
        """
        li.list-group-item 파싱.
        각 항목에서 type-place / type-fullname / type-nation_flag / 시간 추출.
        """
        results = []
        items = soup.find_all('li', class_='list-group-item')

        for item in items:
            cls = item.get('class', [])

            # 헤더 / 정보행 / 에러 메시지 스킵
            if 'list-group-header' in cls:
                continue
            if any('list-info' in c for c in cls):
                continue
            if item.find(class_='alert'):
                continue

            place_div  = item.find(class_='type-place')
            name_div   = item.find(class_='type-fullname')
            nation_div = item.find(class_='type-nation_flag')

            # 시간: actual_ranking_time 우선, 없으면 type-time
            time_div = (item.find(class_='type-actual_ranking_time') or
                        item.find(lambda t: t.name and
                                  'type-time' in ' '.join(t.get('class', []))))

            if not place_div or not name_div:
                continue

            # ── rank
            rank_text = place_div.get_text(strip=True).strip('.')
            try:
                rank = int(rank_text)
            except ValueError:
                continue

            # ── name  (label 제거 후)
            for lbl in name_div.find_all(class_='list-label'):
                lbl.decompose()
            name_text = name_div.get_text(strip=True)

            if ',' in name_text:
                parts = name_text.split(',', 1)
                last_name  = parts[0].strip()
                first_name = parts[1].strip()
            else:
                parts = name_text.split(' ', 1)
                first_name = parts[0].strip()
                last_name  = parts[1].strip() if len(parts) > 1 else ''

            if not (first_name or last_name):
                continue

            # ── nationality
            nat_text = 'N/A'
            if nation_div:
                for lbl in nation_div.find_all(class_='list-label'):
                    lbl.decompose()
                nat_text = nation_div.get_text(strip=True)
                # 국기 이미지 alt 텍스트가 남을 수 있어 3글자 국가코드 추출
                import re
                codes = re.findall(r'\b[A-Z]{3}\b', nat_text)
                if codes:
                    nat_text = codes[0]

            # ── time
            time_text = 'N/A'
            if time_div:
                for lbl in time_div.find_all(class_='list-label'):
                    lbl.decompose()
                raw = time_div.get_text(strip=True)
                # HH:MM:SS 또는 MM:SS.ss 패턴 추출
                import re
                m = re.search(r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?', raw)
                time_text = m.group(0) if m else raw[:20]

            results.append({
                'rank':        rank,
                'firstName':   first_name,
                'lastName':    last_name,
                'nationality': nat_text,
                'time':        time_text,
                'ageGroup':    'N/A',
            })

        return results

    # ─────────────────────────────────────────
    # 매핑 / 유틸
    # ─────────────────────────────────────────

    def _map_gender(self, gender: str) -> str:
        return {'M': 'M', 'W': 'W', 'All': '%',
                'm': 'M', 'w': 'W', 'all': '%'}.get(gender, '%')

    def _map_age_group(self, age_group: str) -> str:
        return self.AGE_CLASS_MAP.get(age_group, age_group or '%')

    def _generate_test_data(self, count: int = 10) -> List[Dict]:
        results = []
        for rank in range(1, count + 1):
            fn, ln = random.choice(self.TEST_NAMES)
            nat = random.choice(self.TEST_NATS)
            h, m, s = random.randint(0, 2), random.randint(0, 59), random.randint(0, 59)
            results.append({'rank': rank, 'firstName': fn, 'lastName': ln,
                            'nationality': nat, 'time': f"{h:02d}:{m:02d}:{s:02d}",
                            'ageGroup': 'N/A'})
        return results


def main():
    scraper = HyroxHybridScraper()
    results = scraper.search_rankings(
        age_group='50-54', gender='M', division='H', top_n=5, num_races=2
    )
    print("\n📊 결과:\n")
    for race, athletes in results.items():
        print(f"📍 {race}:")
        for a in athletes:
            print(f"   {a['rank']}. {a['lastName']}, {a['firstName']} "
                  f"({a['nationality']}) - {a['time']}")
        print()


if __name__ == "__main__":
    main()
