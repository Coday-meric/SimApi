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

    def create_db(self):
        # Create file and directory
        dirdb = Path(self.dbdir)
        dirdb.mkdir(parents=True, exist_ok=True)
        dbfile = Path(self.dburl)
        dbfile.touch(exist_ok=True)

        # Create table of db
        con = sqlite3.connect(self.dburl)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS setup_simcam(
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                rotate INTEGER,
                framerate INTEGER,
                width INTEGER,
                height INTEGER,
                profile TEXT,
                level TEXT,
                bitrate_vid INTEGER,
                bitrate_aud INTEGER
            )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS setup_simcloud(
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                login TEXT,
                password TEXT,
                directory TEXT,
                url_nextcloud TEXT
            )''')
        con.commit()
        con.close()

    def setup_simcam(self, rotate, framerate, width, height, profile, level, bitrate_vid, bitrate_aud):
        status = True
        message = "Configuration camera saved successfully"
        try:
            self.create_db()
            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT id FROM setup_simcam")
            data = cur.fetchone()
            if data is not None:
                print('Exist')
                cur.execute("DELETE FROM setup_simcam")
                con.commit()
            donnees = (rotate, framerate, width, height, profile, level, bitrate_vid, bitrate_aud)
            cur.execute("INSERT INTO setup_simcam (rotate, framerate, width, height, profile, level, bitrate_vid, bitrate_aud) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", donnees)
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            message = "Failed to insert data into sqlite table : " + str(error)
            status = False
        return status, message


    def setup_simcloud(self, login, password, directory, url_nextcloud):
        status = True
        message = "Configuration cloud saved successfully"
        try:
            self.create_db()
            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT id FROM setup_simcloud")
            data = cur.fetchone()
            if data is not None:
                print('Exist')
                cur.execute("DELETE FROM setup_simcloud")
                con.commit()
            donnees = (login, password, directory, url_nextcloud)
            cur.execute("INSERT INTO setup_simcloud (login, password, directory, url_nextcloud) VALUES (?, ?, ?, ?)", donnees)
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            message = "Failed to insert data into sqlite table : " + str(error)
            status = False
        return status, message

    def get_setup_simcloud(self):
        try:
            self.create_db()
            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT * FROM setup_simcloud")
            data = cur.fetchone()
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            message = "Failed to insert data into sqlite table : " + str(error)
            status = 500
            return status, message

        # true = enregistrement en cours / false = pas d'enregistrement en cours
        if data is not None:
            status = 200
            return status, data[1], data[2], data[3], data[4]
        else:
            message = "Setup cloud not found"
            status = 404
            return status, message

    def get_setup_simcam(self):
        try:
            self.create_db()
            con = sqlite3.connect(self.dburl)
            cur = con.cursor()
            cur.execute("SELECT * FROM setup_simcam")
            data = cur.fetchone()
            con.commit()
            con.close()
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
            message = "Failed to insert data into sqlite table : " + str(error)
            status = 500
            return status, message

        # true = enregistrement en cours / false = pas d'enregistrement en cours
        if data is not None:
            status = 200
            return status, data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]
        else:
            message = "Setup camera not found"
            status = 404
            return status, message

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


    def rec_video(self, name, time_limit):
        data_setup = self.setup.get_setup_simcam()
        rotate = data_setup[1]
        framerate = data_setup[2]
        width = data_setup[3]
        height = data_setup[4]
        profile = data_setup[5]
        level = data_setup[6]
        bitrate_vid = data_setup[7]
        bitrate_aud = data_setup[8]
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
        cmdbase = 'libcamera-vid --rotation ' + str(rotate) + ' --nopreview -t ' + self.time_limit + ' --codec libav -o ' + self.file_source + ' --framerate ' + str(framerate) + ' --width ' + str(width) + ' --height ' + str(height) + ' --profile ' + profile + ' --level ' + level + ' --bitrate ' + str(bitrate_vid) + ' -n --libav-audio --audio-source alsa --audio-device default --audio-bitrate ' + str(bitrate_aud) + ''
        process = subprocess.Popen(cmdbase, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                   preexec_fn=os.setsid)
        # Stockage du PID
        self.pid = os.getpgid(process.pid)

        # Status d'enregistrement
        self.status = True

        return self.status, self.pid

    def unrec_video(self):
        data_setup = self.setup.get_setup_simcloud()

        login = data_setup[1]
        password = data_setup[2]
        directory = data_setup[3]
        url_nextcloud = data_setup[4]
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
                nc.mkdir(directory + annee + '')
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

#Todo: Gerer le cron via falcon et python
class Upload:
        def __init__(self):
            self.setup = Setup()

        def upload_file(self):
            data_setup = self.setup.get_setup_simcloud()

            login = data_setup[1]
            password = data_setup[2]
            directory = data_setup[3]
            url_nextcloud = data_setup[4]
            cmd_upload = 'login="' + login + '" password="' + password + '" directory="' + directory + '" url_nextcloud="' + url_nextcloud + '" bash ../cron/simcron.bash >> ../log/simcron.txt'
            subprocess.Popen(cmd_upload, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            return True

#Todo: Improve preview with http protocole
class Preview:
    def __init__(self):
        self.setup = Setup()
        self.pid = None

    def run_preview(self):
        data_setup = self.setup.get_setup_simcam()
        rotate = data_setup[1]
        width = data_setup[3]
        height = data_setup[4]
        cmdbase = 'libcamera-vid -t 600000 --rotation ' + rotate + ' --width ' + width + ' --height ' + height + ' --codec h264 --inline --listen -o tcp://0.0.0.0:8888'
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
