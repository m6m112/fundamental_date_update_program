from tqdm import tqdm
from datetime import datetime                                           # For Date management
import json                                                             # for json 
import requests                                                         # For HTTP request 
import pandas as pd                                                     # For Data management

class Fund_Updater():
    def __init__(self):
        '''
            __init__() : 클래스 생성자 함수 
                crtfc_key 로드 및 fetch_time 관리
        '''
        # today 
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')   

        # opendart crtfc_key 로드
        with open('./DATA/config.json','r') as in_file:
            config = json.load(in_file)
            self.crtfc_key = config['crtfc_key']
        
        # fetch 시간 업데이트 
        config['fund_fetch_time'] = self.today
        with open('./DATA/config.json','w') as out_file:
            json.dump(config, out_file, indent='\t')

        # corpcode 업로드 
        self.corpcode = pd.read_csv('./DATA/corpcode.csv')
        self.corpcode = self.corpcode.applymap(str)  
        for i in range(len(self.corpcode)):
           self.corpcode['corpcode'][i] = self.corpcode['corpcode'][i].zfill(8)
    
    def __del__(self):
        '''
            __del__() : 클래스 소멸자 함수 
        '''
        print(f"[{self.today}] financial statement update.")
    
    def get_xml_to_frame(self, url, items, items_names, params):
        '''
            get_xml_to_frame() : 데이터 요청 및 반환 함수 
                [input] 
                (1) url : json 데이터 요청 주소 
                (2) items : 반환 데이터 Key list
                (3) item_names : 반환 데이터 저장 컬럼명 리스트
                (4) params : url 요청 시, 필요한 인자의 딕셔너리 (ex. crtfc_key)
                
                [output] 
                xml 형식의 데이터를 DataFrame으로 반환
        '''

        # url에 데이터 요청 -> json형태로 요청 데이터 text 로드
        res = requests.get(url, params)
        json_dict = json.loads(res.text) 
        
        data = [] 
        # status가 "000"이면 정상 신호 
        if json_dict['status'] == "000":  
            # list 원소 가져오기 
            for line in json_dict['list']: 
                # 빈 리스트 추가 | 데이터를 리스트로 묶어서 저장하기 위함
                data.append([])

                for itm in items:
                    # 가져 올 item key를 찾아서 append 
                    if itm in line.keys(): 
                        data[-1].append(line[itm]) 
                    # 데이터가 없으면 공백 
                    else: 
                        data[-1].append('')

        df = pd.DataFrame(data, columns=items_names)
        return df

    
    def get_financial_state (self, crtfc_key, corp_code, bsns_year, reprt_code, fs_div):
        '''
            get_financial_state() : 단일회사재무제표 업로드 함수 
                [input]
                (1) corp_code : 고유코드 
                (2) bsns_year : 사업연도
                (3) reprt_code : 보고서 코드 (11013, 11012, 11014, 11011)
                (4) fs_div : 연결재무제표/재무제표 (CFS, OFS)

                [output]
                단일회사의 재무제표 데이터를 DataFrame 형태로 반환
        '''

        # 응답 결과 key list
        items = ["rcept_no","reprt_code","bsns_year","corp_code","sj_div","sj_nm", 
             "account_id","account_nm","account_detail","thstrm_nm", "thstrm_amount",
             "thstrm_add_amount","frmtrm_nm","frmtrm_amount", "frmtrm_q_nm","frmtrm_q_amount",
             "frmtrm_add_amount","bfefrmtrm_nm", "bfefrmtrm_amount","ord"] 

        # 응답 결과 DF의 column 명 설정 
        item_names = ["접수번호","보고서코드","사업연도","고유번호","재무제표구분", "재무제표명",
                  "계정ID","계정명","계정상세","당기명","당기금액", "당기누적금액","전기명","전기금액","전기명(분/반기)", 
                  "전기금액(분/반기)","전기누적금액","전전기명","전전기금액", "계정과목정렬순서"] 

        # 요청 인자 dictionary
        params = {'crtfc_key': crtfc_key, 'corp_code': corp_code, 'bsns_year': bsns_year, 'reprt_code': reprt_code, 'fs_div': fs_div} 
        # 요청 url | 단일회사 전체 재무제표
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json" 
        # 데이터 요청 함수 실행 
        df = self.get_xml_to_frame(url, items, item_names, params)

        return df
    
    def fund_update(self):
        '''
            fund_update() : 전 종목 2021년 사업보고서 다운로드 함수 
        '''

        code = self.corpcode['code']
        company = self.corpcode['company']
        corp_code = self.corpcode['corpcode']
     
        for i in tqdm(range(1, len(corp_code))):
            reprt_df =self.get_financial_state(self.crtfc_key, corp_code[i], 2021, '11011', fs_div = "CFS") 
            reprt_df = reprt_df.drop(['접수번호','당기누적금액','전기명(분/반기)','전기금액(분/반기)','전기누적금액','계정과목정렬순서'], axis = 1)
            reprt_df.to_csv(f'./DATA/final_reprt/[{company[i]}({code[i]})] final_reprt.csv', index = False)



if __name__ == '__main__':
    fund_updater = Fund_Updater()
    fund_updater.fund_update()