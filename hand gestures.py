import cv2
import mediapipe as mp
import pyautogui
import math
import threading
import tkinter as tk

# Flags controlled by GUI
enable_left_click = tk.BooleanVar(value=True)
enable_right_click = tk.BooleanVar(value=True)
enable_drag = tk.BooleanVar(value=True)
enable_scroll = tk.BooleanVar(value=True)

# Gesture tracking states
dragging = False
clicking = False
right_clicking = False

# Create the GUI in a separate thread
def create_gui():
    root = tk.Tk()
    root.title("Gesture Controls")
    root.geometry("250x200")

    tk.Checkbutton(root, text="Enable Left Click", variable=enable_left_click).pack(anchor='w')
    tk.Checkbutton(root, text="Enable Right Click", variable=enable_right_click).pack(anchor='w')
    tk.Checkbutton(root, text="Enable Drag", variable=enable_drag).pack(anchor='w')
    tk.Checkbutton(root, text="Enable Scroll", variable=enable_scroll).pack(anchor='w')

    tk.Label(root, text="Close this window to stop gesture control.", fg="red").pack(pady=10)
    root.mainloop()

# Start the GUI in a new thread
threading.Thread(target=create_gui, daemon=True).start()

# MediaPipe setup
cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            lm = hand_landmarks.landmark
            index_tip = lm[8]
            thumb_tip = lm[4]
            middle_tip = lm[12]
            ring_tip = lm[16]

            x = int(index_tip.x * frame_w)
            y = int(index_tip.y * frame_h)
            screen_x = int(index_tip.x * screen_w)
            screen_y = int(index_tip.y * screen_h)
            pyautogui.moveTo(screen_x, screen_y)
            cv2.circle(frame, (x, y), 10, (0, 255, 255), -1)

            # Distances
            dist_thumb_index = math.hypot(x - int(thumb_tip.x * frame_w), y - int(thumb_tip.y * frame_h))
            dist_thumb_middle = math.hypot(int(middle_tip.x * frame_w) - int(thumb_tip.x * frame_w),
                                           int(middle_tip.y * frame_h) - int(thumb_tip.y * frame_h))

            # Left Click
            if enable_left_click.get() and dist_thumb_index < 40 and dist_thumb_middle > 50:
                if not clicking:
                    clicking = True
                    pyautogui.click()
                    cv2.putText(frame, 'Left Click', (x + 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                clicking = False

            # Right Click
            if enable_right_click.get() and dist_thumb_middle < 40:
                if not right_clicking:
                    right_clicking = True
                    pyautogui.rightClick()
                    cv2.putText(frame, 'Right Click', (x + 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            else:
                right_clicking = False

            # Dragging
            if enable_drag.get() and dist_thumb_index < 40:
                if not dragging:
                    dragging = True
                    pyautogui.mouseDown()
                    cv2.putText(frame, 'Dragging', (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                if dragging:
                    dragging = False
                    pyautogui.mouseUp()

            # Scroll
            ring_y = int(ring_tip.y * frame_h)
            if enable_scroll.get() and ring_y > frame_h * 0.7:
                if y < frame_h * 0.3:
                    pyautogui.scroll(20)
                    cv2.putText(frame, 'Scroll Up', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                elif y > frame_h * 0.7:
                    pyautogui.scroll(-20)
                    cv2.putText(frame, 'Scroll Down', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Gesture Mouse Control", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
