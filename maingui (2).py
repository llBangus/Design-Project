import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import pymongo
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np
import os,time
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
import serial
ser=serial.Serial('/dev/serial0',9600,timeout=1)
sys.setrecursionlimit(40000)
class LoginScreen(QWidget):
    login_successful = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        self.keyboard_shift_pressed = False
        # create a username label and input field
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        # create a password label and input field
        self.password_label = QLabel("One Time Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # create a virtual keyboard
        self.keyboard = QWidget()
        self.keyboard_layout = QGridLayout()
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0','<-', 
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 
            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 
            'Z', 'X', 'C', 'V', 'B', 'N', 'M', '_','-',
             'Del','Shift',
        ]
        positions = [(i, j) for i in range(5) for j in range(11)]
        for position, key in zip(positions, keys):
            if key == '<-':
                button = QPushButton(key)
                button.clicked.connect(lambda _, text=key: self.keyboard_backspace())
            elif key == 'Del':
                button = QPushButton(key)
                button.clicked.connect(lambda _, text=key: self.keyboard_delete())
            elif key == 'Shift':
                button = QPushButton(key)
                button.clicked.connect(lambda _, text=key: self.keyboard_shift())
            else:
                button = QPushButton(key)
                button.clicked.connect(lambda _, text=key: self.keyboard_click(text))
            button.setFocusPolicy(Qt.NoFocus)
            self.keyboard_layout.addWidget(button, *position)
        self.keyboard.setLayout(self.keyboard_layout)

        # create a login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)

        # create a layout for the login screen
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.keyboard)
        layout.addWidget(self.login_button)
        self.setLayout(layout)
        self.setGeometry(0, -10, 1025, 610)
    def keyboard_click(self, text):
        current_widget = self.focusWidget()
        

        if current_widget == self.username_input:
            current_text = self.username_input.text()
            self.username_input.setText(current_text + text.lower() if not self.keyboard_shift_pressed else current_text + text.upper())
        elif current_widget == self.password_input:
            current_text = self.password_input.text()
            self.password_input.setText(current_text + text.lower() if not self.keyboard_shift_pressed else current_text + text.upper())
        

    def keyboard_shift(self):
       
            
        if self.keyboard_shift_pressed == True:
            self.keyboard_layout.itemAtPosition(3, 7).widget().setStyleSheet(f"background-color: none;")
            self.keyboard_shift_pressed = False
        else:
            self.keyboard_layout.itemAtPosition(3, 7).widget().setStyleSheet(f"background-color: {'white'};")
            self.keyboard_shift_pressed = True

    def keyboard_backspace(self):
        current_widget = self.focusWidget()
        if current_widget == self.username_input:
            current_text = self.username_input.text()
            self.username_input.setText(current_text[:-1])
        elif current_widget == self.password_input:
            current_text = self.password_input.text()
            self.password_input.setText(current_text[:-1])

    def keyboard_delete(self):
        current_widget = self.focusWidget()
        if current_widget == self.username_input:
            self.username_input.setText('')
        elif current_widget == self.password_input:
            self.password_input.setText('')

    def check_login(self):
        try:
            # get the entered username and password
            self.username = self.username_input.text()
            password = int(self.password_input.text())
            client = pymongo.MongoClient("mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/?retryWrites=true&w=majority")
            # query the MongoDB Atlas database for the user with the entered username and password
            user = client.dropbox.userinfo.find_one({"User": self.username, "otp": password})

            # if a matching user was found, show the home screen and hide the login screen
            if user is not None:
                
                print(self.username)
                data=self.username
                self.login_successful.emit(data)
                home_screen = HomeScreen(data)
                home_screen.show()
                self.hide()
            else:
                # display an error message if the user's credentials are incorrect
                error_dialog = QMessageBox()
                error_dialog.setWindowTitle("Error")
                error_dialog.setText("Invalid username or password.")
                error_dialog.setIcon(QMessageBox.Warning)
                error_dialog.exec_()
        except Exception as e:
            # display an error message if there was an error connecting to the MongoDB Atlas database
            print(e)
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Could not connect to database. Please try again later.")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.exec_()


class HomeScreen(QWidget):
    def __init__(self, data):
        
        super().__init__()
        global cap,liveflag,bindname,lockflag,client,lockcheck,cap2
        lockcheck=0
        idvar="A1,"
        print(idvar)
        ser.write(idvar.encode())
        lockflag=1
        bindname = data
        self.userdata = data
        client = pymongo.MongoClient("mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/?retryWrites=true&w=majority")
        user = client.dropbox.userinfo.find_one({"User": self.userdata})
        query = {"User": self.userdata}
        new_data = {"$set": {"request_status": "rejected"}}
        client.dropbox.userinfo.update_one(query, new_data)
        liveflag=1
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Loop)
        self.timer.start()
        cap=cv2.VideoCapture(2)
        cap.set(3,640)
        cap.set(4,480)
        time.sleep(1)
        cap2=cv2.VideoCapture(0)
        cap2.set(3,640)
        cap2.set(4,480)
        time.sleep(0.1)
        self.i1=QtWidgets.QLabel(self)
        self.i1.setGeometry(60,50,300,300)
        self.disp=QtGui.QPixmap("/home/pi/Desktop/blackscreen.png")
        self.disp=self.disp.scaledToHeight(180)
        self.i1.setScaledContents(True)
        self.i1.setPixmap(self.disp)

        self.i2=QtWidgets.QLabel(self)
        self.i2.setGeometry(450,50,300,300) 
        self.i2.setScaledContents(True)
        self.i2.setPixmap(self.disp)

        self.recogbutton = QtWidgets.QPushButton("Analyze",self)
        self.recogbutton.clicked.connect(self.recogfunc)
        self.recogbutton.resize(100,60)
        self.recogbutton.move(350,420)
        self.recogbutton.setVisible(0)
        self.registerbutton = QtWidgets.QPushButton("Register",self)
        self.registerbutton.clicked.connect(self.registerfunc)
        self.registerbutton.resize(100,60)
        self.registerbutton.move(350,420)
        
        self.activatebutton = QtWidgets.QPushButton("Activate",self)
        self.activatebutton.clicked.connect(self.activatefunc)
        self.activatebutton.resize(100,60)
        self.activatebutton.move(350,520)
        
        self.palmbutton = QtWidgets.QPushButton("Palm",self)
        self.palmbutton.clicked.connect(self.palmfunc)
        self.palmbutton.resize(100,60)
        self.palmbutton.move(450,520)
        #self.trainbutton = QtWidgets.QPushButton("Save",self)
        #self.trainbutton.clicked.connect(self.trainfunc)
        #self.trainbutton.move(500,420)

        #self.lockerbutton = QtWidgets.QPushButton("Lock",self)
        #self.lockerbutton.clicked.connect(self.lockerfunc)
        #self.lockerbutton.move(700,420)

        

        self.a3=QtWidgets.QLabel('----------------',self)
        self.a3.move(300,380)
        self.a3.resize(300,30)
        self.a3.setText(f"Hi! Welcome {user['FullName']}")
        self.a4=QtWidgets.QLabel('Instructions:\n1. Place and align your face and palm on the camera.\n2. Press register and wait for it to complete.\n3. Press Activate if you already placed your package \nand ready to lock.',self)
        self.a4.move(600,420)
        self.a4.resize(400,400)
        self.a4.setAlignment(QtCore.Qt.AlignTop)
        self.setGeometry(0, -10, 1025, 610)
        self.show()
        #self.setGeometry(0, -10, 525, 410)
        QApplication.quit = self.exit
    def palmfunc(self):
        global cap2,bindname,x,y,w,h
        ret, frame = cap2.read()
      
                
        crop_img = frame[y:y+h, x:x+w]
        crop_img = cv2.resize(crop_img,(260,360),interpolation=cv2.INTER_AREA)
        folder="/home/pi/Desktop/users/"+str(bindname) +"/palm"
         

        try:
           
                    
            path, dirs, files = next(os.walk(folder))
            file_count = len(files)


            cv2.imwrite(str("/home/pi/Desktop/users/"+bindname)+"/palm/"
                        +str(bindname)+"_"+str(bindname)+"_"
                        +str(file_count)+".png",crop_img)
        except Exception as e:
            cv2.imwrite(str("/home/pi/Desktop/users/"+bindname)+"/palm/"
                        +str(bindname)+"_"
                        +str(file_count)+".png",crop_img)
            print(e)
    def activatefunc(self):
        global cap,face_recognizer
        idvar="B1,"
        print(idvar)
        ser.write(idvar.encode())
        def prepare_training_data(data_folder_path):
            dirs = os.listdir(data_folder_path)
            faces = []
            labels = []
            for dir_name in dirs:
                
                subject_dir_path = data_folder_path + "/" + dir_name
                subject_images_names = os.listdir(subject_dir_path)

                for image_name in subject_images_names:
                    print(image_name)
                    label = int(image_name.split("_")[0])        
                    image_path = subject_dir_path + "/" + image_name
                    image = cv2.imread(image_path,0)

                    
                    faces.append(image)
                    labels.append(label)
                    #print(faces)
                    #print(labels)
            return faces, labels
        faces, labels = prepare_training_data("/home/pi/Desktop/users")
        print("Total faces: ", len(faces))
        print("Total labels: ", len(labels))
        #face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer = cv2.face.FisherFaceRecognizer_create()
        face_recognizer.train(faces, np.array(labels))
        face_recognizer.write('/home/pi/Desktop/model_trained.yml')
        self.activatebutton.setVisible(0)
        self.a3.setVisible(0)
        self.a4.setVisible(0)
        self.registerbutton.setVisible(0)
        self.recogbutton.setVisible(1)
    def lockerfunc(self):
        global lockflag
        if lockflag==0:
            idvar="B1,"
            print(idvar)
            ser.write(idvar.encode())
            lockflag=1
        elif lockflag==1:
            idvar="B2,"
            print(idvar)
            ser.write(idvar.encode())
            lockflag=0
        idvar="C,"
        ser.write(idvar.encode())
        time.sleep(0.5)
        data= str(ser.readline())
        print(data)
    def recogfunc(self):
            global cap,face_recognizer
            face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/haarcascade_frontalface_default.xml')
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            #face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            face_recognizer = cv2.face.FisherFaceRecognizer_create()
            face_recognizer.read('/home/pi/Desktop/model_trained.yml')
            for (x,y,w,h) in faces:
               
                crop_img = gray[y:y+h, x:x+w]
                crop_img = cv2.resize(crop_img,(120,120),interpolation=cv2.INTER_AREA)
                cv2.imwrite('/home/pi/Desktop/crop_img.png',crop_img)
                label,confidence = face_recognizer.predict(crop_img)
                df = pd.read_csv('/home/pi/Desktop/userdata.csv')
                result = df.loc[df['ID'] == label, 'Name'].iloc[0]
                
                print(label)
                print(confidence)
                print(result)
                self.a3.setText("Welcome "+result+"!")
                if result == self.userdata:
                    idvar="B2,"
                    print(idvar)
                    ser.write(idvar.encode())
                    self.activatebutton.setVisible(1)
                    self.a3.setVisible(1)
                    self.a4.setVisible(1)
                    self.registerbutton.setVisible(1)
                    self.recogbutton.setVisible(0)
            self.disp=QtGui.QPixmap("/home/pi/Desktop/crop_img.png")    
            self.i2.setPixmap(self.disp)
    def registerfunc(self):
        global cap,bindname
        for i in range(10):
            face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/haarcascade_frontalface_default.xml')
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                #cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                crop_img = gray[y:y+h, x:x+w]
                crop_img = cv2.resize(crop_img,(120,120),interpolation=cv2.INTER_AREA)
                cv2.imwrite('/home/pi/Desktop/crop_img.png',crop_img)
                folder="/home/pi/Desktop/users/"+str(bindname) 
                if os.path.isfile('/home/pi/Desktop/userdata.csv'):
                    pass
                else:
                    
                    df = pd.DataFrame(columns=['ID', 'Name'])
                    df.to_csv('/home/pi/Desktop/userdata.csv', index=False)    

                if not os.path.exists(folder):
                    os.makedirs(folder)
                    directory_path="/home/pi/Desktop/users/"
                    files_and_folders = os.listdir(directory_path)
                    user_id = len([f for f in files_and_folders if os.path.isdir(os.path.join(directory_path, f))])-1
                    data_entry = {'ID': user_id, 'Name': bindname}
                    df = pd.read_csv('/home/pi/Desktop/userdata.csv')
                    df = df.append(data_entry, ignore_index=True)
                    df.to_csv('/home/pi/Desktop/userdata.csv', index=False) 
                else:
                    files = os.listdir(str("/home/pi/Desktop/users/"
                                            +bindname))
                    readfile = files[0]
                    user_id = readfile.split("_")[0]
                    
                path, dirs, files = next(os.walk(folder))
                file_count = len(files)


                cv2.imwrite(str("/home/pi/Desktop/users/"+bindname)+"/"
                            +str(user_id)+"_"+str(bindname)+"_"
                            +str(file_count)+".png",crop_img)
                
            self.disp=QtGui.QPixmap("/home/pi/Desktop/crop_img.png")    
            self.i2.setPixmap(self.disp)
    def trainfunc(self):
        global cap,face_recognizer
        def prepare_training_data(data_folder_path):
            dirs = os.listdir(data_folder_path)
            faces = []
            labels = []
            for dir_name in dirs:
                
                subject_dir_path = data_folder_path + "/" + dir_name
                subject_images_names = os.listdir(subject_dir_path)

                for image_name in subject_images_names:
                    print(image_name)
                    label = int(image_name.split("_")[0])        
                    image_path = subject_dir_path + "/" + image_name
                    image = cv2.imread(image_path,0)

                    
                    faces.append(image)
                    labels.append(label)
                    #print(faces)
                    #print(labels)
            return faces, labels
        faces, labels = prepare_training_data("/home/pi/Desktop/users")
        print("Total faces: ", len(faces))
        print("Total labels: ", len(labels))
        #face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer = cv2.face.FisherFaceRecognizer_create()
        face_recognizer.train(faces, np.array(labels))
        face_recognizer.write('/home/pi/Desktop/model_trained.yml')
    def Loop(self):
        global liveflag,cap,client,lockcheck,cap2,x,y,w,h
        user = client.dropbox.userinfo.find_one({"User": self.userdata})
        #print(user['request_status'])
        if user['request_status']=='rejected' and lockcheck==0:
            idvar="A1,"
            print(idvar)
            ser.write(idvar.encode())
            lockcheck=1
                
        elif user['request_status']=='accepted' and lockcheck==1:
            idvar="A2,"
            print(idvar)
            ser.write(idvar.encode())
            lockcheck=0    
        if liveflag==1:
            camflag=2
            try:
                if camflag==1:
                    ret, frame = cap.read()
                    face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/haarcascade_frontalface_default.xml')
                    ret, frame = cap.read()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x,y,w,h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                    image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                        frame.strides[0], QtGui.QImage.Format_RGB888)
                    image=image.scaledToHeight(360)
                    self.i1.setPixmap(QtGui.QPixmap.fromImage(image))
                elif camflag==2:
                    ret, frame = cap2.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    x=150
                    y=120
                    w=260
                    h=360
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                        frame.strides[0], QtGui.QImage.Format_RGB888)
                    image=image.scaledToHeight(360)
                    self.i1.setPixmap(QtGui.QPixmap.fromImage(image))
            except Exception as e:
                print(e)
        QtCore.QCoreApplication.processEvents()  
    def exit(self):

        QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show the login screen
    login_screen = LoginScreen()
    login_screen.show()

    sys.exit(app.exec_())
