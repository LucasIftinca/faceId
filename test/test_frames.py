import cv2
import time

def test_frames():
    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS detectat: {fps}")
    cap.set(cv2.CAP_PROP_FPS, 10)
    nr=0
    t1=time.time()
    while nr<100:
        ret, frame = cap.read()
        if not ret:
            break
        nr+=1
    t2=time.time()
    fps=nr/(t2-t1)
    print(f"FPS real: {fps}")
    cap.release()
    cv2.destroyAllWindows
    
if __name__ == "__main__":
    test_frames()