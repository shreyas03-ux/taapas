from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import os
import time
import cv2
import numpy as np
import pyautogui
stop_recording = False

@login_required
def home(request):
    # This function can be simplified or can utilize session data as necessary
    sessions = request.session.get('sessions', [])
    current_session = request.session.get('current_session', '')

    return render(request, 'main/home.html', {
        'sessions': sessions,
        'current_session': current_session,
        'output': '',  # You can pass this based on your logic
        'error': '',   # You can pass this based on your logic
    })

def capture_screen():
    # Capture screenshot using PyAutoGUI and convert it to OpenCV format
    screen = np.array(pyautogui.screenshot())
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    return screen

# Global variable to keep track of whether to stop recording or not
stop_recording = False

@login_required
def record_screen(request):
    global stop_recording
    output = ""
    error = None
    current_session = request.session.get('current_session', None)
    sessions = request.session.get('sessions', [])

    if request.method == 'POST':
        # Handle new session creation
        if 'new_session' in request.POST:
            session_name = request.POST.get('session_name')
            if session_name:
                sessions = sessions or []
                sessions.append(session_name)
                request.session['sessions'] = sessions
                current_session = session_name
                request.session['current_session'] = current_session
            else:
                error = "Session name cannot be empty."

        # Handle session selection
        elif 'select_session' in request.POST:
            selected_session = request.POST.get('session')
            if selected_session in sessions:
                current_session = selected_session
                request.session['current_session'] = current_session
            else:
                error = "Selected session does not exist."

        # Start recording
        elif 'start_recording' in request.POST:
            duration = int(request.POST.get('duration', 10))
            timestamp = int(time.time())
            filename = f'screen_recording_{timestamp}.avi'
            filepath = os.path.join(settings.MEDIA_ROOT, filename)

            # Create media directory if it doesn't exist
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)

            frame_size = (1920, 1080)  # Adjust according to your screen resolution
            out = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(*'XVID'), 10, frame_size)

            start_time = time.time()

            # Capture screen frames
            while (time.time() - start_time) < duration and not stop_recording:
                screenshot = capture_screen()
                out.write(screenshot)

            out.release()

            if os.path.exists(filepath):
                stop_recording = False  # Reset the stop recording flag
                output = f'Download your file <a href="{filename}">here</a>.'
            else:
                error = "Error saving file."

        # Stop recording
        elif 'stop_recording' in request.POST:
            stop_recording = True
            return JsonResponse({'message': 'Recording stopped successfully'})

    return render(request, 'main/home.html', {
        'current_session': current_session,
        'sessions': sessions,
        'output': output,
        'error': error
    })

# Global variable to keep track of whether to stop recording or not


@login_required
def download_file(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    try:
        with open(filepath, 'rb') as f:
            response = HttpResponse(f, content_type="video/x-msvideo")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)