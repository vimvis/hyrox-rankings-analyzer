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
from hyrox_scraper import HyroxScraper

app = Flask(__name__)
CORS(app)

# 글로벌 스크래퍼 인스턴스
scraper = HyroxScraper()

# 캐시된 결과 (메모리)
cache = {}


@app.route('/')
def index():
    """메인 페이지"""
    # HTML 파일이 같은 디렉토리에 있는 경우
    return open('hyrox_app.html', 'r', encoding='utf-8').read()


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
