# https://blog.csdn.net/weixin_43191954/article/details/124056998 
# "Recently, Yushu (Unitree) officially updated the Go1 software so that the camera can be transmitted remotely, and wirelessly" 

# On each Jetson edit the following files, and change the address 192.168.12.10, and set to your preferred address. 

# For example I have an RF mesh radio plugged into the dogs ethernet port, and a remote viewing PC on the mesh with the address 192.168.123.96
#
# As such I have edited the yaml files as follows:
# /home/unitree/Unitree/autostart/imageai/mLComSystemFrame/config/mqMNConfig.yaml:udpHost: "192.168.123.96"
# /home/unitree/Unitree/autostart/imageai/mLComSystemFrame/config/mqSNNLConfig.yaml:udpHost: "192.168.123.96"
# /home/unitree/Unitree/autostart/imageai/mLComSystemFrame/config/mqSNNRConfig.yaml:udpHost: "192.168.123.96"

import cv2

# Set this address to the viewing PC IP address
udpstrPrevData = "udpsrc address=192.168.123.96" + " port=" 
udpPORT = [9101, 9102, 9103, 9104, 9105]
udpstrBehindData = " ! application/x-rtp,media=video,encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
labels = ["Front", "Chin", "Left Side", "Right Side", "Bottom"]

cams = [cv2.VideoCapture(udpstrPrevData +  str(port) + udpstrBehindData) for port in udpPORT]

# Read from the first camera to get the window size
ret, image = cams[0].read()
height, width = image.shape[:2]

while True:
    for i, cam in enumerate(cams):
        ret, image = cam.read()
        if image is not None:
            cv2.namedWindow(labels[i], cv2.WINDOW_NORMAL)
            # Define window positions according to their labels
            if labels[i] == "Front":
                cv2.moveWindow(labels[i], width, 0)
            elif labels[i] == "Chin":
                cv2.moveWindow(labels[i], width, height)
            elif labels[i] == "Left Side":
                cv2.moveWindow(labels[i], 0, height)
            elif labels[i] == "Right Side":
                cv2.moveWindow(labels[i], 2*width, height)
            elif labels[i] == "Bottom":
                cv2.moveWindow(labels[i], width, 2*height)
            cv2.imshow(labels[i], image)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit after reading
        break

for cam in cams:
    cam.release()

cv2.destroyAllWindows()


