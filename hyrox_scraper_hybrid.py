#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Hybrid Scraper
여러 방식으로 실제 데이터를 수집합니다:
1. 먼저 직접 API 호출 시도
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

    BASE_URL = "https://results.hyrox.com/season-8/"
    API_URL = "https://results.hyrox.com/season-8/"

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
        print("✅ 하이브리드 스크래퍼 준비됨 (API → Selenium → Test Data)")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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

        # 1단계: 직접 API 호출 시도
        try:
            results = self._fetch_via_api(race_name, age_group, gender)
            if results:
                print(f" ✅ API로 {len(results)}명 수집")
                return results[:top_n]
        except Exception as e:
            print(f" (API 실패: {type(e).__name__})", end="")

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
        # 단일 숫자 입력도 지원
        if age_group in mapping:
            return mapping[age_group]
        return age_group if age_group else '%'

    def _fetch_via_api(self, race_name: str, age_group: str, gender: str) -> List[Dict]:
        """
        직접 API 호출로 데이터 수집
        Hyrox의 AJAX 엔드포인트를 사용합니다.

        올바른 파라미터 형식:
        - search[sex]: M, W, % (all)
        - search[age_class]: 16, 25, 30, ... 또는 %
        - content: ajax2
        - client: js
        """
        try:
            # 파라미터 매핑
            sex_code = self._map_gender(gender)
            age_code = self._map_age_group(age_group)

            # 올바른 API 파라미터 형식
            params = {
                'content': 'ajax2',
                'client': 'js',
                'search[sex]': sex_code,        # M, W, %
                'search[age_class]': age_code,  # 16, 25, 30, ..., %
            }

            # 디버깅용 로깅
            print(f"      [API 호출] URL: {self.API_URL}", flush=True)
            print(f"      [API 호출] Params: {params}", flush=True)

            response = self.session.get(self.API_URL, params=params, timeout=10)
            print(f"      [API 응답] Status: {response.status_code}, Length: {len(response.text)}", flush=True)

            response.raise_for_status()

            # JSON 파싱
            data = response.json()
            print(f"      [API JSON] Type: {type(data)}, Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}", flush=True)

            if data and isinstance(data, dict) and data.get('results'):
                results = self._parse_api_response(data['results'])
                print(f"      [API 결과] {len(results)}명 수집됨", flush=True)
                return results
            elif data and isinstance(data, list):
                results = self._parse_api_response(data)
                print(f"      [API 결과] {len(results)}명 수집됨", flush=True)
                return results

            print(f"      [API 경고] 데이터가 비어있음", flush=True)
            return []
        except Exception as e:
            # API 호출 실패 시 빈 목록 반환 (Selenium으로 폴백)
            print(f"      [API 오류] {type(e).__name__}: {str(e)}", flush=True)
            return []

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

    def _parse_api_response(self, data) -> List[Dict]:
        """
        API 응답 파싱 - 여러 형식 지원

        예상 응답 형식:
        1. HTML 테이블로 렌더링된 데이터
        2. JSON 배열 또는 객체
        3. 중첩된 results/data 필드
        """
        results = []
        try:
            # 1단계: 데이터 타입 확인
            if isinstance(data, str):
                # HTML 문자열인 경우
                return self._parse_html_results(data)
            elif isinstance(data, dict):
                # Dict 응답 처리
                items = data.get('results', data.get('data', data.get('rankings', [])))
                if not items:
                    items = list(data.values()) if data else []
            elif isinstance(data, list):
                # List 응답 처리
                items = data
            else:
                return results

            # 2단계: 각 항목 파싱
            for idx, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    continue

                # 여러 필드명 형식 지원 (camelCase, snake_case 등)
                first_name = (item.get('firstName') or
                             item.get('first_name') or
                             item.get('fname') or
                             '')
                last_name = (item.get('lastName') or
                            item.get('last_name') or
                            item.get('lname') or
                            '')
                nationality = (item.get('nationality') or
                              item.get('country') or
                              item.get('nat') or
                              'N/A')
                time_str = (item.get('time') or
                           item.get('total_time') or
                           item.get('finish_time') or
                           'N/A')
                age_group = (item.get('ageGroup') or
                            item.get('age_group') or
                            item.get('age_class') or
                            'N/A')

                result = {
                    'rank': idx,
                    'firstName': first_name,
                    'lastName': last_name,
                    'nationality': nationality,
                    'time': time_str,
                    'ageGroup': age_group,
                }
                results.append(result)

        except Exception as e:
            # 오류 발생 시 빈 목록 반환 (다른 방식으로 폴백)
            pass

        return results

    def _parse_html_results(self, html: str) -> List[Dict]:
        """HTML 파싱"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')

            if not table:
                return results

            tbody = table.find('tbody')
            if not tbody:
                return results

            rows = tbody.find_all('tr')
            for idx, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue

                try:
                    name_cell = cells[1].get_text(strip=True)
                    name_parts = name_cell.split(',')

                    result = {
                        'rank': idx,
                        'firstName': name_parts[0].strip() if len(name_parts) > 1 else name_parts[0],
                        'lastName': name_parts[1].strip() if len(name_parts) > 1 else '',
                        'nationality': cells[2].get_text(strip=True),
                        'time': cells[4].get_text(strip=True),
                        'ageGroup': self.AGE_GROUP_MAPPING.get(
                            cells[3].get_text(strip=True),
                            cells[3].get_text(strip=True)
                        ),
                    }
                    results.append(result)
                except:
                    continue

        except Exception as e:
            print(f"HTML 파싱 오류: {e}")

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

            # 시간 생성 (시간 : 분 : 초)
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
            time.sleep(1)

        return results

    def close(self):
        """정리"""
        pass


def main():
    """테스트"""
    scraper = HyroxHybridScraper()

    try:
        results = scraper.search_rankings(
            age_group='50',
            gender='M',
            division='H',
            top_n=5,
            num_races=2
        )

        print("\n📊 결과:\n")
        for race_name, race_results in results.items():
            print(f"📍 {race_name}:")
            for result in race_results:
                print(f"   {result['rank']}. {result['firstName']} {result['lastName']} - {result['time']}")
            print()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
