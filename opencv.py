import random
import cv2
import numpy as np
import time
import psycopg2
import requests
import tkinter as tk
from tkinter import font

# Set the URL of your Flask app
url = 'http://127.0.0.1:5000'

db_params = {
    'dbname': 'hackbu24',
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost',  
    'port': '5432'       
}

def get_data():
    global person, attempt, mode, historical_yes, historical_attempt
    person = person_entry.get()
    attempt = attempt_entry.get()
    mode = mode_var.get()
    historical_yes = historical_var.get()
    historical_attempt = historical_attempt_entry.get()

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

def mark_squares(event, x, y, flags, param):
    global ROIs, marking_squares
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(ROIs) < 3:
            ROIs.append((x -10, y -10, 20, 20))
            cv2.circle(prev_frame, (x, y), 10, (0, 255, 0), -1)
            cv2.imshow('Video', prev_frame)
            if len(ROIs) == 3:
                marking_squares = False
  
                
# Create a Tkinter window for data input
input_window = tk.Tk()
input_window.title("Data Input")

# Set the size of the input window
input_window.geometry("800x600")

# Entry fields for person name, attempt number, and mode
font_style = font.Font(family="Helvetica", size=12)

person_label = tk.Label(input_window, text="Enter the person name:", font=font_style)
person_label.pack()
person_entry = tk.Entry(input_window, font=font_style)
person_entry.pack(pady=5)

attempt_label = tk.Label(input_window, text="Enter the attempt number:", font=font_style)
attempt_label.pack()
attempt_entry = tk.Entry(input_window, font=font_style)
attempt_entry.pack(pady=5)

#  Radio buttons for selecting mode (0 for hand, 1 for legs)
mode_label = tk.Label(input_window, text="Select the mode:", font=font_style)
mode_label.pack()

mode_var = tk.IntVar()
hand_radio = tk.Radiobutton(input_window, text="Hand", variable=mode_var, value=0, font=font_style)
leg_radio = tk.Radiobutton(input_window, text="Legs", variable=mode_var, value=1, font=font_style)

hand_radio.pack()
leg_radio.pack(pady=10)

mode_label_h = tk.Label(input_window, text="Select historical training:", font=font_style)
mode_label_h.pack()
historical_var = tk.IntVar()
historical_yes_radio = tk.Radiobutton(input_window, text="Yes", variable=historical_var, value=0, font=font_style)
historical_no__radio = tk.Radiobutton(input_window, text="No", variable=historical_var, value=1, font=font_style)
historical_yes_radio.pack()
historical_no__radio.pack(pady=10)


historical_id = tk.Label(input_window, text="Enter the historical attempt number:", font=font_style)
historical_id.pack()
historical_attempt_entry = tk.Entry(input_window, font=font_style)
historical_attempt_entry.pack(pady=5)




# Button to confirm input and start the webcam
confirm_button = tk.Button(input_window, text="Confirm", command=lambda: (get_data(), input_window.destroy()), font=font_style)
confirm_button.pack(pady=10)

# Open webcam capture after closing the Tkinter input window
input_window.protocol("WM_DELETE_WINDOW", lambda: (cap.release(), cv2.destroyAllWindows(), input_window.destroy()))

# Start the Tkinter event loop
input_window.mainloop()

window_name = 'Video'



# Open webcam capture
print("Starting in 2 seconds...")
print(person, attempt, mode, historical_yes, historical_attempt)
time.sleep(2)



cap = cv2.VideoCapture(0)  # 0 corresponds to the default camera (you can change it if you have multiple cameras)


# Create a resizable window
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Set the initial size of the window (optional)
cv2.resizeWindow(window_name, 1200, 1200)  

# Read the first frame to initialize variables
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
ROIs = []
marking_squares = True

# cv2.namedWindow('Video')
cv2.setMouseCallback('Video', mark_squares)

while marking_squares:
    cv2.imshow('Video', prev_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

roi_colors = [prev_frame[y:y+h, x:x+w] for (x, y, w, h) in ROIs]
# Variables for storing timestamps of color changes
timestamps = [0] * len(ROIs)

current_random_no = random.randint(1, 3)
print(current_random_no)
all_data = []

if historical_yes == 1:
    # Main loop
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        # Track ROIs

        corners = track_ROIs(frame, ROIs)
        # frame = cv2.flip(frame,1)
        # Draw rectangles around the ROIs
        for i, (x, y, w, h) in enumerate(ROIs):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if current_random_no == i + 1:
                cv2.putText(frame, str(i + 1), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(frame, str(i + 1), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
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
                data = {'value': current_random_no}
                response = requests.put(url, json=data)

                # Print the response
                print(response.status_code)
                print(response.json())

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
        if len(all_data) == 30 or cv2.waitKey(25) & 0xFF == ord('q'):
            # add data to postgres db
            conn = establish_db_connection()
            cur = conn.cursor()
            for d in all_data:
                # Example: Inserting data into the table
                insert_data_query = "INSERT INTO athlete (person, attempt, time, point, mode) VALUES (%s, %s, %s, %s, %s);"
                data_to_insert = (person, attempt, d[0], d[1], "mode"+ str(mode))

                cur.execute(insert_data_query, data_to_insert)

                # Commit the transaction to save changes
                conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()
            break
else:
    rows = []
    try:
        conn = establish_db_connection()
        cur = conn.cursor()
            
        # Select all rows from the 'athlete' table
        select_data_query = f"SELECT * FROM athlete where attempt = {historical_attempt};"
        cur.execute(select_data_query)

        # Fetch all rows
        rows = cur.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)

    except psycopg2.Error as e:
        print("Error executing SQL query:", e)
    # Main loop
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        # Track ROIs

        corners = track_ROIs(frame, ROIs)
        # frame = cv2.flip(frame,1)
        # Draw rectangles around the ROIs
        for i, (x, y, w, h) in enumerate(ROIs):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if current_random_no == i + 1:
                cv2.putText(frame, str(i + 1), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(frame, str(i + 1), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
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
                data = {'value': current_random_no}
                response = requests.put(url, json=data)

                # Print the response
                print(response.status_code)
                print(response.json())

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
        if len(all_data) == 30 or cv2.waitKey(25) & 0xFF == ord('q'):
            # add data to postgres db
            conn = establish_db_connection()
            cur = conn.cursor()
            for d in all_data:
                # Example: Inserting data into the table
                insert_data_query = "INSERT INTO athlete (person, attempt, time, point, mode) VALUES (%s, %s, %s, %s, %s);"
                data_to_insert = (person, attempt, d[0], d[1], "mode"+ str(mode))

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