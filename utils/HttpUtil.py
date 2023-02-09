from urllib import request
from urllib import parse

# from flask import logging
class HttpUtil(object):
    @staticmethod
    def handle_response(resp):
        if resp.getcode() == 200:
            return resp.read().decode('UTF-8')
        else:
            print(str(resp)+', HTTP CODE=' + resp.getcode())
            return None

    @staticmethod
    def post(url, params=None):
        try:
            if type(url) is not str:
                print(str(url)+' is not a str')
                return None
            if params is not None:
                if type(params) is not dict:
                    print(type(params) + ' is not a dict')
                    return None
                else:
                    data = parse.urlencode(params).encode('utf-8')
                    resp = request.urlopen(url, data=data)
                    return HttpUtil.handle_response(resp)
            else:
                return HttpUtil.handle_response(request.urlopen(url,data={}))
        except Exception as e:
            print(e)
        finally:
            print(str(url)+':'+str(params))


    @staticmethod
    def simple_post(url, params=None):
        try:
            if type(url) is not str:
                print(str(url) + ' is not a str')
                return None
            if params is not None:
                if type(params) is not dict:
                    print(type(params) + ' is not a dict')
                    return None
                else:
                    data = parse.urlencode(params).encode('utf-8')
                    with request.urlopen(url, data=data) as resp:
                        print('HttpStatus: ' + resp.status + ' - ' + resp.reason)
                        return resp
            else:
                return request.urlopen(url, data={})
        except Exception as e:
            print(e)
        finally:
            print(str(url) + ':' + str(params))


    @staticmethod
    def get(url, params=None):
        try:
            if type(url) is not str:
                print(str(url)+' is not a str')
                return None
            if params is not None and type(params) is dict:
                url = url+'?'
                for key in list(params.keys()):
                    url = url + str(key) + '=' + str(params[key]) + '&'
                url = url[0:-1]
            else:
                print('type is not dict, type='+str(type(params)))
            resp = request.urlopen(url)
            return HttpUtil.handle_response(resp)
        except Exception as e:
            print('exception:'+str(e))
            raise e
        finally:
            print(url)

    @staticmethod
    def generate_params(params):
        if type(params) is dict:
            return {'request_data': params}
        else:
            return None

if __name__ == '__main__':
#     params = {'request_data': {'login_id': 'fanjianfang@cnpc.com.cn', 'token': '123123123'}}
#     get_params = {'login_id': 'fanjianfang@cnpc.com.cn', 'token': '123123123'}
#     url = 'http://11.11.156.106:610/portal/v1/version/static_info'
#     print(HttpUtil.post(url=url, params=params))
#     print('---------------------post1-----------------------')
#     print(HttpUtil.post(url, {}))
#     print('---------------------post2-----------------------')
#     print(HttpUtil.post(url, None))
#     print('---------------------post3-----------------------')
#     print(HttpUtil.post(url))
#     print('---------------------post4-----------------------')
#     print(HttpUtil.get(url=url, params=get_params))
    s = [b'\xe7\x89\x88\xe6\x9c\xac\xe4\xb8\x8d\xe5\xad\x98\xe5\x9c\xa8']
    a = s[0]
    print(a.decode('utf-8'))