from django.core.management.base import BaseCommand

from subprocess import Popen
from sys import stdout, stdin, stderr
import time
import os
import signal


class Command(BaseCommand):
    help = 'Run all commands'
    commands = [
        'python manage.py runserver 0.0.0.0:8000',
        # 'python manage.py Mogele_Plant_01_Att',
        # "python manage.py Mogele_Plant_01_Meal", #uncomment this if you running on Moglle
        # 'python manage.py Mogele_Plant_02_Att',
        # "python manage.py Mogele_Plant_02_Meal" #uncomment this if you running on Moglle

    ]

    def handle(self, *args, **options):
        proc_list = []

        for command in self.commands:
            print("$ " + command)
            proc = Popen(command, shell=True, stdin=stdin,
                         stdout=stdout, stderr=stderr)
            proc_list.append(proc)

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            for proc in proc_list:
                os.kill(proc.pid, signal.SIGKILL)
