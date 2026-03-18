#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Playwright Scraper
Playwright을 사용해 Hyrox 웹사이트에서 실제 데이터를 수집합니다.
Vercel 서버리스 환경과 로컬 환경 모두에서 작동합니다.
"""

from playwright.async_api import async_playwright
import asyncio
import json
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import os

class HyroxPlaywrightScraper:
    """Playwright를 사용해서 Hyrox 웹사이트에서 실제 데이터를 수집"""

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
        """초기화"""
        print("✅ Playwright 스크래퍼 준비됨")
        self.browser = None
        self.context = None

    def get_recent_races(self, num_races: int = 10) -> List[Tuple[str, str]]:
        """최근 대회 목록"""
        all_races = self.RACES_2026 + self.RACES_2025
        all_races.sort(key=lambda x: x[1], reverse=True)
        return all_races[:num_races]

    async def fetch_race_results(self, race_name: str, age_group: str,
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
        page = None
        try:
            print(f"  🔄 {race_name} 데이터 로드 중...", end="", flush=True)

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # 페이지 로드
                await page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)

                # Race 필터: 대회명으로 선택
                try:
                    select = await page.query_selector("select")
                    if select:
                        await select.select_option(label=race_name)
                        await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f" (Race 필터 실패: {e})")
                    return []

                # Age Group 필터 선택
                try:
                    selects = await page.query_selector_all("select")
                    if len(selects) >= 4:
                        age_label = self.AGE_GROUP_MAPPING.get(age_group, age_group)
                        await selects[3].select_option(label=age_label)
                        await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f" (Age Group 필터 실패: {e})")

                # Gender 필터 선택
                try:
                    selects = await page.query_selector_all("select")
                    if len(selects) >= 3:
                        gender_text = 'Men' if gender == 'M' else 'Women'
                        await selects[2].select_option(label=gender_text)
                        await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f" (Gender 필터 실패: {e})")

                await page.wait_for_timeout(2000)

                # HTML 파싱
                html = await page.content()
                results = self._parse_results_table(html, race_name)

                print(f" ✅ {len(results)}명")
                await browser.close()
                return results[:top_n]

        except Exception as e:
            print(f" ❌ 오류: {e}")
            return []
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass

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

    async def search_rankings(self, age_group: str, gender: str, division: str,
                            top_n: int = 10, num_races: int = 10) -> Dict:
        """종합 검색 수행 (비동기)"""
        results = {}
        races = self.get_recent_races(num_races)

        print(f"🔍 {len(races)}개 대회에서 데이터 수집 중...\n")

        for race_name, race_date in races:
            race_results = await self.fetch_race_results(
                race_name, age_group, gender, division, top_n
            )
            results[race_name] = race_results
            await asyncio.sleep(1)

        return results

    def search_rankings_sync(self, age_group: str, gender: str, division: str,
                           top_n: int = 10, num_races: int = 10) -> Dict:
        """동기식 래퍼 (Flask와 호환)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.search_rankings(age_group, gender, division, top_n, num_races)
            )
        finally:
            loop.close()


# 테스트
async def main():
    """테스트"""
    scraper = HyroxPlaywrightScraper()

    results = await scraper.search_rankings(
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


if __name__ == "__main__":
    asyncio.run(main())
