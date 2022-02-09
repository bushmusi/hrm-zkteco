import json
from datetime import datetime
from django.core.management.base import BaseCommand
import requests
import threading
from core.serializers import AttendanceSerializer, UserSerializer
from zk import ZK
import os
import sys
from tenacity import retry, wait_chain, wait_fixed
import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)

ip_one = ZK(env('PLANT_02_ATT'), port=4370)
conn_one = None





class Command(BaseCommand):
    # @retry(retry=retry_if_exception_type())
    @retry(wait=wait_chain(*[wait_fixed(3) for i in range(3)] +
                           [wait_fixed(7) for i in range(2)] +
                           [wait_fixed(9)]))
    def handle(self, *args, **kwargs):
        self.stdout.write("Plant 02 attendance : server running")
        try:
            conn_one = ip_one.connect()
            print('------------Plant 02 attendance : Device connected!!!------------')
            
            users = conn_one.get_users()
            user_list = UserSerializer(users,many=True)
            users_payload = {
                "All Users: ": user_list.data
            }
            with open('Plant_02_users.json','w') as jsonfile:
                json.dump(users_payload,jsonfile)

            for attendance in conn_one.live_capture():
                if attendance is None:
                    pass
                else:
                    att_data = AttendanceSerializer(attendance)
                    print(att_data.data)
                    
                    strg_att_list = list()
                    """
                    Below codes will updated in next phase
                    """
                    today_date = datetime.now().strftime("%Y-%m-%d")
                    today_date_split = today_date.split('-')
                    file_name = 'plant_02_att_'+today_date_split[0]+'_' + \
                        today_date_split[1]+'_'+today_date_split[2]+'.json'

                    if os.path.exists(file_name):
                        json_file = open(file_name)
                        json_string = json_file.read()
                        json_file.close()
                        strg_att_list = json.loads(json_string)
                        strg_att_list.append(att_data.data)
                    else:
                        delete_old_files()
                        att_all_list = conn_one.get_attendance()
                        att_all_list = AttendanceSerializer(
                            att_all_list, many=True)
                        payload = {"current_att_data": att_data.data,
                                "att_all_list": att_all_list.data}
                        prev_datas = payload['att_all_list']
                        for item in prev_datas:
                            current_item_date = item['timestamp']
                            current_item_split = current_item_date.split('-')
                            if current_item_split[0] == today_date_split[0] and current_item_split[1] == today_date_split[1]:
                                strg_att_list.append(item)
                        strg_att_list.append(att_data.data)
                        with open(str(file_name), 'w') as jsonfile:
                            json.dump(strg_att_list, jsonfile)
                    """
                    Above codes will be maintined
                    """
                            
                    payload = {"current_att_data": att_data.data,
                               "att_all_list": strg_att_list}
                    

                    url = env("ATT_URL")
                    
                    threading.Thread(target=request_task,args=(url,payload)).start()
                    
                    print("------------Plant 02 attendance : Punch detected------------")
        except UnboundLocalError:
            print(" Plant 02 attendance : I am unable to connect to server")
        except Exception as e:
            print("Plant 02 attendance : Process terminate : {}".format(e))
        finally:
            if conn_one:
                conn_one.disconnect()

def request_task(url,data):
    requests.post(url,json = data)

# Delete old files && Delete existing file
def delete_old_files():
    directory = "."

    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".json")]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)
