from flask import Flask, render_template, Response, url_for, request
import datetime
import cv2
import json
import numpy as np
from FPTvision.app import FaceAnalysis
from FPTvision.model_zoo import arcface_onnx
from FPTvision.utils import face_align
import queue
import threading

import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

# Khởi tạo mô hình
Detection = FaceAnalysis()
Detection.prepare(ctx_id=0, det_size=(640, 480))

Recognition = arcface_onnx.ArcFaceONNX()
Recognition.prepare(ctx_id=0)


app = Flask(__name__)

static_path = "static"
avatar_path = "static/avatar/"


# Đọc embeddings từ file JSON
with open('./data/AI17BH1.json', 'r') as json_file:
    embeddings_dict = json.load(json_file)
    

# Trọng số cho mỗi vector embedding
# WEIGHTS = [0.2, 0.2, 0.2, 0.2, 0.2]
# weight = 1

students_dict = {}

# spf = 1
# current_frame = 14

session = {}

def get_people():
    with open('app\people.json', 'r') as json_file:
        people = json.load(json_file)
    return people

model_cap = cv2.VideoCapture("rtsp://admin:toiyeufpt1@192.168.52.220:554/onvif1", cv2.CAP_FFMPEG)
model_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
model_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
model_cap.set(cv2.CAP_PROP_FPS, 30)

last_frame = None

def update_last_frame():
    global last_frame
    q = queue.Queue()
    while True:
        ret, frame = model_cap.read()
        if not ret:
            continue
        if not q.empty():
            try:
                q.get_nowait()  # discard previous (unprocessed) frame
            except q.Empty:
                pass
        q.put(frame)
        last_frame = frame

t = threading.Thread(target=update_last_frame)
t.daemon = True
t.start()

def generate_frames():
    global model_cap
    # global current_frame

    with open('app\emb1.json', 'r') as json_file:
        emb_dict = json.load(json_file)

    # def save_face_image(frame, kps, student_id, img_type="in"):
    #     """Lưu hình ảnh khuôn mặt được crop vào đường dẫn chỉ định."""
    #     face_image = face_align.norm_crop(frame, kps)
    #     img_path = f'app/static/img/avatars/{student_id}/{img_type}.png'
    #     cv2.imwrite(img_path, face_image)

    # def update_student_record(student_id, frame, kps, checkin=False):
    #     """Cập nhật thông tin check-in hoặc check-out cho sinh viên."""
    #     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     img_type = "in" if checkin else "out"
    #     save_face_image(frame, kps, student_id, img_type)
    #     if student_id in students_dict:
    #         if checkin:
    #             students_dict[student_id]["CheckInTime"] = now
    #         else:
    #             students_dict[student_id]["CheckOutTime"] = now
    
    # def _reader():
    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break
    #         if not q.empty():
    #             try:
    #                 q.get_nowait()  # discard previous (unprocessed) frame
    #             except queue.Empty:
    #                 pass
    #         q.put(frame)

    # def read():
    #     return q.get()

    while True:
        # ret, frame = model_cap.read()
        frame = last_frame
        # current_frame += 1
        # if (current_frame != 15):
            # continue
        # current_frame = 0
        # if not frame:
        #     break
        if frame is None:
            continue

        frame = cv2.flip(frame, 1)
        faces = Detection.get(frame)

        for face in faces:
        # if len(faces) > 0:
            # face = faces[0]

            detected_embedding = Recognition.get(frame, face)
            
            matched_id = None
            #TODO: Good max_similarity
            max_similarity = 0.53
            for people_id, embeddings in emb_dict.items():
                weighted_similarity = 0.0
                # print(people_id, len(embeddings))
                for i, vector in enumerate(embeddings):
                    similarity = Recognition.compute_sim(np.array(vector), detected_embedding)
                    weighted_similarity = similarity
                    # print('debug sim', weighted_similarity)

                if weighted_similarity > max_similarity:
                    matched_id = people_id
                    max_similarity = weighted_similarity

            if matched_id:
                print("max sim", max_similarity)
                if matched_id not in session:
                    session[matched_id] = {
                        "time": datetime.datetime.now()
                    }

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # model_cap.release()

def get_video_from_cam():
    global last_frame
    while True:
        frame = last_frame

        if frame is None:
            continue
        # if not ret:
            # break

        # frame = cv2.flip(frame, 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # cap.release()

@app.route('/peopleData')
def get_people_data():
    people = get_people()
    res = { 'data': [] }
    for id in people.keys():
        info = people[id]
        person = {
            'id': id,
            'full_name': info['full_name'],
            'avatar': avatar_path + id + info['name'] + ".png"
        }
        if id in session:
            person['attendance'] = True
            person['time'] = session[id]
        else:
            person['attendance'] = False
            person['time'] = None
        res['data'].append(person)
    # print("session", session)
    return res

@app.route('/StudentChecking')
def update_student_data():
    return students_dict

@app.route('/initdata')
def init_data():
    # students_dict = {}
    for key, value in embeddings_dict.items():
        student_id, full_name = key.split('-', 1)
        checkin_time = value.get("checkin_time", "N/A")
        checkout_time = value.get("checkout_time", "N/A")
        student_data = {
            "StudentID": student_id,
            "FullName": full_name,
            "Avatar": url_for('static', filename=f'img/avatars/{student_id}/avatar.png'),
            "CheckInImage": url_for('static', filename=f'img/avatars/{student_id}/in.png'),
            "CheckInTime": checkin_time,    
            "CheckOutImage": url_for('static', filename=f'img/avatars/{student_id}/out.png'),
            "CheckOutTime": checkout_time,
            "HandRissing": 0,
            "Status": 'Processing',
            "Frames": 0,
            "DistractiveFrames": 0, 
        }
        # Sử dụng StudentID làm khóa
        students_dict[student_id] = student_data
    return students_dict

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/classroom')
def classroom():
    return render_template('classroom.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.post('/register_new')
def register_new():
    request_data = request.get_json()
    idData = request_data["idData"]
    nameData = request_data["nameData"]
    fullNameData = request_data["fullNameData"]
    peopleData = {
        'name': nameData,
        'full_name': fullNameData
    }
    update_people_json(idData, peopleData)
    frame = last_frame
    faces = Detection.get(frame)

    max_area = 0
    max_bbox = None
    max_face = None
    if faces and len(faces) > 0:
        # Find the face with the largest bounding box area
        for face in faces:
            bbox = face.bbox.astype(int)
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            if area > max_area:
                max_area = area
                max_bbox = bbox
                max_face = face
    if max_bbox is not None:
        # norm crop
        face_image = face_align.norm_crop(frame, max_face.kps)
        path = "app/" + avatar_path + str(idData)+str(nameData)+".png"
        print("path", path)
        cv2.imwrite(path, face_image)
        emb_res = Recognition.get_feat(imgs = face_image)
        emb_res = emb_res[0]
        emb_res = emb_res.tolist()
        update_embeddings_dict(idData, emb_res)

    return { "msg": "ok" }

def update_people_json(id, peopleData):
    f = open("app\people.json")
    data = json.load(f)
    if id in data:
        print("already exist")
        return
    data[id] = {}
    data[id]['name'] = peopleData['name']
    data[id]['full_name'] = peopleData['full_name']
    with open("app\people.json", "w") as outfile: 
        json.dump(data, outfile)

def update_embeddings_dict(id, emb):
    f = open("app\emb1.json")
    data = json.load(f)
    if id not in data:
        data[id] = []
    data[id].append(emb)
    with open("app\emb1.json", "w") as outfile: 
        json.dump(data, outfile)
    print("register new: success", id)


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_video')
def get_video():
    return Response(get_video_from_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
