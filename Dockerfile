# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Set environment variable to ensure that python output is sent straight to terminal (e.g. container log) without being first buffered and that you can see the output of your application (e.g. Django logs) in real time.
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Run collectstatic (Configure Django to serve its own static files)
# Use the --noinput flag to automatically agree to any prompts Django might throw during this command
RUN python manage.py collectstatic --noinput

# Expose port 8000 to allow communication to/from the server
EXPOSE 8000

# Start gunicorn with the module your_project_name.wsgi
# Replace 'your_project_name' with the actual name of your project
# E.g., If your Django project's name is 'mysite', then the command would be 'mysite.wsgi:application'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]

# To find your project name, look for the name of the directory that contains your wsgi.py file.
# This directory will be located inside your project where your settings.py file is located.
