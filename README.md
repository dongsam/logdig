# LogDig

## 목적
웹 서비스상의 유저들의 행동, 이탈, 패턴을 파악하기 위해 웹상의 유저의 클릭, 페이지 이동 등을 로그로서 생성, 수집한다.

## How to use 
#### Deployment
- `git clone https://github.com/dongsam/logdig.git`
- `cd logdig`
- `config.py` 수정을 통한 서비스 설정 
    + [SERVICE_NAME, AWS KEY 등 ]
- `pip install -r requirements.txt`
    + (Flask, Flask-RESTful, boto3 설치)
- `python setup_AWS.py`
    + 결과로 나오는 `http://{{service-name}}-{{eb_version_lable_suffix}}.elasticbeanstalk.com` 
    + 형태의 URL에 AWS EB 실행을 위해 몇분 기다린 후 접속하여, Success 문구를 통해 정상 작동 확인
    + 해당 URL을  `clickTracker.js` 파일 상단 serverUrl 변수에 아래와 같이 삽입
    + `var serverUrl = 'http://test-service-1.elasticbeanstalk.com';`

#### Web 서비스에 적용
- Google analytics 형식으로 추적 대상 웹 페이지에 위 clickTracker.js 스크립트 삽입
    + `<script src="your_path/clickTracker.js"></script>`
    + 추후 [Google Analytics](https://developers.google.com/analytics/devguides/collection/analyticsjs/) 방식으로 변경 계획
- POST 로 로그 전송

#### 데이타가 쌓이는 형식
- 로그 데이터 이동 경로
![structure](http://i.imgur.com/T4Cxov9.png)

- SQS에 로그가 쌓이는 화면 
![sqs](http://i.imgur.com/aHFr822.png)


- **Lambda (SQS -> S3) 스케줄링 설정**
    + 스케줄링, 이벤트에 의해 Lambda Function 호출 시, SQS 큐에 로그가 100개 이상 쌓여있다면 S3로 저장
    + Lambda 스케줄링, 이벤트 설정은 AWS API(boto3)를 통해 설정이 불가능, 따라서 AWS 웹에서 수동 설정 필요
    + AWS Console -> Lambda -> 대상 Function 선택(SERVICE_NAME-lambda) -> Event Source 탭 선택 -> Add evnet Source
    + Event source type 을 Scheduled Event 로 설정하여 5분 주기 등 cron 처럼 설정 가능
    + 이 외에도 SNS, CloudWatch 등 원하는 이벤트 소스로 설정 가능
    ![lambda_setting](http://i.imgur.com/P0Y8dD2.png)


- S3에 로그가 저장되는 형식 
    + 일별로 디렉토리 생성 ex)2015-12-31 
    ![s3_date](http://i.imgur.com/uOHtVwo.png)
    + 일별 디렉토리 하위에 SHA-256 으로 해쉬된 이름으로 로그파일 저장 (로그 파일명 충돌방지)
    ![s3_log](http://i.imgur.com/iAFMmDq.png)


- Log 저장 형식 
    - 각 라인에 한개의 로그씩 한 파일에 100개 이상이 로그 존재
    ![log_file](http://i.imgur.com/ZAgYYqO.png)



#### 분석방법 
- Spark 등에서 S3에 쌓여있는 로그를 읽어 분석 가능
- Zeppelin 등을 통해 Dashboard 형태로 분석 및 시각화 가능


## 개발 및 배포 환경 및 기술스택 
- RESTful server    
    + AWS Elastic Beanstalk
    + Python 3.4 or 2.7
    + Flask, Flask-RESTful, boto3
    
- Log queue 
    + AWS SQS
    + AWS Lambda
        * Python 2.7

- Log storage - AWS S3


## 구조

### Client log sender
- 클릭좌표를 통한 Heat Map 구성 혹은 버튼, 링크만 추적
- 추후 마우스 이동 기록도 염두


#### ClickTracker.js
![clickTracker](http://i.imgur.com/ytMYAmo.png)
##### init local stroage
- user key 초기화 ( 20자리 랜덤 영문 대소문자, 숫자 )
- load_count 0으로 초기화
- 위 값 local storage에 저장 

##### click event listener
- a, span, button 태그에 대해 
- href, reactid, data-reactid 속성이 있으며 클릭 이벤트 발생시 make log 호출 

##### make log
- click handle event 호출하여 클릭 정보 획득 
- load_count 값 1 증가 
- 기타 로그 값들로 json 구성하여 LocalStorage 에 저장 ( html5, IE8 이상 )

##### click handle event
- 마우스 클릭 이벤트에 대해 클릭 x, y 좌표 등 반환

##### url change listenr
- DOMSubtreeModified 이벤트를 통해 비동기로 페이지가 새로 렌더링, 변경된것을 체크 
- 위 이벤트 발생 상황에서 url 값 변경 또한 감지시 send log 호출 

##### send log
- 페이지 새로 랜더링, 혹은 페이지 이동 후 LocalStorage 에 저장된 Log를 불러옴
- POST 로 RESTful Flask 서버에 불러온 로그 전송


### Log Data

|       Name      |            Description            |                example                 |
|-----------------|-----------------------------------|----------------------------------------|
| timestamp       | 로그 생성 시간(UT)                | 2015-12-22T06:19:03.366Z               |
| token           | 서비스 토큰                       | VkdzNVRsRlZVa1JVTURWUFVsVk9WVk5WT1U4PQ |
| user_key        | 유저 구분 세션 키                 | tR2VQSYNNXJwbBQLijmR                   |
| current_page    | 링크를 클릭한 페이지              | http://site.com/index.html             |
| link            | 클릭하여 이동된 링크              | http://site.com/page.html              |
| x               | 마우스 클릭 x 좌표                | 110                                    |
| y               | 마우스 클릭 y 좌표                | 400                                    |
| spent_milli_sec | 사이트 방문 후 소요 시간 (밀리초) | 1120                                   |
| user_agent      | Browser User Agent                | Mozilla/5.0 (Macintosh...              |
| load_count      | 사이트에서 링크 이동 횟수         | 2                                      |



## 추정 AWS 과금
![aws_pricing](http://i.imgur.com/rLbDeuJ.png)


## To do
### 추후 구성 계획
![logdig_future](http://i.imgur.com/I9fhKfg.png)

### LogDig Core ( Spark )
- 토큰(서비스), 알고리즘, 분석 별 Zeppelin Note 생성
- Zeppelin Note 별 스케줄 설정에 따라 주기적 실행, 분석, 결과데이터 생성

#### 분석 알고리즘
- Heat Map 집중 진행
- 그 후에는 A/B Test 고려

#### Analysis Language
- Python, Scala, Spark SQL

### Dashboard
- Zeppelin
- https://zeppelin.incubator.apache.org/

## 유사 서비스, 참고 자료
- https://www.google.com/analytics/
- http://bizspring.co.kr/website/heatmap/special_features.php
- https://www.optimizely.com/
- http://www.slideshare.net/yongho/ga-47277482
- http://www.slideshare.net/LeeGwan/ss-42159541
