import datetime
import os
import signal
import subprocess
from pathlib import Path
import nextcloud_client
import sqlite3

class Setup:
    def __init__(self):
        self.dbdir = '../db'
        self.dburl = '../db/simdb.db'
        self.status = False
        self.message = None
        self.login = None
        self.password = None
        self.directory = None
        self.url_nextcloud = None

    def create_db(self):
        # Create file and directory
        dirdb = Path(self.dbdir)
        dirdb.mkdir(parents=True, exist_ok=True)
        dbfile = Path(self.dburl)
        dbfile.touch(exist_ok=True)

        # Create table of db
        con = sqlite3.connect(self.dburl)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS setup(
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                login TEXT,
                password TEXT,
                directory TEXT,
                url_nextcloud TEXT
            )''')
        con.commit()
        con.close()


    def setup_simcam(self, login, password, directory, url_nextcloud):
        self.login = login
        self.password = password
        self.directory = directory
        self.url_nextcloud = url_nextcloud
        self.status = True
        self.message = "Configuration saved successfully"

        try:
            self.create_db()

            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT id FROM setup")
            data = cur.fetchone()
            if data is not None:
                print('Exist')
                cur.execute("DELETE FROM setup")
                con.commit()
            donnees = (login, password, directory, url_nextcloud)
            cur.execute("INSERT INTO setup (login, password, directory, url_nextcloud) VALUES (?, ?, ?, ?)", donnees)
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            self.message = "Failed to insert data into sqlite table : " + str(error)
            self.status = False
        return self.status, self.message

    def get_setup(self):
        try:
            self.create_db()
            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT * FROM setup")
            data = cur.fetchone()
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            self.message = "Failed to insert data into sqlite table : " + str(error)
            status = 500
            return status, self.message

        # true = enregistrement en cours / false = pas d'enregistrement en cours
        if data is not None:
            status = 200
            return status, data[1], data[2], data[3], data[4]
        else:
            self.message = "Setup not found"
            status = 404
            return status, self.message

class Rec:
    def __init__(self):
        self.setup = Setup()
        self.dburl = '../db/simdb.db'
        self.dirvideo = '../data/video/'
        self.status = False
        self.pid = None
        self.file_source = None
        self.file_name = None
        self.name = None
        self.time = None
        self.time_limit = None
        self.login = None
        self.password = None
        self.directory = None
        self.url_nextcloud = None


    def rec_video(self, name, time_limit):
        # Déclaration de variable
        self.time = datetime.datetime.now().timestamp()
        timestamp = datetime.datetime.now()
        jour = timestamp.strftime('%d-%m-%y_%Hh%M')

        # Création dossier
        path = Path(self.dirvideo)
        path.mkdir(parents=True, exist_ok=True)

        # Nom fichier
        self.name = name.replace(" ", "_")
        self.file_name = self.name + '_' + jour + '.mp4'
        self.file_source = self.dirvideo + self.file_name

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
        data_setup = self.setup.get_setup()

        self.login = data_setup[1]
        self.password = data_setup[2]
        self.directory = data_setup[3]
        self.url_nextcloud = data_setup[4]
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
            nc = nextcloud_client.Client(self.url_nextcloud)
            nc.login(self.login, self.password)

            try:
                nc.mkdir(self.directory + annee + '')
            except:
                print("Directory Exist")

            try:
                nc.mkdir('Simon/Vidéos-Simon/' + annee + '/Semaine-' + semaine + '')
            except:
                print("Directory Exist")

        except:
            pass

        # Changement status de l'enregistrement
        self.status = False

        return self.file_source

    def status_rec(self):
        return self.status

    def info_rec(self):
        return self.pid, self.name, self.file_name, self.file_source, self.time, self.status


class Upload:
        def __init__(self):
            self.setup = Setup()

        def upload_file(self):
            data_setup = self.setup.get_setup()

            login = data_setup[1]
            password = data_setup[2]
            cmd_upload = 'login="' + login + '" password="' + password + '" bash ../cron/simcron.bash >> ../log/simcron.txt'
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
