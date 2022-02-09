import json
from datetime import datetime
from django.core.management.base import BaseCommand
import requests
from core.serializers import AttendanceSerializer
from zk import ZK
import os
import sys
from tenacity import retry, wait_chain, wait_fixed
from django.views.decorators.csrf import csrf_exempt
import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)

ip_one = ZK(env('PLANT_O2_MEAL_CARD'), port=4370)
conn_one = None


class Command(BaseCommand):
    # @retry(retry=retry_if_exception_type())
    @retry(wait=wait_chain(*[wait_fixed(3) for i in range(3)] +
                           [wait_fixed(7) for i in range(2)] +
                           [wait_fixed(9)]))
    def handle(self, *args, **kwargs):
        self.stdout.write("Plant 02 mealcard: Live server is starting")
        try:
            conn_one = ip_one.connect()
            print('------------Plant 02 mealcard: Device connected!!!------------')
            for attendance in conn_one.live_capture():
                if attendance is None:
                    pass
                else:
                    att_data = AttendanceSerializer(attendance)
                    print(att_data.data)
                    meal_att_all_list = conn_one.get_attendance()
                    meal_att_all_list= AttendanceSerializer(meal_att_all_list,many=True)
                    
                            
                    payload = {"current_att_data": att_data.data,
                               "att_all_list": meal_att_all_list.data,
                               "plant":"2"}

                    with open("Meal_payload_plant_02.json", 'w') as jsonfile:
                        json.dump(payload, jsonfile)                      
                    res = requests.post(
                        env("MEALCARD_URL"), json=payload) 
                    print(res.status_code)    
                    # if res.status_code != 200:
                    #     conn_one.test_voice(index=33)
                    # else: 
                    #     conn_one.test_voice(index=0)
                    print("------------Plant 02 mealcard: Punch detected------------")
        except UnboundLocalError:
            print(" Plant 02 mealcard: I am unable to connect to server")
        except Exception as e:
            print("Plant 02 mealcard: Process terminate : {}".format(e))
        finally:
            if conn_one:
                conn_one.disconnect()

