import cv2
from datetime import datetime

timestamp = datetime.now().strftime("%H%M%S")


def capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    frame = cv2.imwrite(frame, f"{timestamp}_num.png")
    cap.release()
    cv2.destroyAllWindows()


def main():
    capture()


if __name__ == "__main__":
    main()
