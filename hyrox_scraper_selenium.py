#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Selenium Scraper
Hyrox 웹사이트에서 실제 데이터를 수집합니다.
JavaScript 렌더링 후 BeautifulSoup으로 파싱합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Tuple
import os

class HyroxSeleniumScraper:
    """Selenium을 사용해서 Hyrox 웹사이트에서 실제 데이터를 수집"""

    BASE_URL = "https://results.hyrox.com/season-8/"
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

    def __init__(self):
        """Selenium 드라이버 초기화"""
        try:
            # Chrome 옵션 설정
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 백그라운드 실행
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Selenium 드라이버 초기화 완료")
        except Exception as e:
            print(f"⚠️  Selenium 드라이버 초기화 실패: {e}")
            self.driver = None

    def get_recent_races(self, num_races: int = 10) -> List[Tuple[str, str]]:
        """최근 대회 목록"""
        all_races = self.RACES_2026 + self.RACES_2025
        all_races.sort(key=lambda x: x[1], reverse=True)
        return all_races[:num_races]

    def fetch_race_results(self, race_name: str, age_group: str,
                          gender: str, division: str, top_n: int = 10) -> List[Dict]:
        """
        특정 대회의 필터링된 결과 가져오기

        Args:
            race_name: 대회명
            age_group: 나이 그룹 코드 (예: '50')
            gender: 성별 코드 (M/W)
            division: 카테고리 코드 (H/HD/HE 등)
            top_n: 상위 N명

        Returns:
            선수 정보 리스트
        """
        if self.driver is None:
            return []

        try:
            print(f"  🔄 {race_name} 데이터 로드 중...", end="", flush=True)

            # 페이지 로드
            self.driver.get(self.BASE_URL)
            time.sleep(2)

            # Race 필터: 대회명으로 선택
            try:
                race_select = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select"))
                )
                Select(race_select).select_by_visible_text(race_name)
                time.sleep(1)
            except Exception as e:
                print(f" (Race 필터 실패: {e})")
                return []

            # Age Group 필터 선택
            try:
                age_selects = self.driver.find_elements(By.CSS_SELECTOR, "select")
                if len(age_selects) >= 4:  # Age Group은 보통 4번째 select
                    age_label = self.AGE_GROUP_MAPPING.get(age_group, age_group)
                    Select(age_selects[3]).select_by_visible_text(age_label)
                    time.sleep(1)
            except Exception as e:
                print(f" (Age Group 필터 실패: {e})")
                pass

            # Gender 필터 선택
            try:
                gender_selects = self.driver.find_elements(By.CSS_SELECTOR, "select")
                if len(gender_selects) >= 3:  # Gender는 보통 3번째
                    gender_text = 'Men' if gender == 'M' else 'Women'
                    Select(gender_selects[2]).select_by_visible_text(gender_text)
                    time.sleep(1)
            except Exception as e:
                print(f" (Gender 필터 실패: {e})")
                pass

            time.sleep(2)

            # HTML 파싱
            html = self.driver.page_source
            results = self._parse_results_table(html, race_name)

            print(f" ✅ {len(results)}명")
            return results[:top_n]

        except Exception as e:
            print(f" ❌ 오류: {e}")
            return []

    def _parse_results_table(self, html: str, race_name: str) -> List[Dict]:
        """HTML에서 결과 테이블 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []

            # 테이블 찾기
            table = soup.find('table')
            if not table:
                return results

            tbody = table.find('tbody')
            if not tbody:
                return results

            # 각 행 파싱
            rows = tbody.find_all('tr')
            for idx, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue

                try:
                    # 데이터 추출
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
                except Exception as e:
                    continue

            return results
        except Exception as e:
            print(f"파싱 오류: {e}")
            return []

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
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Selenium 드라이버 종료")


def main():
    """테스트"""
    scraper = HyroxSeleniumScraper()

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
