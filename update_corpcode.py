from datetime import datetime 
import requests 
import pandas as pd 
import io 
import zipfile
import xml.etree.ElementTree as et 
import json

class Dart:
    def __init__(self):

        # today 
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')   

        # opendart crtfc_key 로드
        with open('./DATA/config.json','r') as in_file:
            config = json.load(in_file)
            self.crtfc_key = config['crtfc_key']
        
        # fetch 시간 업데이트 
        config['corpcode_fetch_time'] = self.today
        with open('./DATA/config.json','w') as out_file:
            json.dump(config, out_file, indent='\t')
    
    def __del__(self):
        print(f"[{self.today}] Dart Corpcode update.")

    def get_corpcode(self): 
        """ 
            get_corpcode() : OpenDart 기업 고유코드 로드 
                input : 
                output: 고유코드 DataFrame 
        """ 

        params = {'crtfc_key':self.crtfc_key} 
        items = ["corp_code", "corp_name", "stock_code", "modify_date"] 
        item_names = ["고유코드","회사명","종목코드","수정일"] 

        # 데이터 요청 url
        url = "https://opendart.fss.or.kr/api/corpCode.xml" 
        # 서버로 HTTP GET 요청하여 응답 획득 | params : 요청 인자 
        res = requests.get(url,params=params)
        # zip file 받아오기 | res.content : 응답의 Raw Body 메모리 파일 객체 BytesIO 인스턴스 생성 
        # BytesIO : Byte파일을 이진파일로 다룰 수 있게 함  
        zfile = zipfile.ZipFile(io.BytesIO(res.content)) 

        #첫 번째 zip file 열기 | namelist: 압축파일의 파일명 읽기
        fin = zfile.open(zfile.namelist()[0])  

        # fromstring : 문자열에서 xml 파싱 | utf-8 decoding 
        root = et.fromstring(fin.read().decode('utf-8')) 
        
        # 데이터를 저장할 리스트
        data = [] 
        # root에 저장된 하나의 Tree를 반환 
        for child in root: 
            # stock_code -> text로 바꿈 | strip : 앞 뒤 공백 삭제 
            if len(child.find('stock_code').text.strip()) > 1: # 종목코드가 있는 경우 
                # 데이터에 공백 리스트 추가 ( 데이터를 넣을 공간 ) => 리스트로 데이터를 저장하기 위함
                data.append([]) 
                for item in items: 
                    data[-1].append(child.find(item).text) 

        df = pd.DataFrame(data, columns=item_names) 
        return df

    def update_code_of_listed_company(self):
        '''
            update_code_of_listed_company() : 코스피/코스닥 상장 회사의 고유코드 업데이트
                get_corpcode() : Dart 등록 회사 고유코드 반환 
        '''

        df = pd.DataFrame()

        # Dart 등록 기업 목록 로드
        all_company = self.get_corpcode()
        # 코스피/코스닥 상장 기업 목록 로드
        listed_company = pd.read_csv('./DATA/listed_company.csv')
        ######################### 데이터 처리 #############################

        # 앞의 인덱스 삭제 
        listed_company = listed_company[['code','company']]
        # 전체 str로 변경 
        listed_company = listed_company.applymap(str)  
        for i in range(len(listed_company)):
            listed_company['code'][i] = listed_company['code'][i].zfill(6)

        ##################################################################

        # 두 데이터 병합 후, 필요한 데이터 선별
        df = pd.merge(listed_company, all_company, left_on='code', right_on='종목코드')
        df = df[['code','company','고유코드']]
        df = df.rename(columns={'고유코드':'corpcode'})

        df.to_csv('./DATA/corpcode.csv',index=False)

if __name__ == '__main__':
    dart = Dart()
    dart.update_code_of_listed_company()
