#!/bin/bash

echo "Shell script started"

export FLASK_APP=app

cd /home/COMP639PRJ2RAR/COMP639_Project_2_RAR || { echo "Directory not found"; exit 1; }

# Check if virtual environment folder exists
if [ ! -d "v-env" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv v-env
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
./home/COMP639PRJ2RAR/COMP639_Project_2_RAR/v-env/bin/activate

# Execute the flask custom cli command
flask scheduler

echo "Shell script completed"