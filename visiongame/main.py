# 初始化和设置
# 导入所需的库，并初始化摄像头。我们设置摄像头的分辨率为1280x720，这是游戏窗口的大小。
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# 初始化攝影機
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # 設定影像寬度
cap.set(4, 721)   # 設定影像高度

# 假設遊戲窗口大小為 1280x720
game_width = 1280
game_height = 721
block_width = 35
block_height = 186
ball_width = 3

# 加载游戏资源,游戏的背景、球拍和球的图像。这些资源存储在本地文件夹中，并在游戏中用作视觉元素。
# 讀取背景圖像尺寸
imgBackground = cv2.imread("Resources/Background.png")

# 讀取球拍圖像
imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

# 讀取球圖像尺寸
imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
#imgBall = cv2.resize(imgBall, (int(game_width * 0.04), int(game_width * 0.04)))  # 保持球為正圓形，寬度和高度相同

# 讀取gameOver圖像尺寸
imgGameOver = cv2.imread("Resources/gameOver.png")
imgGameOver = cv2.resize(imgGameOver, (game_width, game_height))


# 手部檢測器, 用于实时检测和跟踪游戏者的手部位置
detector = HandDetector(detectionCon=0.8, maxHands=2)

# 變數初始化
ballPos = [100, 100]  # 球的位置
speedX = 15           # 球在X方向的速度
speedY = 15           # 球在Y方向的速度
gameOver = False      # 遊戲結束標誌
score = [0, 0]        # 計分板
# 在變量初始化部分添加一個新變量來跟蹤上次增加速度時的總分
last_speed_increase_total_score = 0

# 游戏逻辑,在游戏的主循环中，处理图像帧，检测手部，根据手部位置更新球拍位置，并控制球的运动。
while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)  # 水平翻轉影像
    imgRaw = img.copy()     # 原始影像副本

    # 檢測手部和其標誌
    hands, img = detector.findHands(img, flipType=False)  # 檢測手部並繪製標誌

    # 確保背景圖像是三通道
    if len(imgBackground.shape) == 2:  # 如果是灰度圖
        imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_GRAY2BGR)
    elif imgBackground.shape[2] == 4:  # 如果是帶有透明通道的圖
        imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGRA2BGR)

    # 再次調整背景圖像尺寸以確保匹配
    imgBackground = cv2.resize(imgBackground, (img.shape[1], img.shape[0]))

    # 嘗試再次合成圖像
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    # 檢測到手部後，根據手部的位置設置球拍位置
    # 如果球触碰到屏幕的边缘，它会反弹。如果球超出屏幕边界，则游戏结束。
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']  # 手的邊界框
            h1, w1, _ = imgBat1.shape
            y1 = y - h1 // 2
            y1 = np.clip(y1, 23, 353)  # 限制球拍的垂直位置，避免超出遊戲窗口

            if hand['type'] == "Left":  # 左手
                img = cvzone.overlayPNG(img, imgBat1, (58, y1))  # 更新左手球拍的位置
                # 檢查球是否在左手球拍的邊界框內
                if 57 <= ballPos[0] <= 57 + w1 and y1 <= ballPos[1] <= y1 + h1:
                    speedX = -speedX  # 反彈
                    ballPos[0] += 30  # 調整球的位置以避免連續碰撞
                    score[0] += 1     # 左手玩家得分

            if hand['type'] == "Right":  # 右手
                img = cvzone.overlayPNG(img, imgBat2, (1186, y1))  # 更新右手球拍的位置
                # 檢查球是否在右手球拍的邊界框內
                if 1156 <= ballPos[0] <= 1156 + w1 and y1 <= ballPos[1] <= y1 + h1:
                    speedX = -speedX  # 反彈
                    ballPos[0] -= 30  # 調整球的位置以避免連續碰撞
                    score[1] += 1     # 右手玩家得分
    # 遊戲結束判斷
    if ballPos[0] < 40 or ballPos[0] > 1200:
        gameOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(img, str(score[1] + score[0]).zfill(2), (592, 385), cv2.FONT_HERSHEY_COMPLEX,
                    2.5, (200, 0, 200), 5)  # 顯示總得分

    else:
        # 移動球
        if ballPos[1] >= 500 or ballPos[1] <= 10:
            speedY = -speedY  # 垂直反彈

        ballPos[0] += speedX
        ballPos[1] += speedY

        # 繪製球
        img = cvzone.overlayPNG(img, imgBall, ballPos)

        cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)  # 左側得分
        cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)  # 右側得分

        # 更新得分邏輯
        # 得分和速度调整
        # 当球拍接触到球时，玩家得分增加
        total_score = score[0] + score[1]
        if total_score % 5 == 0 and total_score != 0 and total_score != last_speed_increase_total_score:
            speedX += 5 if speedX > 0 else -5  # 根據當前X方向速度的符號增加速度
            speedY += 5 if speedY > 0 else -5  # 根據當前Y方向速度的符號增加速度
            last_speed_increase_total_score = total_score  # 更新上次增加速度時的總分

    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))  # 縮放原始影像並顯示在左下角

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):  # 按 'q' 鍵退出遊戲
        break
    if key == ord('r'):  # 按'r' 重置遊戲
        ballPos = [100, 100]
        speedX = 15
        speedY = 15
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("Resources/gameOver.png")  # 重新載入遊戲結束圖片



