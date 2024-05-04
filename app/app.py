import json
import falcon
from utils import Upload, Rec, Preview, Setup

setup = Setup()
rec = Rec()
preview = Preview()
upload = Upload()

class SetupSimCloud(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        data = json.load(req.stream)
        login = data['login']
        password = data['password']
        directory = data['directory']
        url_nextcloud = data['url_nextcloud']
        res = setup.setup_simcloud(login, password, directory, url_nextcloud)
        if res[0]:
            resp.status = falcon.HTTP_201
            resp.text = json.dumps({"message": res[1]})
        else:
            resp.status = falcon.HTTP_500
            resp.text = json.dumps({"message": res[1]})

    def on_get(self, req, resp):
        """Handles GET requests"""
        res = setup.get_setup_simcloud()
        if res[0] == 200:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps({"login": res[1], "password": res[2], "directory": res[3], "url_nextcloud": res[4]})
        elif res[0] == 404:
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"message": res[1]})
        else:
            resp.status = falcon.HTTP_500
            resp.text = json.dumps({"message": res[1]})

class SetupSimCam(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        data = json.load(req.stream)
        rotate = data['rotate']
        framerate = data['framerate']
        width = data['width']
        height = data['height']
        profile = data['profile']
        level = data['level']
        bitrate_vid = data['bitrate_vid']
        bitrate_aud = data['bitrate_aud']
        res = setup.setup_simcam(rotate, framerate, width, height, profile, level, bitrate_vid, bitrate_aud)
        if res[0]:
            resp.status = falcon.HTTP_201
            resp.text = json.dumps({"message": res[1]})
        else:
            resp.status = falcon.HTTP_500
            resp.text = json.dumps({"message": res[1]})

    def on_get(self, req, resp):
        """Handles GET requests"""
        res = setup.get_setup_simcam()
        if res[0] == 200:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps({"rotate": res[1], "framerate": res[2], "width": res[3], "height": res[4], "profile": res[5], "level": res[6], "bitrate_vid": res[7], "bitrate_aud": res[8]})
        elif res[0] == 404:
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"message": res[1]})
        else:
            resp.status = falcon.HTTP_500
            resp.text = json.dumps({"message": res[1]})

class RunRecSession(object):
    def on_post(self, req, resp):
        """Handles POST requests"""
        data = json.load(req.stream)
        name = data['name']
        time_limit = data['time']
        res = rec.rec_video(name, time_limit)
        if res[0]:
            resp.status = falcon.HTTP_200  # This is the default status
            resp.text = json.dumps({"volunteer name": name})
        else:
            resp.status = falcon.HTTP_200  # This is the default status
            resp.text = json.dumps({"status": res[1]})


class StopRecSession(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        path = rec.unrec_video()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = json.dumps({"path": path})


class StatusRecSession(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        status = rec.status_rec()
        if status:
            info = rec.info_rec()
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(
                {"pid": info[0], 'name': info[1], 'file': info[2], 'path': info[3], 'time': info[4], 'status': info[5]})
        else:
            resp.status = falcon.HTTP_200  # This is the default status
            resp.text = json.dumps({"status": status})


class UploadFile(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        status = upload.upload_file()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = json.dumps({"status": status})


class RunPreview(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        status = preview.run_preview()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = json.dumps({"status": status})


class StopPreview(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        status = preview.stop_preview()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = json.dumps({"status": status})


# falcon.API instances are callable WSGI apps
app = falcon.App()

# Resources are represented by long-lived class instances
my_setup_cloud = SetupSimCloud()
my_setup_cam = SetupSimCam()
run_rec = RunRecSession()
stop_rec = StopRecSession()
status_rec = StatusRecSession()
upload_file = UploadFile()
run_preview = RunPreview()
stop_preview = StopPreview()

# things will handle all requests to the '/things' URL path
app.add_route('/setup/cloud', my_setup_cloud)
app.add_route('/setup/cam', my_setup_cam)
app.add_route('/rec', run_rec)
app.add_route('/unrec', stop_rec)
app.add_route('/status', status_rec)
app.add_route('/upload', upload_file)
app.add_route('/preview', run_preview)
app.add_route('/unpreview', stop_preview)
