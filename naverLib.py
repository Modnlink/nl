def find_address_codes(address_name, file_path="address_code.txt"):
    matching_codes = []
    
    # 파일을 읽어서 address_codes 딕셔너리 생성
    with open(file_path, 'r', encoding='cp949') as file:
        next(file)  # 첫 줄은 헤더이므로 건너뜁니다.
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 3 and parts[2] == '존재':  # 폐지되지 않은 법정동만 포함합니다.
                code, name, _ = parts
                if address_name in name:
                    matching_codes.append(code)
    return matching_codes


def find_address_names(address_code, file_path="address_code.txt"):
    matching_names = ''
    
    # 파일을 읽어서 address_names 딕셔너리 생성
    with open(file_path, 'r', encoding='cp949') as file:
        next(file)  # 첫 줄은 헤더이므로 건너뜁니다.
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 3 and parts[2] == '존재':  # 폐지되지 않은 법정동만 포함합니다.
                code, name, _ = parts
                if address_code in code:
                    matching_names = name
    return matching_names
 