import requests
import urllib3
import sys
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parser_result(json,service) -> bool:
    if json['services'][service]['healthz'] == "up":
        return True
    else:
        print("Service with not \"up\" state - {}".format(json['services'][service]['healthz']))
        return False

def get_service_status(url,service,namespace,token):
    service = service + "." + namespace
    body = {"procedure": "status","run-service": service}
    res = requests.post(url, headers={'Authorization': 'Bearer ' + token}, json = body, verify=False)
    if res.status_code == 200:
        if parser_result(res.json(),service):
            print("200 OK, {}".format(res.json()['services'][service]['healthz']))
        else:
            sys.exit(1)
    else:
        print("Something went wrong - {} : {}".format(res.status_code,res.text))
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Service check")
    parser.add_argument("-u", dest="url", required=True)
    parser.add_argument("-s", dest="service", required=True)
    parser.add_argument("-n", dest="namespace", required=True)
    parser.add_argument("-t", dest="token", required=True)
    args = parser.parse_args()

    try:
        get_service_status(args.url,args.service,args.namespace,args.token)
    except Exception as e:
        print("Something went wrong - {}".format(e))
        sys.exit(1)


### How to run
#  
#  
# python3 sm--test.py -u http://site-manager.qa-fullha-kubernetes.openshift.sdntest.qubership.org/sitemanager -s sm- -n default -t eyJhbGciOiJSUzI1NiIsImtpZCI6Im9MT3EyZ1JqSnJpc0RqanJpakVBdjJ4ZjJJaWRoVkZJQWRwdVRsaFIzZHMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJzaXRlLW1hbmFnZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoic20tYXV0aC1zYS10b2tlbiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJzbS1hdXRoLXNhIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiZDI1NmFlOWQtMGNlNS00Y2YxLWEwMmUtNDhmNzM2NmU5YzlhIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OnNpdGUtbWFuYWdlcjpzbS1hdXRoLXNhIn0.LQYopkzTgsTh23X0sCZfmaTBw7nPgthJlxLGM2cHbgoakx2M4QD487A_0JuA8_hiY7VdmXRvV3cH9OptwnjcuJ-D1fkjMgVxhkuXdOaE_5zIP-BtaaWeRUHQ3M5f-lPYGMlrAHAQrCzJ-LXYbrjfBRpIO5-CjgBiG_cMsI8RK4DXo214A6HLpfFOnABZ_VXVIYW-1vhxrlEB_47zqdYFQhShpXURJukQKrHnlv1dj9gzrJG129zfqaii4d7eZEFGMrKpXx86eLcWTmRLMVcZXCf9xFtNUFXzVCo002Vb6UUiuWn6kswMJljXjxbcy9OCarPQnuC-TIPMWx7hyQx5Xg
#
#
### Example for output
# {
#   "services": {
#     "sm-.default": {
#       "deps": {
#         "after": [],
#         "before": []
#       },
#       "healthz": "up",
#       "message": "I'm OK",
#       "mode": "active",
#       "status": "done"
#     }
#   }
# }