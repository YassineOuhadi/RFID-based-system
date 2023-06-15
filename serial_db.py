#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 22:00:02 2023
@author: yassine
"""

import serial
import psycopg2
import datetime

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="attendance-db.c61cjdfm6rpa.us-east-1.rds.amazonaws.com",
    database="Attendance_DB",
    user="postgres",
    password="postgres"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Open Serial port
ser = serial.Serial('/dev/ttyUSB1', 9600)

# Read RFID codes and class name from Serial port and write them to PostgreSQL
while True:
    data = ser.readline().strip()

    # Decode the bytes object to string
    data_str = data.decode('utf-8')

    # Split the data into RFID code and class name
    rfid_code_str, class_name = data_str.split(',')

    # Find the user with the RFID code
    cur.execute("SELECT * FROM \"user\" WHERE rfid = %s", (rfid_code_str,))
    user = cur.fetchone()

    if user:
        # User found, insert their presence
        seance_fk = 17  # Use the existing seance ID or change it accordingly
        entry_time = datetime.datetime.now().time()

        # Check if the user's role is "student"
        if user[8] == "STUDENT":
            is_validate = True  # If user is a student, set is_validate to True
        else:
            is_validate = False  # For other roles, set is_validate to False

        cur.execute("INSERT INTO \"presence\" (seance_fk, user_fk, entry_time, is_validate) VALUES (%s, %s, %s, %s)",
                    (seance_fk, user[0], entry_time, is_validate))
        conn.commit()

        message = "RFID code {}, date {}, time {}, class {} written to PostgreSQL".format(
            rfid_code_str, datetime.datetime.now().strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%H:%M:%S"), class_name)
        print(message)

        # Send message to Arduino via Serial
        ser.write(message.encode())
    else:
        print("User not found for RFID code: {}".format(rfid_code_str))

# Close the database connection and Serial port when done
cur.close()
conn.close()
ser.close()
