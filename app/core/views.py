import json
from django.http import JsonResponse
from django.http.response import HttpResponse
from .serializers import UserSerializer, AttendanceSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
import os
import sys
import requests
from datetime import datetime
# import subprocess

from zk import ZK

# command = "python manage.py runscript activate_server && python manage.py runscript activate_attendance"
# comm = "git status && python manage.py LiveAttendance"
# subprocess.call(comm, shell=True)

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)
import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

conn = None
zk = ZK('172.17.32.83', port=4370)


@csrf_exempt
@api_view(['GET', 'PUT'])
def user_data(request):
    try:
        global conn, zk
        conn = zk.connect()
        print('Disabling device ...')
        conn.disable_device()
        print('--- Get User ---')
        users = conn.get_users()
        print("############### Current total users: ", len(users))
        start = 0
        for user in users:
            temp = int(user.uid) - start
            start = start + 1
            if temp != 1:
                print("******dirty data at uid: ", user.uid)
    except Exception as ex:
        print("Process terminate : {}".format(ex))
        return JsonResponse(ex)

    if request.method == 'GET':
        serializer = UserSerializer(users, many=True)
        return JsonResponse({
            "success": True,
            "Data": serializer.data
        }, safe=False)

    elif request.method == 'PUT':
        # data = JSONParser().parse(request)
        d = request.data
        serializer = UserSerializer(data=d)
        if serializer.is_valid():
            print("----user update started---")
            user_data = serializer.data

            try:
                user_update = conn.set_user(
                    uid=user_data['uid'],
                    name=user_data['name'],
                    privilege=user_data['privilege'],
                    password=user_data['password'],
                    user_id=str(user_data['user_id'])
                )

            except Exception as ex:
                return JsonResponse({
                    'success': False,
                    'data': ex
                })
                raise ex

            return JsonResponse({
                "success": True,
                "data": user_data
            })
        return JsonResponse({
            "success": False,
            'data': serializer.errors
        })


@csrf_exempt
@api_view(['GET'])
def plant_01_att(request):
    att_ip_one = ZK(env('PLANT_01_ATT'), port=4370) #172.16.32.81 head office ip
    att_conn_one = att_ip_one.connect()
    att_all_list = att_conn_one.get_attendance()
    att_all_list = AttendanceSerializer(
        att_all_list, many=True)
    payload = { "att_all_list": att_all_list.data, "plant": '1' }
    url = "http://172.17.32.6:8181/hrmmogllie/api/zkteco/sync/att/all"
    res = requests.post(url,json = payload)
    return JsonResponse({'success':"true"})

@csrf_exempt
@api_view(['GET'])
def plant_02_att(request):
    att_ip_two = ZK(env('PLANT_02_ATT'), port=4370) #172.16.32.81 head office ip
    att_conn_two = att_ip_two.connect()
    att_all_list = att_conn_two.get_attendance()
    att_all_list = AttendanceSerializer(
        att_all_list, many=True)
    payload = { "att_all_list": att_all_list.data, "plant": '2' }
    url = "http://172.17.32.6:8181/hrmmogllie/api/zkteco/sync/att/all"
    res = requests.post(url,json = payload)
    return JsonResponse({'success':"true"})

@csrf_exempt
@api_view(['GET'])
def plant_01_meal(request):
    meal_ip_one = ZK(env('PLANT_01_MEAL_CARD'), port=4370) #172.16.32.81 head office ip
    meal_conn_one = meal_ip_one.connect()
    att_all_list = meal_conn_one.get_attendance()
    att_all_list = AttendanceSerializer(
        att_all_list, many=True)
    payload = { "att_all_list": att_all_list.data, "plant": '1' }
    url = "http://172.17.32.6:8181/hrmmogllie/api/zkteco/sync/meal/all"
    res = requests.post(url,json = payload)
    return JsonResponse({'success':"true"})

@csrf_exempt
@api_view(['GET'])
def plant_02_meal(request):
    meal_ip_two = ZK(env('PLANT_O2_MEAL_CARD'), port=4370) #172.16.32.81 head office ip
    meal_conn_one = meal_ip_two.connect()
    att_all_list = meal_conn_one.get_attendance()
    att_all_list = AttendanceSerializer(
        att_all_list, many=True)
    payload = { "att_all_list": att_all_list.data, "plant": '2' }
    url = "http://172.17.32.6:8181/hrmmogllie/api/zkteco/sync/meal/all"
    res = requests.post(url,json = payload)
    return JsonResponse({'success':"true"})

def attendance_list(request):
    try:
        global conn, zk
        conn = zk.connect()
        print('Disabling device ...')
        conn.disable_device()
        print('--- Get attendances ---')
        att_list = conn.get_attendance()
        att_list = AttendanceSerializer(
            att_list, many=True)
        
    
    except Exception as ex:
        print("Process terminate : {}".format(ex))
        return JsonResponse(ex)

    if request.method == 'GET':
        return JsonResponse(att_list.data, safe=False)


def attendance_live_capture(request):
    try:
        conn = zk.connect()
        for attendance in conn.live_capture():
            if attendance is None:
                pass
            else:
                att_data = AttendanceSerializer(attendance)
                print(att_data.data)
                att_all_list = conn.get_attendance()
                payload = {"current_att_data": att_all_list,
                           "att_all_list": att_data}
                res = requests.post(
                    "http://localhost/hrm/api/zkteco/att-new-record", params=payload)
                print(res.json())
    except UnboundLocalError:
        print(" I am unable to connect to the server")
    except Exception as e:
        print("Process terminate : {}".format(e))
    finally:
        pass

@csrf_exempt
def classify_data(att_items):
    strg_att_list = list()

    today_date = datetime.now().strftime("%Y-%m-%d")
    today_date_split = today_date.split('-')
    file_name = today_date_split[0]+'_' + \
        today_date_split[1]+'_'+today_date_split[2]+'.json'

    att_list = att_items
    current_data = att_list['current_att_data']
    prev_datas = att_list['att_all_list']

    if os.path.exists(file_name):
        json_file = open(file_name)
        json_string = json_file.read()
        json_file.close()
        strg_att_list = json.loads(json_string)
        strg_att_list.append(current_data)
    else:
        for item in prev_datas:
            current_item_date = item['timestamp']
            current_item_split = current_item_date.split('-')
            if current_item_split[0] == today_date_split[0] and current_item_split[1] == today_date_split[1]:
                strg_att_list.append(item)
        strg_att_list.append(current_data)
        with open(str(file_name), 'w') as jsonfile:
            json.dump(strg_att_list, jsonfile)

    return strg_att_list
