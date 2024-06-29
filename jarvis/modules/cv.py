import cv2
import face_recognition
from email.header import decode_header

# Load the face detection model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load your face encoding
my_image = face_recognition.load_image_file('my_face.jpg')
my_face_encoding = face_recognition.face_encodings(my_image)[0]
# Function to detect and recognize face
def detect_and_recognize_face():
    cap = cv2.VideoCapture(0)
    face_recognized = False

    while not face_recognized:
        ret, frame = cap.read()
        rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB

        # Find all the faces and face encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([my_face_encoding], face_encoding)
            if match[0]:
                face_recognized = True
                break

        cv2.imshow('Face Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return face_recognized