from DoAn.myPose import myPose
import pyautogui
import cv2
import cvzone
import threading
from multiprocessing import Queue

def control_kyboard(q):
    global game_started
    global count
    global LRUD_old
    global reps
    global calo

    while True:
        if q.empty() != True:
            LRUD = q.get()
            if LRUD:
                if LRUD_old != LRUD or (LRUD == LRUD_old and count > 8):
                    count = 0
                    if LRUD == "left":
                        pyautogui.keyDown('left')
                        pyautogui.keyUp('left')
                    elif LRUD == "right":
                        pyautogui.keyDown('right')
                        pyautogui.keyUp('right')
                    elif LRUD == "up":
                        pyautogui.keyDown('up')
                        pyautogui.keyUp('up')
                    else:
                        pyautogui.keyDown('down')
                        pyautogui.keyUp('down')
                    reps += 1
                    if reps % 4 == 0 and reps != 0:
                        calo += 1
                elif LRUD == LRUD_old:
                    count += 1
                LRUD_old = LRUD

def processCamera(cap, q, pose):
    """
    Xứ lý frame mỗi khung hình, kiểm tra trạng thái người chơi
    :param cap:
    :param q:
    :param pose:
    :return:
    """
    global game_started
    global center_box
    global LRUD_old
    global calo
    global reps
    global clap_duration
    global message

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        image, result = pose.dectectPose(image)
        image, checkpoint = pose.getCheckPoint(image, result, center_box)

        CLAP = pose.checkClap(image, result)
        if CLAP:
            if CLAP == "Y":
                clap_duration += 1
                if clap_duration >= 10:
                    if game_started:
                        pyautogui.press('space')
                        # print("Space")
                    else:
                        game_started = True
                        pyautogui.click(x=720, y=560, button="left")
                        message = ""
                        # print("Click in display")
                    clap_duration = 0
            else:
                clap_duration = 0
        if game_started:
            # if checkpoint[0] < 640 and checkpoint[1] < 480 and checkpoint is not None:
            LRUD, center_box = pose.checkPose_LRUD(checkpoint, center_box)
            q.put(LRUD)
        image = cv2.flip(image, 1)
        """
            scale: độ to nhỏ của chữ
            thickness: độ dày của chữ
            offset: độ to, nhỏ  của box chữa chữ
        """
        cvzone.putTextRect(image, f"Reps: {reps}", (30, 30), scale=1, thickness=1, offset=15, colorR=(0, 0, 0))
        cv2.putText(image, f"{message}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=(0, 0, 0), thickness= 1)
        cvzone.putTextRect(image, f"Stage: {LRUD_old}", (30, 80), scale=1, thickness=1, offset=15, colorR=(0, 0, 0))
        cvzone.putTextRect(image, f"Colo: {calo}", (30, 130), scale=1, thickness=1, offset=15, colorR=(0, 0, 0))
        cv2.imshow("Camera Is Open", image)
        cv2.waitKey(1)
    cap.release()
    cv2.destroyWindow()
if __name__ == '__main__':
    # khởi tạo camera và pose
    cap = cv2.VideoCapture(0)
    pose = myPose()
    # setup lại khung hình cho camera: 3-image_width, 4-image_height, 5-FPS
    img_height, img_width = 480, 640
    cap.set(3, img_width)
    cap.set(4, img_height)
    cap.set(5, 60)
    """
        Khởi tạo các thông số:
        LRUD: Nonen -> ban đầu chưa dịch chuyển nên chúng ta lưu trạng thái là None
        LRUD_old: Nonen -> Lưu lại trạng thái trước, khởi tạo ban đầu là None vì thực hiện hành động
        count: biến đếm, nếu trong 8 khung hình mà trạng thái dịch chuyển vẫn dữ nguyên thì
               không thực hiện điều khiển nhân bàn phím ở trạng thái đó.
        reps: biến đếm, thực hiện được bao nhiêu trạng thái
        calo: biến tính lượng calo người chơi tiêu thụ: reps / 4
        game_started: Kiểm tra trạng thái game: đã bắt đầu hay chưa, hay đã kết thúc. (True đã bắt đầu, False: chưa bắt đầu)
        clap_duration: biến đếm số khung hình mà người chơi chắp tay vào 
    """
    LRUD = "None"
    LRUD_old = "None"
    count = 1
    reps = 0
    calo = 0
    game_started = False
    clap_duration = 0
    message = "Please Clap Your Hands And Hole 5 Seconds"

    """
        Vẽ một hình chữ nhật làm vùng ngưỡng:
        center_point: tâm hình chữ nhật -> khởi tạo ban đầu là điểm chính giữa khung hình
        center_box: lưu trữ tọa độ điểm đâu, và điểm cuối hình chữ nhật.
    """
    center_point = (img_width // 2, img_height // 2 + 80)
    center_box = [(center_point[0] + 110, center_point[1] - 65),
                  (center_point[0] - 110, center_point[1] + 65)]
    # khởi tạo hàng đợi Queue để lưu trữ biến LRUD được kiểm tra trong mỗi khung hình
    q = Queue()
    #Tạo và chạy hai luồng:
    #Luồng chỉ chạy và xử lý ảnh
    thread_process_camera = threading.Thread(target=processCamera, args=(cap, q, pose))
    #Luồng chỉ xử lý điều khiển bàn phìm
    thread_control_keyboard = threading.Thread(target=control_kyboard, args=(q, ))

    thread_process_camera.start()
    thread_control_keyboard.start()




