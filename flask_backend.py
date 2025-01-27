

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import cv2
from YOLO_Video import video_detection  # Import your YOLO model function

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Restrict CORS to React app origin

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for video upload
@app.route('/upload-video', methods=['POST'])
def upload_video():
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        app.logger.info(f"File uploaded successfully: {filepath}")
        return jsonify({'file_path': filepath}), 200

    except Exception as e:
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Route for streaming processed video
@app.route('/stream-video', methods=['GET'])
def stream_video():
    file_path = request.args.get('file_path')

    # Validate file path
    if not file_path or not os.path.exists(file_path):
        app.logger.error(f"File not found or invalid path: {file_path}")
        return jsonify({'error': 'File not found'}), 404

    try:
        # Generate video frames
        def generate_frames():
            app.logger.info(f"Processing video: {file_path}")
            for frame in video_detection(file_path):
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except Exception as e:
        app.logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Changed to host 0.0.0.0 and port 5000 to make it accessible from other services
    app.run(debug=True, host='0.0.0.0', port=5000)


# from flask import Flask, request, Response, jsonify
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import os
# import cv2
# from YOLO_Video import video_detection  # Import your YOLO model function

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Restrict CORS to React app origin

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Ensure upload folder exists
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Route for video upload
# @app.route('/upload-video', methods=['POST'])
# def upload_video():
#     try:
#         # Check if file is in the request
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file provided'}), 400

#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'}), 400

#         # Save the uploaded file
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         app.logger.info(f"File uploaded successfully: {filepath}")
#         return jsonify({'file_path': filepath}), 200

#     except Exception as e:
#         app.logger.error(f"Error uploading file: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500

# # Route for streaming processed video
# @app.route('/stream-video', methods=['GET'])
# def stream_video():
#     file_path = request.args.get('file_path')

#     # Validate file path
#     if not file_path or not os.path.exists(file_path):
#         app.logger.error(f"File not found or invalid path: {file_path}")
#         return jsonify({'error': 'File not found'}), 404

#     try:
#         # Generate video frames
#         def generate_frames():
#             app.logger.info(f"Processing video: {file_path}")
#             for frame in video_detection(file_path):
#                 _, buffer = cv2.imencode('.jpg', frame)
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

#         return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#     except Exception as e:
#         app.logger.error(f"Error processing video: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, request, Response, jsonify, send_file
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import os
# import cv2
# from YOLO_video import video_detection  # Import your YOLO model function

# app = Flask(__name__)
# CORS(app)  # Allow cross-origin requests
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Route for video upload
# @app.route('/upload-video', methods=['POST'])
# def upload_video():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file provided'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Save the uploaded file
#     filename = secure_filename(file.filename)
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)

#     return jsonify({'file_path': filepath}), 200

# # Route for streaming processed video
# @app.route('/stream-video', methods=['GET'])
# def stream_video():
#     file_path = request.args.get('file_path')
#     if not file_path or not os.path.exists(file_path):
#         return jsonify({'error': 'File not found'}), 404

#     def generate_frames():
#         for frame in video_detection(file_path):
#             _, buffer = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True)

