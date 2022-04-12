import json
import pandas as pd                             # For Data management
from datetime import datetime                   # For Date management 

class Company_Updater():
    ## 상장 종목 업데이트 클래스 ##
    def __init__(self):
        '''
            __init__() : 클래스 생성자 함수 
        ''' 
        # 데이터 파일 경로 
        self.file_path = "C:/Users/user/OneDrive/바탕 화면/CODE/AIQuant/DATA"
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        # fetch 시간 업데이트 
        # json 파일 열기
        with open('./DATA/config.json','r') as in_file:
            config = json.load(in_file)

        # json 파일 수정 | listed_company_fetch_time 수정
        config['listed_company_fetch_time'] = self.today
        with open('./DATA/config.json','w') as out_file:
            json.dump(config, out_file, indent='\t')

    def __del__(self):
        '''
            __del__() : 클래스 소멸자 함수 
        ''' 
        print(f"[{self.today}] listed company list update.")

    def read_krx_code (self):
        '''
            read_krx_code() : KRX로부터 상장 기업 목록 파일을 읽어와서 데이터프레임으로 반환
        '''
        # 상장 종목 목록 가져오기 
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx = pd.read_html(url,header=0)[0]
        # 데이터 정리
        krx = krx[['종목코드','회사명']]
        krx = krx.rename(columns={'종목코드':'code','회사명':'company'})
        krx.code = krx.code.map('{:06d}'.format)

        krx.to_csv(f"{self.file_path}/listed_company.csv",index=False)    
        
        return krx

if __name__ == '__main__':
    cp = Company_Updater()
    cp.read_krx_code()
