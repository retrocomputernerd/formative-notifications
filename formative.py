import requests
import time
from threading import Thread
from seleniumwire import webdriver
import json
from seleniumwire.utils import decode
from slack_sdk.webhook import WebhookClient
with open('formativesettings.json') as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()
email = (jsonObject['email'])
password = jsonObject['password']
url = jsonObject['webhook']
webhook = WebhookClient(url)
driver = webdriver.Chrome(executable_path="REDACTED")
print('Imported all required libraries and settings')
driver.get('https://app.formative.com/')
time.sleep(2)
driver.find_element_by_xpath('//*[@id="routes-container"]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[1]/input').send_keys(email)
driver.find_element_by_xpath('//*[@id="routes-container"]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[2]/input').send_keys(password)
driver.find_element_by_xpath('//*[@id="routes-container"]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[3]/button').click()
request = driver.wait_for_request('https://svc.goformative.com/graphql/auth/mutation/LoginWith')
for request in driver.requests:
    if request.response:
            if request.url.startswith("https://svc.goformative.com/graphql/auth/mutation/LoginWith"):
                    body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                    jsonResponse = json.loads(body.decode('utf-8'))
                    JWTToken = jsonResponse['data']['login']['loginToken']
                    refreshToken = jsonResponse['data']['login']['refreshToken']
                    print('Successfully harvested login tokens')
print('Now starting the Loop')
i = 1
while i < 6:
    print('Starting the Loop')
    headers2 = {
        'authority': 'svc.goformative.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'b3': 'REDACTED',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        'origin': 'https://app.formative.com',
        'referer': 'https://app.formative.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
        'x-app-version': 'production-2022-10-07-379598-83',
        'x-ntp-t0': 'REDACTED',
    }

    json_data2 = {
        'operationName': 'RefreshUserSessionTokens',
        'variables': {
            'refreshToken': refreshToken,
            'loginToken': JWTToken,
        },
        'query': 'mutation RefreshUserSessionTokens($refreshToken: String!, $loginToken: String!) {\n  refreshUserSessionTokens(refreshToken: $refreshToken, loginToken: $loginToken) {\n    loginToken\n    loginTokenExpiration\n    refreshToken\n    refreshTokenExpiration\n    userId\n    __typename\n  }\n}\n',
    }

    response2 = requests.post('https://svc.goformative.com/graphql/mutation/RefreshUserSessionTokens', headers=headers2, json=json_data2)
    json2 = response2.json()
    JWTToken = json2['data']['refreshUserSessionTokens']['loginToken']
    refreshToken = json2['data']['refreshUserSessionTokens']['refreshToken']
    print(JWTToken)
    print(refreshToken)
    print('Harvested Brand New Tokens')
    headers = {
        'authority': 'svc.goformative.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer ' + str(JWTToken),
        'b3': 'REDACTED',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        'origin': 'https://app.formative.com',
        'referer': 'https://app.formative.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
        'x-app-version': 'production-2022-10-06-377494-a5',
        'x-ntp-t0': 'REDACTED',
        'x-user-id': 'REDACTED',
    }

    json_data = {
        'operationName': 'NotificationCenterCountQuery',
        'variables': {
            'isRead': False,
            'startDate': '2022-09-08T04:00:00.000Z',
            'withNotifications': True,
        },
        'query': 'query NotificationCenterCountQuery($isRead: Boolean, $startDate: Date!, $withNotifications: Boolean!) {\n  viewer {\n    _id\n    student\n    feedbackMessages2(isRead: $isRead, startDate: $startDate) {\n      totalCount\n      __typename\n    }\n    notifications(isRead: $isRead, startDate: $startDate) @include(if: $withNotifications) {\n      totalCount\n      __typename\n    }\n    orgInvites {\n      code\n      email\n      sentAt\n      __typename\n    }\n    sectionInvites {\n      code\n      __typename\n    }\n    __typename\n  }\n}\n',
    }
    response = requests.post('https://svc.goformative.com/graphql/query/NotificationCenterCountQuery', headers=headers, json=json_data)
    #print(response.text)
    json = response.json()
    notificationcount = json['data']['viewer']['feedbackMessages2']['totalCount']
    print('Checking Notifications')
    if notificationcount >= 1:
        print(notificationcount)
        webhook.send(text='<!channel> CHECK FORMATIVE YOU HAVE ' + str(notificationcount) + ' NOTIFICATIONS')
    print('Sleeping for 10 minutes')
    time.sleep(600)
   
