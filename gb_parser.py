
import numpy as np  
import cv2
import pytesseract
import pyautogui 
from pynput.keyboard import Key, Listener
import time 
import threading
import datetime

# Instruction to use
# Wait until Listener will start (message on a screen)
# Press Left Shift to start screen shoting
# Press Left Shift to stop screen shoting
# Press Right Shift to stop loop and start extract text messages
# close window after messages will be exported to file (message on a screen)


# Use picture_detect.py  to detect y coordinates
top_line=190  # y coordinate on top after which we have messages
bottom_line=962 # y coordinate at bottob above which we have messages
left_x_boundary=640
right_x_boundary=1900


chat_messages=[]
images=[]
long_images=[]
capturing = False
Breaks = False

def add_missing_part(text1, text2):  
    if text2 in text1:  
        return text1  

    # Find the longest suffix of text1 that is a prefix of text2  
    max_suffix_length = 0  
    for i in range(len(text1)):  
        if text1.endswith(text2[:i+1]):  
            max_suffix_length = i+1  

    # The missing part of text2  
    missing_part = text2[max_suffix_length:]  

    # Add the missing part to text1  
    updated_text1 = text1 + missing_part  
    return updated_text1  


def find_message_boundaries(image):  
    # Convert the image to grayscale  
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  

    # Threshold the image to get binary image of white regions  
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  

    # Find contours  
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  

    # Filter contours based on their rectangularity and area  
    filtered_boxes = []
    full_box = []
    top_box=[]
    min_area = 50  # Minimum area of a valid box  

    for contour in contours:  
        epsilon = 0.02 * cv2.arcLength(contour, True)  
        approx = cv2.approxPolyDP(contour, epsilon, True)  

        if len(approx) == 4:  # Check if the contour has 4 vertices (approximate rectangle)  
            x, y, w, h = cv2.boundingRect(approx)  
            area = cv2.contourArea(contour)                 
            #print(area)
            if area > min_area and x>500:  
                if len(top_box)==0:
                    top_box.append((x, y, w, h))
                elif top_box[0][2]<w:
                    top_box.pop()
                    top_box.append((x, y, w, h))
                    
    for contour in contours:  
        epsilon = 0.02 * cv2.arcLength(contour, True)  
        approx = cv2.approxPolyDP(contour, epsilon, True)  

        if len(approx) == 4:  # Check if the contour has 4 vertices (approximate rectangle)  
            x, y, w, h = cv2.boundingRect(approx)  
            area = cv2.contourArea(contour)  
            #cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2) 
            if area > min_area and x>500 and w<1000 and y>top_line+2 and y+h<bottom_line:  
                filtered_boxes.append((x, y, w, h))                      
                #print(f'{y+h}, {bottom_line}')
                

    # Sort the bounding boxes by their y-coordinate (top to bottom)  
    filtered_boxes = sorted(filtered_boxes, key=lambda x: x[1]) 
    
    if len(filtered_boxes)==0:
        #print(f'No messages found')
        full_box.append((left_x_boundary, top_line, right_x_boundary-left_x_boundary, bottom_line-top_line))
    
    for box in filtered_boxes:
        x, y, w, h = box  
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)    
    
    for box in top_box:
        x, y, w, h = box  
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)          
        
    for box in full_box:
        x, y, w, h = box  
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 50, 0), 2)          
    
    #cv2.line(image, (left_x_boundary, bottom_line), (right_x_boundary, bottom_line), (0, 0, 255), 2)
    #cv2.line(image, (left_x_boundary, top_line), (left_x_boundary, bottom_line), (0, 0, 255), 2)
    #cv2.line(image, (right_x_boundary, top_line), (right_x_boundary, bottom_line), (0, 0, 255), 2)
    #cv2.imshow('Detected Boxes', image)  
    #cv2.waitKey(0)  
    #cv2.destroyAllWindows()     
    #time.sleep(5)
    return filtered_boxes, top_box, full_box


def extract_text_from_image(image, lang='eng+rus'):    
    text = pytesseract.image_to_string(image , lang='eng+rus')  
    return text


# Function to capture screenshot and process image  
def capture_and_process():
    global images
    #print(f'Make a screen shot and process...')
    screenshot = pyautogui.screenshot()  
    image = np.array(screenshot)  
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  
      
    # Find message boundaries  
    message_boxes, top_box, full_box = find_message_boundaries(image)  
      
    # Process each message box  
    text_messages = []  
    for box in message_boxes:  
        x, y, w, h = box  
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        roi = image[y:y+h, x:x+w]
        images.append(roi)
    
    # Process full screen message
    if len(message_boxes)==0 and len(full_box)>0:
        x, y, w, h = full_box[0]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        roi = image[y:y+h, x:x+w]
        long_images.append(roi)        

    return 0

    
def on_press(key):
    global capturing
    global Breaks
    if key == Key.shift_l : # or key == Key.shift_r:        
        capturing = not capturing  
        print(f"Left Shift is pressed! Capturing: {capturing}")
        
    if key == Key.shift_r:        
        Breaks = not Breaks  
        print(f"Right Shift is pressed! Breaks: {Breaks}")        
        
def start_listener():  
    with Listener(on_press=on_press) as listener:  
        print("Listener started...")
        listener.join()
        #while not Breaks:  
        #    pass  
        #listener.stop()
        
        
def export_messages_to_file(messages):    
    d = datetime.datetime.today()
    today_str=d.strftime("%Y%m%d%H%m")  
    
    with open(f'.\\Export\\messages-{today_str}.txt', 'w', encoding='utf-8') as file:  
        file.write("Ты аналитик по облигациям и анализируешь открытые источники информации и формируешь заключения.\n")
        file.write("Ниже приведены сообщения специализированного чата по облигациям. Сделай анализ сообщений чата. Напиши:\n")
        file.write("Перечисли темы, которые обсуждались в чате.\n")
        file.write("Какие общие макроэкономические темы обсуждались ? Какие тренды они могут формировать или изменять? Как они могут повлиять на цены облигаций? \n")
        file.write("Какие торговые рекомендации были даны или сформулированы в чате? Детально напиши про это.\n")        
        file.write("Какие эмитенты обсуждались ?\n")
        file.write("Какие эмитенты, если такие были, были позитивно оценены и почему? Детально напиши про это.\n")
        file.write("Какие эмитенты, если такие были, были негативно оценены и почему? Детально напиши про это.\n")
        file.write("Какую оценку для рынка можно дать на основании анализа сообщений и их тональности ?\n\n\n")
        for m in messages:  
            file.write(m + '\n') 
    return 0
    
        
if __name__ == "__main__":  
    # Load the image  
    pytesseract.pytesseract.tesseract_cmd = r'd:\Tools\Tesseract\tesseract.exe'
    text_messages=[]    
    full_screen_messages=""
    #image = cv2.imread('gb-20241226.png')
    
    # Start listener in a separate thread  
    listener_thread = threading.Thread(target=start_listener)  
    listener_thread.start() 
        
    #print(f"Capturing: {capturing}")
    
    previous_screenshot = None  
    messages=[]   
  
    while not Breaks:
        #print(f"capturing: {capturing}")
        if capturing:  
            screenshot = pyautogui.screenshot()  
            current_image = np.array(screenshot)  
            current_image = cv2.cvtColor(current_image, cv2.COLOR_RGB2BGR)  
              
            if previous_screenshot is not None:  
                diff = cv2.absdiff(current_image, previous_screenshot)  
                non_zero_count = np.count_nonzero(diff)  
                if non_zero_count > 0:  # Change detected 
                    capture_and_process()
                    #messages=capture_and_process()  
                    #for m in messages:
                        #if m not in text_messages:
                            #text_messages.append(m)
                    previous_screenshot = current_image  
            else:  
                capture_and_process()
                #messages=capture_and_process()  
                #for m in messages: 
                    #if m not in text_messages:
                        #text_messages.append(m)
                previous_screenshot = current_image  

    print(f'Start processing images...')
    for i in images:
        text = extract_text_from_image(i) 
        #print(text)
        if text not in text_messages:
            text_messages.append(text)
            
    for i in long_images:
        text = extract_text_from_image(i) 
        #print(f'Full screen messages before update: \n {full_screen_messages}')
        #print(f'New text to be analyzed: \n {text}')
        full_screen_messages=add_missing_part(full_screen_messages, text)
        #print(f'New full text: \n {full_screen_messages}')
        #print('\n')

    text_messages.append(full_screen_messages) 
    #for m in text_messages:
        #print("---------")
        #print(m)
        #print("---------")
    export_messages_to_file(text_messages)
    print(f'Messages exported')
    listener_thread.join()
    
    
    
                
              
 