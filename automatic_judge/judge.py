USERNAME = 'test_judge'
API_KEY = '65d13f6a296145338e12a26cda0a0eea'
CONTEST_ID = 1
URL = 'http://localhost:8888'
SLEEP_TIME = 200 # milliseconds
SLEEP_TIME = 0 # milliseconds

import requests
from time import sleep

URL = URL.rstrip('/')

def api_call(action, data={}):
    res = requests.post(URL + '/api/judge/' + action, data=dict({'username': USERNAME, 'api_key': API_KEY, 'contest_id': CONTEST_ID}.items() + data.items()))
    print res.text
    # print res.status_code
    # print res.json()
    return res.json()

while True:
    res = api_call('get_next_submission')

    if 'error' in res:
        if res['error'] == 'NO_SUBMISSIONS':
            pass
        else:
            print("Unknown error: %s" % res['error'])

        sleep(SLEEP_TIME / 1000.0)
    else:
        # print(res['submission']['id'])
        # print(res['team']['name'])
        # print(res['problem']['name'])
        # print(res['problem']['short_id'])
        # print(res['solution']['code'])
        # print(res['solution']['lang']['name'])
        # print(res['solution']['lang']['compile_cmd'])
        # print(res['solution']['lang']['run_cmd'])
        # print(res['announce_timeout'], ' ms')
        # if 'checker' in res:
        #     print(res['checker']['code'])
        #     print(res['checker']['lang']['name'])
        #     print(res['checker']['lang']['compile_cmd'])
        #     print(res['checker']['lang']['run_cmd'])
        # print(res['time_limit'], ' ms')
        # print(res['memory_limit'], 'bytes')
        # for t in res['tests']:
        #     print(t['input'])
        #     print(t['output'])

        ann_res = api_call('announce', {'submission_id': res['submission']['id']})
        # print(ann_res['announce_timeout'], ' ms')

        verdict_res = api_call('verdict', {'submission_id': res['submission']['id'], 'verdict': 'AC'})



