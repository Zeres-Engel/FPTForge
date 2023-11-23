import glob
import cv2

# import matplotlib.pyplot as plt

# from FPTvision.app import FaceAnalysis
# from FPTvision.utils import face_align
import queue

# Khởi tạo mô hình
# model = FaceAnalysis()
# model.prepare(ctx_id=0, det_size=(640, 480))

import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

# Truy cập webcam
cap1 = cv2.VideoCapture("rtsp://admin:Ditmemay@192.168.52.220:554/onvif1", cv2.CAP_FFMPEG)

# Thiết lập các thuộc tính cho webcam
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 420)  # Thiết lập chiều rộng khung hình
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)  # Thiết lập chiều cao khung hình
# cap.set(cv2.CAP_PROP_FPS, 30)  # Thiết lập tốc độ ghi hình (60 khung hình/giây)
count = 1
# while cap.isOpened():
#     print(cap.isOpened())

q = queue.Queue()
while True:
    # Đọc khung hình từ webcam
    ret, frame = cap1.read()
    print(ret)
    if not ret:
        break
    # Lật ngược khung hình (phản chiếu qua trục dọc)

    frame = cv2.flip(frame, 1)

    # Nhấn 'q' để chụp và 'n' để đóng
    # if cv2.waitKey(1) & 0xFF == ord('q'):

        # Dò tìm khuôn mặt
        # faces = model.get(frame)

        # max_area = 0
        # max_bbox = None
        # max_face = None
        # if faces and len(faces) > 0:
        #     # Find the face with the largest bounding box area
        #     for face in faces:
        #         bbox = face.bbox.astype(int)
        #         area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        #         if area > max_area:
        #             max_area = area
        #             max_bbox = bbox
        #             max_face = face
        # if max_bbox is not None:
        #     # norm crop
        #     face_image = face_align.norm_crop(frame, max_face.kps)
        #     cv2.imwrite(str(count)+".png", face_image)
        #     count +=1
        #     # if max_bbox is not None:
        #     cv2.rectangle(frame, (max_bbox[0], max_bbox[1]), (max_bbox[2], max_bbox[3]), (242, 111, 33), 2)
        #     cv2.putText(frame, f'Score: {max_face.det_score:.2f}', (max_bbox[0], max_bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)
    # Hiển thị kết quả trên cửa sổ OpenCV
    # elif cv2.waitKey(1) & 0xFF == ord('n'):
    #     break

    if not q.empty():
        try:
            q.get_nowait()  # discard previous (unprocessed) frame
        except q.Empty:
            pass
    q.put(frame)
    cv2.imshow('Face Detection', frame)

# Đóng camera và tắt tất cả cửa sổ OpenCV
cap1.release()
cv2.destroyAllWindows()