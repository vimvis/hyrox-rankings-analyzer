#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Hybrid Scraper
여러 방식으로 실제 데이터를 수집합니다:
1. 먼저 직접 HTML 페이지 파싱 시도
2. Selenium 사용 시도
3. 마지막으로 테스트 데이터 폴백
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import time
import random


class HyroxHybridScraper:
    """여러 방식으로 Hyrox 데이터를 수집하는 하이브리드 스크래퍼"""

    # 올바른 URL: index.php 필요
    BASE_URL = "https://results.hyrox.com/season-8/"
    INDEX_URL = "https://results.hyrox.com/season-8/index.php"

    RACES_2025 = [
        ("2025 Stockholm", "2025-01-18"),
        ("2025 Shenzhen", "2025-01-19"),
        ("2025 Vancouver", "2025-01-26"),
        ("2025 Anaheim", "2025-02-02"),
        ("2025 Frankfurt", "2025-02-09"),
        ("2025 Melbourne", "2025-02-16"),
        ("2025 Gent", "2025-02-23"),
        ("2025 Poznan", "2025-03-02"),
        ("2025 London Excel", "2025-03-09"),
        ("2025 Verona", "2025-03-16"),
    ]

    RACES_2026 = [
        ("2026 EMEA London Olympia", "2026-01-18"),
        ("2026 Bangkok", "2026-01-25"),
        ("2026 Beijing", "2026-02-01"),
        ("2026 Toulouse", "2026-02-08"),
        ("2026 Glasgow", "2026-02-15"),
        ("2026 Cancun", "2026-02-22"),
        ("2026 Copenhagen", "2026-03-01"),
        ("2026 Washington DC", "2026-03-08"),
        ("2026 Phoenix", "2026-03-15"),
    ]

    AGE_GROUP_MAPPING = {
        'U24': '16-24',
        '25': '25-29',
        '30': '30-34',
        'X30': '30-39',
        '35': '35-39',
        '40': '40-44',
        'X40': '40-49',
        '45': '45-49',
        '50': '50-54',
        'X50': '50-59',
        '55': '55-59',
        '60': '60-64',
        '65': '65-69',
        '70': '70-74',
        '75': '75-79',
    }

    # 테스트 데이터용 샘플
    TEST_FIRST_NAMES = ["Anna", "Bob", "Carlos", "Diana", "Erik", "Fiona", "Gustav", "Hannah",
                        "Ivan", "Julia", "Klaus", "Laura", "Marco", "Nora", "Oscar", "Paula"]
    TEST_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                       "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                       "Wilson", "Anderson", "Thomas"]
    TEST_NATIONALITIES = ["USA", "GER", "GBR", "FRA", "SPA", "ITA", "AUS", "CAN", "NED",
                         "SWE", "NOR", "CHE", "AUT", "BEL", "KOR", "JPN"]

    def __init__(self):
        """초기화"""
        print("✅ 하이브리드 스크래퍼 준비됨 (HTML → Selenium → Test Data)")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://results.hyrox.com/season-8/',
        })

    def get_recent_races(self, num_races: int = 10) -> List[Tuple[str, str]]:
        """최근 대회 목록"""
        all_races = self.RACES_2026 + self.RACES_2025
        all_races.sort(key=lambda x: x[1], reverse=True)
        return all_races[:num_races]

    def fetch_race_results(self, race_name: str, age_group: str,
                          gender: str, division: str, top_n: int = 10) -> List[Dict]:
        """
        여러 방식으로 데이터 수집 시도
        """
        print(f"  🔄 {race_name} 데이터 로드 중...", end="", flush=True)

        # 1단계: 직접 HTML 페이지 파싱 시도
        try:
            results = self._fetch_via_html(race_name, age_group, gender)
            if results:
                print(f" ✅ HTML로 {len(results)}명 수집")
                return results[:top_n]
            else:
                print(f" (HTML: 결과 없음)", end="")
        except Exception as e:
            print(f" (HTML 실패: {type(e).__name__}: {str(e)[:60]})", end="")

        # 2단계: Selenium 시도
        try:
            results = self._fetch_via_selenium(race_name, age_group, gender)
            if results:
                print(f" → Selenium으로 {len(results)}명 수집")
                return results[:top_n]
        except Exception as e:
            print(f" (Selenium 실패: {type(e).__name__})", end="")

        # 3단계: 테스트 데이터 폴백
        print(f" → Test Data 사용")
        results = self._generate_test_data(top_n)
        return results

    def _map_gender(self, gender: str) -> str:
        """성별 코드 매핑: M/W/All → M/W/%"""
        mapping = {
            'M': 'M',
            'W': 'W',
            'All': '%',
            'm': 'M',
            'w': 'W',
            'all': '%',
        }
        return mapping.get(gender, '%')

    def _map_age_group(self, age_group: str) -> str:
        """나이 그룹 코드 매핑: 50-54 → 50"""
        mapping = {
            'All': '%',
            '16-24': '16',
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
        }
        if age_group in mapping:
            return mapping[age_group]
        return age_group if age_group else '%'

    def _fetch_via_html(self, race_name: str, age_group: str, gender: str) -> List[Dict]:
        """
        직접 HTML 페이지 파싱으로 데이터 수집

        올바른 URL 구조:
        https://results.hyrox.com/season-8/index.php
            ?event_main_group=2026+Washington+DC
            &pid=list
            &pidp=ranking_nav
            &search[sex]=M
            &search[age_class]=50
            &search[nation]=%

        또는 전체 랭킹:
        https://results.hyrox.com/season-8/index.php
            ?pid=list_overall
            &pidp=ranking_nav
            &search[sex]=M
            &search[age_class]=50
        """
        sex_code = self._map_gender(gender)
        age_code = self._map_age_group(age_group)

        # race_name을 URL 파라미터로 변환
        # "2026 Washington DC" → "2026 Washington DC" (공백 유지, requests가 인코딩)
        event_group = race_name

        # 전략 1: 특정 이벤트 결과 페이지
        params_event = {
            'event_main_group': event_group,
            'pid': 'list',
            'pidp': 'ranking_nav',
            'search[sex]': sex_code,
            'search[age_class]': age_code,
            'search[nation]': '%',
        }

        print(f"\n      [HTML 호출] URL: {self.INDEX_URL}", flush=True)
        print(f"      [HTML 호출] Params: {params_event}", flush=True)

        response = self.session.get(self.INDEX_URL, params=params_event, timeout=15)
        print(f"      [HTML 응답] Status: {response.status_code}, Length: {len(response.text)}", flush=True)
        print(f"      [HTML 응답] Content-Type: {response.headers.get('Content-Type', 'N/A')}", flush=True)

        response.raise_for_status()

        # HTML 파싱
        results = self._parse_html_results(response.text)
        print(f"      [HTML 결과] {len(results)}명 파싱됨", flush=True)

        # 전략 1 실패 시 전체 랭킹으로 폴백
        if not results:
            print(f"      [HTML 전략2] 전체 랭킹으로 재시도...", flush=True)
            params_overall = {
                'pid': 'list_overall',
                'pidp': 'ranking_nav',
                'search[sex]': sex_code,
                'search[age_class]': age_code,
            }
            response2 = self.session.get(self.INDEX_URL, params=params_overall, timeout=15)
            print(f"      [HTML 전략2] Status: {response2.status_code}, Length: {len(response2.text)}", flush=True)
            response2.raise_for_status()
            results = self._parse_html_results(response2.text)
            print(f"      [HTML 전략2] {len(results)}명 파싱됨", flush=True)

        return results

    def _fetch_via_selenium(self, race_name: str, age_group: str, gender: str) -> List[Dict]:
        """
        Selenium으로 JavaScript 렌더링된 페이지 파싱
        로컬 개발용 (Vercel에서는 작동 안 함)
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait, Select
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            raise ImportError("Selenium이 설치되지 않았습니다")

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(self.BASE_URL)
            time.sleep(2)

            # Race 필터
            try:
                selects = driver.find_elements(By.CSS_SELECTOR, "select")
                if selects:
                    Select(selects[0]).select_by_visible_text(race_name)
                    time.sleep(1)
            except:
                pass

            # Age Group 필터
            try:
                selects = driver.find_elements(By.CSS_SELECTOR, "select")
                if len(selects) >= 4:
                    age_label = self.AGE_GROUP_MAPPING.get(age_group, age_group)
                    Select(selects[3]).select_by_visible_text(age_label)
                    time.sleep(1)
            except:
                pass

            # Gender 필터
            try:
                selects = driver.find_elements(By.CSS_SELECTOR, "select")
                if len(selects) >= 3:
                    gender_text = 'Men' if gender == 'M' else 'Women'
                    Select(selects[2]).select_by_visible_text(gender_text)
                    time.sleep(1)
            except:
                pass

            time.sleep(2)

            # HTML 파싱
            html = driver.page_source
            return self._parse_html_results(html)

        finally:
            if driver:
                driver.quit()

    def _parse_html_results(self, html: str) -> List[Dict]:
        """
        mika:timing HTML 테이블 파싱

        예상 테이블 구조:
        - Col 0: Rank
        - Col 1: Name (Last, First 형식)
        - Col 2: Nationality
        - Col 3: Age Class
        - Col 4: City (옵션)
        - Col 5: Division (H, HD, HE 등)
        - Col 6: Finish Time
        """
        results = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # 디버깅: 페이지 내용 확인
            page_title = soup.find('title')
            print(f"      [HTML 파싱] 페이지 제목: {page_title.get_text() if page_title else 'N/A'}", flush=True)

            # 결과 테이블 찾기 (여러 선택자 시도)
            table = None
            selectors = [
                'table.results-list',
                'table.ranking-list',
                'table#resultTable',
                'table.list-table',
                'div.list-results table',
                'div#listContainer table',
                'table',  # 마지막 수단: 첫 번째 테이블
            ]

            for selector in selectors:
                table = soup.select_one(selector)
                if table:
                    print(f"      [HTML 파싱] 테이블 발견: '{selector}'", flush=True)
                    break

            if not table:
                print(f"      [HTML 파싱] 테이블 없음! Tables 수: {len(soup.find_all('table'))}", flush=True)
                # 테이블이 없으면 리스트 형태로 파싱 시도
                return self._parse_list_results(soup)

            # 헤더 파싱 (컬럼 순서 파악)
            headers = []
            thead = table.find('thead')
            if thead:
                header_cells = thead.find_all(['th', 'td'])
                headers = [h.get_text(strip=True).lower() for h in header_cells]
                print(f"      [HTML 파싱] 헤더: {headers}", flush=True)

            # 데이터 행 파싱
            tbody = table.find('tbody') or table
            rows = tbody.find_all('tr')
            print(f"      [HTML 파싱] 데이터 행 수: {len(rows)}", flush=True)

            for idx, row in enumerate(rows, 1):
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue

                try:
                    # 각 셀 텍스트 추출
                    cell_texts = [c.get_text(strip=True) for c in cells]

                    # 헤더 기반 파싱 (헤더가 있는 경우)
                    if headers and len(headers) == len(cell_texts):
                        result = self._parse_row_by_headers(headers, cell_texts, idx)
                    else:
                        # 위치 기반 파싱 (mika:timing 기본 구조)
                        result = self._parse_row_by_position(cell_texts, idx)

                    if result:
                        results.append(result)

                except Exception as e:
                    continue

            print(f"      [HTML 파싱] 최종 결과: {len(results)}명", flush=True)

        except Exception as e:
            print(f"      [HTML 파싱 오류] {type(e).__name__}: {str(e)}", flush=True)

        return results

    def _parse_row_by_headers(self, headers: List[str], cells: List[str], idx: int) -> Dict:
        """헤더 컬럼명 기반 행 파싱"""
        def find_col(keywords):
            for kw in keywords:
                for i, h in enumerate(headers):
                    if kw in h:
                        return cells[i] if i < len(cells) else ''
            return ''

        name_raw = find_col(['name', 'athlete', 'participant', 'competitor'])
        nat = find_col(['nat', 'country', 'nation'])
        time_val = find_col(['time', 'finish', 'result', 'total'])
        age = find_col(['age', 'class', 'category'])

        # 이름 분리 (Last, First 형식)
        if ',' in name_raw:
            parts = name_raw.split(',', 1)
            last_name = parts[0].strip()
            first_name = parts[1].strip()
        else:
            parts = name_raw.split(' ', 1)
            first_name = parts[0].strip()
            last_name = parts[1].strip() if len(parts) > 1 else ''

        if not (first_name or last_name):
            return None

        return {
            'rank': idx,
            'firstName': first_name,
            'lastName': last_name,
            'nationality': nat or 'N/A',
            'time': time_val or 'N/A',
            'ageGroup': age or 'N/A',
        }

    def _parse_row_by_position(self, cells: List[str], idx: int) -> Dict:
        """
        위치 기반 행 파싱 (mika:timing 기본 구조)

        mika:timing 기본 컬럼 순서:
        0: Rank
        1: Name (Last, First)
        2: Nationality / Country
        3: Age Class
        4: City (선택)
        5: Division (H, HD, etc.)
        6: Finish Time

        또는:
        0: Rank
        1: Name
        2: Country
        3: Finish Time
        """
        n = len(cells)
        if n < 3:
            return None

        # 첫 셀이 숫자면 순위 컬럼
        rank_offset = 0
        try:
            int(cells[0].replace('.', '').strip())
            rank_offset = 1
        except:
            pass

        name_raw = cells[rank_offset] if rank_offset < n else cells[0]

        # 이름 분리
        if ',' in name_raw:
            parts = name_raw.split(',', 1)
            last_name = parts[0].strip()
            first_name = parts[1].strip()
        else:
            parts = name_raw.split(' ', 1)
            first_name = parts[0].strip()
            last_name = parts[1].strip() if len(parts) > 1 else ''

        if not (first_name or last_name):
            return None

        # 국적 (rank_offset + 1)
        nat_col = rank_offset + 1
        nationality = cells[nat_col] if nat_col < n else 'N/A'

        # 시간 - 마지막 컬럼 또는 HH:MM:SS 패턴으로 찾기
        time_val = 'N/A'
        import re
        time_pattern = re.compile(r'\d{1,2}:\d{2}:\d{2}')
        for cell in reversed(cells):
            if time_pattern.match(cell.strip()):
                time_val = cell.strip()
                break

        # Age group
        age_col = rank_offset + 2
        age_group = cells[age_col] if age_col < n else 'N/A'

        return {
            'rank': idx,
            'firstName': first_name,
            'lastName': last_name,
            'nationality': nationality,
            'time': time_val,
            'ageGroup': age_group,
        }

    def _parse_list_results(self, soup) -> List[Dict]:
        """테이블 없을 때 리스트/div 기반 파싱"""
        results = []

        # div 기반 결과 목록 시도
        list_items = soup.select('.list-group-item, .result-item, .athlete-row, [class*="result"]')
        print(f"      [리스트 파싱] 항목 수: {len(list_items)}", flush=True)

        for idx, item in enumerate(list_items[:50], 1):
            text = item.get_text(separator=' ', strip=True)
            if not text:
                continue
            results.append({
                'rank': idx,
                'firstName': text[:30],
                'lastName': '',
                'nationality': 'N/A',
                'time': 'N/A',
                'ageGroup': 'N/A',
            })

        return results

    def _generate_test_data(self, count: int = 10) -> List[Dict]:
        """
        테스트 데이터 생성 (최후의 폴백)
        실제 데이터를 불러올 수 없을 때만 사용됩니다
        """
        results = []
        for rank in range(1, count + 1):
            first_name = random.choice(self.TEST_FIRST_NAMES)
            last_name = random.choice(self.TEST_LAST_NAMES)
            nationality = random.choice(self.TEST_NATIONALITIES)

            hours = random.randint(0, 2)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            result = {
                'rank': rank,
                'firstName': first_name,
                'lastName': last_name,
                'nationality': nationality,
                'time': time_str,
                'ageGroup': '50-54',
            }
            results.append(result)

        return results

    def search_rankings(self, age_group: str, gender: str, division: str,
                       top_n: int = 10, num_races: int = 10) -> Dict:
        """종합 검색 수행"""
        results = {}
        races = self.get_recent_races(num_races)

        print(f"🔍 {len(races)}개 대회에서 데이터 수집 중...\n")

        for race_name, race_date in races:
            race_results = self.fetch_race_results(
                race_name, age_group, gender, division, top_n
            )
            results[race_name] = race_results
            time.sleep(0.5)

        return results

    def close(self):
        """정리"""
        pass


def main():
    """테스트"""
    scraper = HyroxHybridScraper()

    try:
        results = scraper.search_rankings(
            age_group='50-54',
            gender='M',
            division='H',
            top_n=5,
            num_races=2
        )

        print("\n📊 결과:\n")
        for race_name, race_results in results.items():
            print(f"📍 {race_name}:")
            for result in race_results:
                print(f"   {result['rank']}. {result['firstName']} {result['lastName']} - {result['nationality']} - {result['time']}")
            print()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
