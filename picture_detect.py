import cv2  
import numpy as np  

# Load the image  
image = cv2.imread('gb-20241226-7.png')  

# Convert to grayscale  
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  

# Apply binary thresholding  
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  

# Find contours  
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  

# Loop through contours and detect long horizontal rectangles  
for cnt in contours:  
    x, y, w, h = cv2.boundingRect(cnt)  

    # Define criteria for a long horizontal rectangle  
    aspect_ratio = w / float(h)  
    if aspect_ratio > 5 and w > 50:  # You can adjust the aspect ratio and size thresholds  
        # Draw rectangle on the original image  
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  

        # Annotate the coordinates of upper-left and lower-left corners  
        upper_left_text = f'({x}, {y})'  
        lower_left_text = f'({x}, {y + h})'  

        cv2.putText(image, upper_left_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 100, 0), 1)  
        cv2.putText(image, lower_left_text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 100, 0), 1)  

# Save or display the annotated image  
cv2.imwrite('annotated_image.png', image)  
cv2.imshow('Annotated Image', image)  
cv2.waitKey(0)  
cv2.destroyAllWindows()  