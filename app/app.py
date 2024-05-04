import json
import falcon
from utils import Upload, Rec, Preview

rec = Rec()
preview = Preview()
upload = Upload()


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
run_rec = RunRecSession()
stop_rec = StopRecSession()
status_rec = StatusRecSession()
upload_file = UploadFile()
run_preview = RunPreview()
stop_preview = StopPreview()

# things will handle all requests to the '/things' URL path
app.add_route('/rec', run_rec)
app.add_route('/unrec', stop_rec)
app.add_route('/status', status_rec)
app.add_route('/upload', upload_file)
app.add_route('/preview', run_preview)
app.add_route('/unpreview', stop_preview)
