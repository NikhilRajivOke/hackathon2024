import random
import cv2
import numpy as np
import time
import psycopg2

db_params = {
    'dbname': 'hackbu24',
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost',  
    'port': '5432'       
}

def establish_db_connection():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        return None

# Function to track ROIs
def track_ROIs(frame, ROIs):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Define the parameters for the Shi-Tomasi corner detection
    corners = []
    max_corners = 10
    quality_level = 0.3
    min_distance = 7
    block_size = 7
    
    for (x, y, w, h) in ROIs:
        # Crop the ROI from the grayscale frame
        roi_gray = gray[y:y+h, x:x+w]
        
        # Use Shi-Tomasi corner detection to find corners in the ROI
        roi_corners = cv2.goodFeaturesToTrack(roi_gray, max_corners, quality_level, min_distance, blockSize=block_size)
        
        # Adjust the corners' coordinates to the entire frame
        if roi_corners is not None:
            roi_corners += (x, y)
        
        corners.append(roi_corners)
    
    return corners

person = input("Enter the person name: ")
attempt = int(input("Enter the attempt number: "))
# Open webcam capture
cap = cv2.VideoCapture(0)  # 0 corresponds to the default camera (you can change it if you have multiple cameras)

# Read the first frame to initialize variables
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
ROIs = []
marking_squares = True

def mark_squares(event, x, y, flags, param):
    global ROIs, marking_squares
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(ROIs) < 3:
            ROIs.append((x, y, 20, 20))
            cv2.circle(prev_frame, (x, y), 10, (0, 255, 0), -1)
            cv2.imshow('Video', prev_frame)
            if len(ROIs) == 3:
                marking_squares = False

cv2.namedWindow('Video')
cv2.setMouseCallback('Video', mark_squares)

while marking_squares:
    cv2.imshow('Video', prev_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

roi_colors = [prev_frame[y:y+h, x:x+w] for (x, y, w, h) in ROIs]
# Variables for storing timestamps of color changes
timestamps = [0] * len(ROIs)
print("Starting Cam in 2 seconds..")
time.sleep(2)
current_random_no = random.randint(1, 3)
print(current_random_no)
all_data = []
# Main loop
while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break
    
    # Track ROIs

    corners = track_ROIs(frame, ROIs)
    
    # Draw rectangles around the ROIs
    for i, (x, y, w, h) in enumerate(ROIs):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, str(i + 1), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # Draw circles for each corner within ROIs
    # for roi_corners in corners:
    #     if roi_corners is not None:
    #         for corner in roi_corners:
    #             x, y = corner.ravel()
    #             cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Track changes in color within ROIs
    for i, roi_color in enumerate(roi_colors):
        # Crop the ROI from the frame
        roi = frame[ROIs[i][1]:ROIs[i][1]+ROIs[i][3], ROIs[i][0]:ROIs[i][0]+ROIs[i][2]]
        
        # Calculate mean absolute difference between current and previous ROI
        diff = np.mean(np.abs(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32) - prev_gray[ROIs[i][1]:ROIs[i][1]+ROIs[i][3], ROIs[i][0]:ROIs[i][0]+ROIs[i][2]].astype(np.float32)))
        
        # Define a threshold for detecting color changes (adjust as needed)
        threshold = 10
        
        # If the difference exceeds the threshold, consider it a color change
        if diff > threshold and (i + 1) == current_random_no:
            print(f"Color change detected in ROI {i+1} at timestamp: {timestamps[i]}")
            all_data.append([time.time(), current_random_no])
            random_number = random.randint(1, 3)
            while(random_number == current_random_no):
                random_number = random.randint(1, 3)
            current_random_no = random_number
            print(current_random_no)

            # Update timestamp for this ROI
            timestamps[i] = cap.get(cv2.CAP_PROP_POS_MSEC)
        
        # Update previous ROI color
        roi_colors[i] = roi
    
    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Update previous frame and grayscale image
    prev_frame = frame.copy()
    prev_gray = gray.copy()

    # Break the loop if 'q' is pressed
    if cv2.waitKey(25) & 0xFF == ord('q'):
        # add data to postgres db
        conn = establish_db_connection()
        cur = conn.cursor()
        for d in all_data:
            # Example: Inserting data into the table
            insert_data_query = "INSERT INTO athlete (person, attempt, time, point) VALUES (%s, %s, %s, %s);"
            data_to_insert = (person, attempt, d[0],d[1])

            cur.execute(insert_data_query, data_to_insert)

            # Commit the transaction to save changes
            conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()