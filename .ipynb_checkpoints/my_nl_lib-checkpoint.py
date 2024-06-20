import requests
import time
import random
import pandas as pd

MaxPages = 3000

def load_address_codes(file_path):
    """
    address_code.txt 파일에서 법정동 코드와 법정동명을 읽어와 딕셔너리로 반환합니다.
    :param file_path: address_code.txt 파일의 경로
    :return: 법정동 코드와 법정동명을 포함한 딕셔너리
    """
    address_codes = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            code, name, status = line.strip().split('\t')
            if status == '존재':  # 폐지된 법정동은 무시
                address_codes[code] = name
    return address_codes

def search_properties_by_condition(region_code, house_type, transaction_type, address_codes):
    url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd={house_type}&tradTpCd={transaction_type}&cortarNo={region_code}&showR0&page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Referer": "https://m.land.naver.com/map/"
    }

    all_data = []

    for attempt in range(MaxPages):
        try:
            print(f">> {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data.get('body'):
                print("더 이상 정보가 없습니다.")
                break

            # 현재 페이지의 데이터를 all_data 리스트에 추가
            for property_info in data['body']:
                cortarNo = property_info.get('cortarNo', '')
                if cortarNo in address_codes:  # 주어진 코드가 address_codes에 있을 때만 추가
                    house_info = {
                        '법정동명': address_codes[cortarNo],
                        '주택 유형': property_info.get('rletTpNm', ''),
                        '거래 유형': property_info.get('tradTpNm', ''),
                        '아파트명': property_info.get('atclNm', ''),
                        '가격': int(str(property_info.get('prc', '')).replace(',', '')),  # 가격을 문자열로 변환 후 쉼표 제거하여 정수로 변환
                        '면적(spc1)': property_info.get('spc1', ''),
                        '면적(spc2)': property_info.get('spc2', ''),
                        '특징 설명': property_info.get('atclFetrDesc', ''),
                        '동호수': property_info.get('buidNm', ''),
                        '층': property_info.get('flrInfo', ''),
                        '방향': property_info.get('direction', ''),
                        '게시일': property_info.get('atclCfmYmd', ''),
                        '위도': property_info.get('lat', ''),
                        '경도': property_info.get('lng', ''),
                        '업체': property_info.get('rltrNm', ''),  # 업체 추가
                    }
                    all_data.append(house_info)

            # 추가 페이지를 요청하기 위해 URL 변경
            url_split = url.split("&page=")
            page_number = int(url_split[1])
            next_page_url = url_split[0] + "&page=" + str(page_number + 1)
            url = next_page_url

        except requests.exceptions.RequestException as e:
            print(f"HTTP 요청 오류 발생: {str(e)} (시도 {attempt + 1}/5)")
            time.sleep(2 ** attempt)
        except ValueError:
            print("JSON 디코딩 오류 발생")
            break
        retry_interval = random.uniform(1, 5)
        time.sleep(retry_interval)

    # 가격을 기준으로 오름차순으로 정렬
    all_data_sorted = sorted(all_data, key=lambda x: x['가격'])

    return all_data_sorted

def save_properties_to_excel(properties, file_name):
    # DataFrame 생성
    df = pd.DataFrame(properties)

    # 엑셀 파일로 저장
    df.to_excel(file_name, index=False, sheet_name='sheet1')

    # Pivot 테이블 생성
    pivot_table = df.groupby(['법정동명', '아파트명', '면적(spc1)'])['가격'].agg(['max', 'min', 'mean', 'count']).reset_index()
    pivot_table['평균(면적/3.3)'] = pivot_table['mean'] / (pivot_table['면적(spc1)'].astype(float) / 3.3)
    
    # 엑셀 파일에 Pivot 테이블 추가
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a') as writer:
        pivot_table.to_excel(writer, sheet_name='sheet2', index=False)
