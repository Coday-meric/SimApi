import datetime
import os
import signal
import subprocess
from pathlib import Path
import nextcloud_client
from dotenv import load_dotenv

class Rec:
    def __init__(self):
        self.status = False
        self.pid = None
        self.file_source = None
        self.file_name = None
        self.name = None
        self.time = None
        self.time_limit = None

    def rec_video(self, name, time_limit):
        # Déclaration de variable
        self.time = datetime.datetime.now().timestamp()
        timestamp = datetime.datetime.now()
        jour = timestamp.strftime('%d-%m-%y_%Hh%M')

        # Création dossier
        path = Path('/simcam/data/video/')
        path.mkdir(parents=True, exist_ok=True)

        # Nom fichier
        self.name = name.replace(" ", "_")
        self.file_name = self.name + '_' + jour + '-quality.mp4'
        self.file_source = '/simcam/data/video/' + self.file_name

        # Set time limit Rec
        self.time_limit = time_limit

        # Démarrage VLC
        cmdbase = 'libcamera-vid --rotation 180 --nopreview -t ' + self.time_limit + ' --codec libav -o ' + self.file_source + ' --framerate 25 --width 1920 --height 1080 --profile high --level 4.2 --bitrate 2500000 -n --libav-audio --audio-source alsa --audio-device default --audio-bitrate 128000'
        process = subprocess.Popen(cmdbase, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                   preexec_fn=os.setsid)
        # Stockage du PID
        self.pid = os.getpgid(process.pid)

        # Status d'enregistrement
        self.status = True

        return self.status, self.pid

    def unrec_video(self):
        load_dotenv()

        login = os.getenv('NEXTCLOUD_LOGIN')
        password = os.getenv('NEXTCLOUD_PASSWORD')
        url_nextcloud = os.getenv('NEXTCLOUD_URL')
        datetime.datetime.now().timestamp()
        timestamp = datetime.datetime.now()
        annee = timestamp.strftime('%Y')
        semaine = timestamp.strftime('%V le %m.%y')

        try:
            os.killpg(self.pid, signal.SIGINT)
        except ProcessLookupError:
            pass

        # Use owncloud library for create dir of file mp4
        try:
            nc = nextcloud_client.Client(url_nextcloud)
            nc.login(login, password)

            try:
                nc.mkdir('Simon/Vidéos-Simon/' + annee + '')
            except:
                print("Directory Exist")

            try:
                nc.mkdir('Simon/Vidéos-Simon/' + annee + '/Semaine-' + semaine + '')
            except:
                print("Directory Exist")

        except:
            pass

        # Pour une utilisation de la library python
        # oc.drop_file('/home/aymeric/Codage/AEVE-REC-API/app/test.txt')

        # Changement status de l'enregistrement
        self.status = False

        # Supprimer le fichier vidéo temporaire
        # if os.path.exists(file_source):
        #    os.remove(file_source)

        return self.file_source

    def status_rec(self):
        return self.status

    def info_rec(self):
        return self.pid, self.name, self.file_name, self.file_source, self.time, self.status


class Upload:
    def upload_file(self):
        load_dotenv()
        login = str(os.getenv('NEXTCLOUD_LOGIN'))
        password = str(os.getenv('NEXTCLOUD_PASSWORD'))
        cmd_upload = 'login="' + login + '" password="' + password + '" bash /simcam/cron/AEVE-REC_Cron.bash >> /simcam/log/AEVE-REC_Cron.txt'
        subprocess.Popen(cmd_upload, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        return True


class Preview:
    def __init__(self):
        self.pid = None

    def run_preview(self):
        cmdbase = 'libcamera-vid -t 600000 --rotation 180 --width 1920 --height 1080 --codec h264 --inline --listen -o tcp://0.0.0.0:8888'
        process = subprocess.Popen(cmdbase, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                   preexec_fn=os.setsid)
        self.pid = os.getpgid(process.pid)

        return True

    def stop_preview(self):
        try:
            os.killpg(self.pid, signal.SIGINT)
        except ProcessLookupError:
            pass

        return True
