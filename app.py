#!/usr/bin/env python3
"""
HYROX Rankings Analyzer - Flask 백엔드
웹 앱의 API 서버입니다.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from hyrox_scraper_hybrid import HyroxHybridScraper

app = Flask(__name__)
CORS(app)

# 글로벌 스크래퍼 인스턴스
# 하이브리드 스크래퍼: API → Selenium → Test Data 순서로 시도
scraper = HyroxHybridScraper()

# 캐시된 결과 (메모리)
cache = {}


@app.route('/')
def index():
    """메인 페이지"""
    try:
        # Vercel과 로컬 환경 모두 호환
        html_file = 'hyrox_app_v2.html'
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # 파일이 없으면 간단한 HTML 반환
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>HYROX Rankings Analyzer</title></head>
        <body style="text-align: center; padding: 50px;">
            <h1>🏃 HYROX Rankings Analyzer</h1>
            <p>앱 파일을 로드할 수 없습니다.</p>
            <p><a href="/api/races">API 테스트</a></p>
        </body>
        </html>
        '''


@app.route('/api/search', methods=['POST'])
def search_rankings():
    """
    랭킹 검색 API

    요청 데이터:
    {
        'age_group': '50',
        'gender': 'M',
        'division': 'H',
        'top_n': 10,
        'num_races': 10
    }
    """
    try:
        data = request.get_json()

        age_group = data.get('age_group', '')
        gender = data.get('gender', '')
        division = data.get('division', '')
        top_n = int(data.get('top_n', 10))
        num_races = int(data.get('num_races', 10))

        # 입력값 검증
        if not age_group or not gender or not division:
            return jsonify({
                'success': False,
                'error': '나이 그룹, 성별, 카테고리를 모두 선택해주세요.'
            }), 400

        # 캐시 키
        cache_key = f"{age_group}_{gender}_{division}_{top_n}_{num_races}"

        # 캐시 확인
        if cache_key in cache:
            return jsonify({
                'success': True,
                'data': cache[cache_key],
                'cached': True
            })

        # 검색 수행
        results = scraper.search_rankings(
            age_group=age_group,
            gender=gender,
            division=division,
            top_n=top_n,
            num_races=num_races
        )

        # 결과 포맷팅
        formatted_results = {}
        total_participants = 0

        for race_name, race_results in results.items():
            formatted_results[race_name] = []

            for result in race_results:
                formatted_results[race_name].append({
                    'rank': result.get('rank'),
                    'firstName': result.get('firstName', 'N/A'),
                    'lastName': result.get('lastName', 'N/A'),
                    'time': result.get('time', 'N/A'),
                    'nationality': result.get('nationality', 'N/A'),
                    'ageGroup': result.get('ageGroup', 'N/A'),
                })
                total_participants += 1

        response_data = {
            'success': True,
            'data': formatted_results,
            'stats': {
                'total_races': len(formatted_results),
                'total_participants': total_participants,
                'timestamp': datetime.now().isoformat()
            },
            'cached': False
        }

        # 캐시에 저장
        cache[cache_key] = response_data

        return jsonify(response_data)

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'입력값 오류: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'검색 중 오류가 발생했습니다: {str(e)}'
        }), 500


@app.route('/api/races', methods=['GET'])
def get_races():
    """최근 대회 목록 반환"""
    try:
        num_races = request.args.get('num', 20, type=int)
        races = scraper.get_recent_races(num_races)

        return jsonify({
            'success': True,
            'races': [
                {
                    'name': name,
                    'date': date
                }
                for name, date in races
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 초기화"""
    global cache
    cache.clear()
    return jsonify({
        'success': True,
        'message': '캐시가 초기화되었습니다.'
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """통계 정보"""
    return jsonify({
        'success': True,
        'cache_size': len(cache),
        'cache_keys': list(cache.keys()),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # 개발 서버로 실행
    # 프로덕션에서는 gunicorn 등을 사용하세요
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/api/debug', methods=['GET'])
def debug_fetch():
    """Hyrox HTML 응답 디버그 - /api/debug?race=2026+Washington+DC&sex=M&age=50"""
    import requests as req
    race = request.args.get('race', '2026 Washington DC')
    sex  = request.args.get('sex', 'M')
    age  = request.args.get('age', '50')
    results = {}

    hdrs = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Referer': 'https://results.hyrox.com/season-8/',
    }

    for label, url, params in [
        ('pid_list', 'https://results.hyrox.com/season-8/index.php',
         {'event_main_group': race, 'pid': 'list', 'pidp': 'ranking_nav',
          'search[sex]': sex, 'search[age_class]': age, 'search[nation]': '%'}),
        ('ajax2', 'https://results.hyrox.com/season-8/',
         {'content': 'ajax2', 'client': 'js', 'event_main_group': race,
          'search[sex]': sex, 'search[age_class]': age}),
        ('base', 'https://results.hyrox.com/season-8/', {}),
    ]:
        try:
            r = req.get(url, params=params, headers=hdrs, timeout=12)
            results[label] = {
                'url': r.url, 'status': r.status_code,
                'ct': r.headers.get('Content-Type',''),
                'len': len(r.text),
                'snippet': r.text[:4000],
            }
        except Exception as e:
            results[label] = {'error': str(e)}

    return jsonify(results)
@app.route('/api/debug2', methods=['GET'])
def debug_fetch2():
    """
    Full HTML 분석 + 테이블 탐색 디버그
    /api/debug2?race=2026+Washington+DC&sex=M&age=50
    """
    import requests as req
    from bs4 import BeautifulSoup
    race = request.args.get('race', '2026 Washington DC')
    sex  = request.args.get('sex', 'M')
    age  = request.args.get('age', '50')

    hdrs = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Referer': 'https://results.hyrox.com/season-8/',
    }

    results = {}

    # pid=list 전체 응답 분석
    try:
        r = req.get(
            'https://results.hyrox.com/season-8/index.php',
            params={'event_main_group': race, 'pid': 'list', 'pidp': 'ranking_nav',
                    'search[sex]': sex, 'search[age_class]': age, 'search[nation]': '%'},
            headers=hdrs, timeout=15
        )
        soup = BeautifulSoup(r.text, 'html.parser')

        # 모든 테이블 찾기
        tables = soup.find_all('table')
        table_info = []
        for i, t in enumerate(tables):
            rows = t.find_all('tr')
            cells_per_row = [len(row.find_all(['td','th'])) for row in rows[:3]]
            table_info.append({
                'index': i,
                'class': t.get('class', []),
                'id': t.get('id', ''),
                'rows': len(rows),
                'cells_in_first_rows': cells_per_row,
                'first_row_text': rows[0].get_text(' | ', strip=True)[:200] if rows else '',
                'second_row_text': rows[1].get_text(' | ', strip=True)[:200] if len(rows) > 1 else '',
                'third_row_text': rows[2].get_text(' | ', strip=True)[:200] if len(rows) > 2 else '',
            })

        # tbody 직접 찾기
        tbodies = soup.find_all('tbody')

        # 선수 이름처럼 보이는 텍스트 검색 (대문자 이름 패턴)
        import re
        name_pattern = re.compile(r'[A-Z][a-z]+,\s*[A-Z]')
        all_text = r.text
        names_found = name_pattern.findall(all_text)[:20]

        # ul.list-group 또는 div.list 패턴 찾기
        list_divs = soup.find_all(['ul', 'ol', 'div'], class_=re.compile(r'list|result|rank', re.I))

        results['pid_list_analysis'] = {
            'status': r.status_code,
            'total_len': len(r.text),
            'table_count': len(tables),
            'tables': table_info,
            'tbody_count': len(tbodies),
            'names_found_in_html': names_found,
            'list_divs_count': len(list_divs),
            'list_divs_classes': [str(d.get('class','')) for d in list_divs[:10]],
            'full_html_tail': r.text[-3000:],   # 마지막 3000자
            'body_start': str(soup.body)[:3000] if soup.body else 'no body',
        }
    except Exception as e:
        import traceback
        results['pid_list_analysis'] = {'error': str(e), 'trace': traceback.format_exc()}

    # content=search 시도 (다른 데이터 엔드포인트 후보)
    for extra_content in ['search', 'list', 'ajax3', 'results']:
        try:
            r2 = req.get(
                'https://results.hyrox.com/season-8/',
                params={'content': extra_content, 'client': 'js',
                        'search[sex]': sex, 'search[age_class]': age,
                        'event_main_group': race},
                headers=hdrs, timeout=8
            )
            results[f'content_{extra_content}'] = {
                'status': r2.status_code,
                'ct': r2.headers.get('Content-Type',''),
                'len': len(r2.text),
                'snippet': r2.text[:2000],
            }
        except Exception as e:
            results[f'content_{extra_content}'] = {'error': str(e)}

    return jsonify(results)
