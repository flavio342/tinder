import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from tkinter import *
from tkinter.tix import *
import requests
import json
import webbrowser
from PIL import Image, ImageTk
import urllib.request
import numpy as np
import random
import math
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from sklearn import linear_model

class App(Tk):

    red = "#F44336"
    red_active="#D32F2F"
    blue = "#2196F3"
    black ="#424242"
    pink = "#FFEBEE"
    green = "#4CAF50"
    green_active = "#2E7D32"

    directory = "images"

    saver = None

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.attributes("-fullscreen", True)

        swin = ScrolledWindow(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        swin.pack()
        self.container = swin.window
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frame = None

        self.get_credentials()

    def show_frame(self, page):
        
        old_frame = self.frame

        self.frame = page(parent=self.container, controller=self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.frame.load_page()
        self.frame.tkraise()

        if old_frame:
            old_frame.destroy()
    
    def set_toolbar(self,isLogged):
        if(isLogged):
            menu = Menu(self,bg=self.red,fg="white")
            self.config(menu=menu)
            subMenu = Menu(menu,activebackground=self.red,activeforeground="white",bg=self.pink)
            menu.add_cascade(label="Menu", menu=subMenu,activebackground=self.red_active,activeforeground="white")
            subMenu.add_command(label="Home",command= lambda: self.show_frame(HomePage))
            subMenu.add_command(label="Dataset",command=lambda: self.show_frame(DatasetPage))
            subMenu.add_command(label="Rate Data",command=lambda: self.show_frame(TreinarPage))
            subMenu.add_command(label="Train Neural Network",command=lambda: self.show_frame(TreinarRedePage))
            subMenu.add_command(label="SVD Plots",command= lambda: self.show_frame(SvdPage))
            subMenu.add_command(label="Tinder Auto Rating",command= lambda: self.show_frame(AutoRatePage))
            subMenu.add_separator()
            subMenu.add_command(label="Log Out",command=self.log_out)
            subMenu.add_command(label="Exit",command=self.quit)
        else:
            menu = Menu(self,bg=self.red,fg="white")
            self.config(menu=menu)
            subMenu = Menu(menu,activebackground=self.red,activeforeground="white",bg=self.pink)
            menu.add_command(label="Exit",command=self.quit,activebackground=self.red_active,activeforeground="white")

    def get_credentials(self):
        
        F = open("user/user.txt","r")
        F_text = F.read()
        F.close()

        if(F_text == "" or len(F_text.split('.')) != 2):
            self.show_frame(LoginPage)
            return

        self.facebook_id = StringVar()
        self.facebook_id.set(F_text.split('.')[0])
        
        self.facebook_tinder_token = StringVar()
        self.facebook_tinder_token.set(F_text.split('.')[1])
        
        r = self.login_into_tinder()

        if(r['success']):
            self.show_frame(HomePage)
        else:
            self.show_frame(LoginPage)

    def login_into_tinder(self):
        loginCredentials = {'facebook_token': self.facebook_tinder_token.get(), 'facebook_id': "lol"}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Tinder Android Version 3.2.0'}
        r = requests.post('https://api.gotinder.com/auth', data=json.dumps(loginCredentials), headers=headers)
        
        if 'token' in r.json():
            F = open("user/user.txt","w") 
            F.write(self.facebook_id.get() + ".")
            F.write(self.facebook_tinder_token.get())
            F.close()
            self.tinder_token = r.json()['token']
            self.user = r.json()['user']
            return {'success':True}
        else:
            self.facebook_id.set("")
            self.facebook_tinder_token.set("")
            if r.json()['code'] == 401:
                return {'success':False,'error':"Facebook's Tinder token incorrect or expired"}
            elif r.json()['code'] == 400:
                return {'success':False,'error':"Missing credentials"}
            else:
                return {'success':False,'error':"Unexpected error"}

    def get_data(self):

        count = len(open("user/bd.txt","r").readlines())
        
        F = open("user/bd.txt","r")
        self.bd = []
        lines_read = []
        for i in range(0,count):
            F_text = F.readline()
            has_read_line = False
            for line in lines_read:
                if line == F_text:
                    has_read_line = True
            if has_read_line:
                continue
            for filename in os.listdir(self.directory):
                if F_text.split(".")[0] + ".jpg" == filename:
                    data = {
                        "file_name": F_text.split(".")[0] + ".jpg",
                        "rate": F_text.split(".")[1]
                    }
                    self.bd.append(data)
            lines_read.append(F_text)
        F.close()

        for filename in os.listdir(self.directory):
            hasFile = False
            for data in self.bd:
                if data['file_name'] == filename:
                    hasFile = True
            if not hasFile:
                data = {
                    "file_name": filename,
                    "rate": "null\n"
                }
                self.bd.append(data)
        
        F = open("user/bd.txt","w")
    
        for data in self.bd:
            F.write(data['file_name'].split(".")[0] + "." + data['rate'])
        F.close()
    
    def log_out(self):
        F = open("user/user.txt","w") 
        F.write("")
        F.close()
        self.show_frame(LoginPage)

    def conv2d(self,x,W):
        return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')

    def maxpool2d(self,x):
        return tf.nn.max_pool(x,ksize=[1,2,2,1], strides=[1,2,2,1],padding='SAME')

    def convolutional_neural_network_model(self,x):

        W_fc_input_size = int(self.input_width/4)

        weights = {'W_conv1' : tf.Variable(tf.random_normal([5,5,1,16])), 
                'W_conv2' : tf.Variable(tf.random_normal([5,5,16,36])),
                'W_fc' : tf.Variable(tf.random_normal([W_fc_input_size*W_fc_input_size*36,128])),
                'out' : tf.Variable(tf.random_normal([128,self.n_classes]))}

        biases = {'b_conv1' : tf.Variable(tf.random_normal([16])), 
                'b_conv2' : tf.Variable(tf.random_normal([36])),
                'b_fc' : tf.Variable(tf.random_normal([128])),
                'out' : tf.Variable(tf.random_normal([self.n_classes]))}

        x = tf.reshape(x,shape=[-1,self.input_width,self.input_width,1])

        conv1 = self.conv2d(x, weights['W_conv1']) + biases['b_conv1'] 
        conv1 = self.maxpool2d(conv1) 
        
        conv2 = self.conv2d(conv1, weights['W_conv2']) + biases['b_conv2'] 
        conv2 = self.maxpool2d(conv2)

        fc = tf.reshape(conv2,[-1,W_fc_input_size*W_fc_input_size*36])
        fc = tf.nn.relu( tf.matmul( fc, weights['W_fc'] ) + biases['b_fc'] )

        output = tf.matmul( fc, weights['out'] ) + biases['out']
        

        return output

class LoginPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
    
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(False)
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - Log In")
        self.config(bg=self.controller.pink)

    def set_page(self):

        self.controller.facebook_id = StringVar()
        self.controller.facebook_id.set("")

        self.controller.facebook_tinder_token = StringVar()
        self.controller.facebook_tinder_token.set("")

        self.error = StringVar()
        self.error.set("")

        title = Label(self,text="S2 MatchMe! S2",bg=self.controller.pink,fg=self.controller.red,font=30)
        #facebook_id_label = Label(self,text="Facebook ID",bg=self.controller.pink,fg=self.controller.black)
        #facebook_id_entry = Entry(self,textvariable=self.controller.facebook_id)
        facebook_tinder_token_label = Label(self,text="Facebook's Tinder Token",bg=self.controller.pink,fg=self.controller.black)
        facebook_tinder_token_entry = Entry(self,textvariable=self.controller.facebook_tinder_token)
        help_link = Label(self, text="How can I get my token?", cursor="hand2",bg=self.controller.pink,fg=self.controller.blue)
        help_link.bind("<Button-1>", self.help_get_credentials)
        error_label = Label(self,textvariable=self.error,bg=self.controller.pink,fg=self.controller.red)

        sendButton = Button(self,text="Login",command=self.log_in,bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")

        pady = 7

        title.pack(pady=40)
        #facebook_id_label.pack(pady=pady)
        #facebook_id_entry.pack(pady=pady)
        facebook_tinder_token_label.pack(pady=pady)
        facebook_tinder_token_entry.pack(pady=pady)
        error_label.pack(pady=pady)
        help_link.pack(pady=pady)
        sendButton.pack(pady=13)

    def log_in(self):
        r = self.controller.login_into_tinder()
        if(r['success']):
            self.controller.show_frame(HomePage)
        else:
            self.error.set(r['error'])

    def help_get_credentials(self,event):
        webbrowser.open_new("https://gist.github.com/taseppa/66fc7239c66ef285ecb28b400b556938")

class HomePage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
    
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.controller.get_data()
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - Home")
        self.config(bg=self.controller.pink)

    def set_page(self):

        url = self.controller.user['photos'][0]['processedFiles'][1]['url']
        
        urllib.request.urlretrieve(url, 'user/user.jpg')
        
        image = Image.open("user/user.jpg")
        image = image.resize((250, 250), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(image)
        user_img = Label(self,image=photo)
        user_img.image = photo
    
        name = self.controller.user['full_name']
        name_label = Label(self,text=name,font=5,bg=self.controller.pink)

        bio = self.controller.user['bio']
        bio_label = Label(self,text=bio,font=4,bg=self.controller.pink)

        pady=10

        user_img.pack(pady=30)
        name_label.pack(pady=pady)
        bio_label.pack(pady=pady)

class DatasetPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.controller.get_data()
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - Dataset")
        self.config(bg=self.controller.pink)
        

    def set_page(self):

        screen_w = int(self.winfo_screenwidth())
        img_w = int(100)
        n_collumns = int(int(screen_w) / img_w)

        title_frame = Frame(self,bg=self.controller.pink)
        title_frame.pack(pady=20)

        title_label = Label(title_frame,text="Number of photos in dataset",bg=self.controller.pink,fg=self.controller.black,font=10)
        self.nImages = StringVar()
        self.nImages.set(str(len(os.listdir(self.controller.directory))))
        self.error = StringVar()
        self.error.set("")

        self.log = StringVar()
        self.log.set("")

        self.n_subjects = StringVar()
        self.n_subjects.set("10")

        self.isSearching = False

        number_label = Label(title_frame,textvariable=self.nImages,bg=self.controller.pink,fg=self.controller.red,font=30)
        error_label = Label(title_frame,textvariable=self.error,bg=self.controller.pink,fg=self.controller.red,font=10)
        log_label = Label(title_frame,textvariable=self.log,bg=self.controller.pink,fg=self.controller.black,font=10)
        
        

        entry_frame = Frame(self,bg=self.controller.pink)
        entry_frame.pack(pady=20)
        
        n_subjects_label = Label(entry_frame,text="Number of subjects to retrieve",bg=self.controller.pink,fg=self.controller.black,font=10)
        n_subjects_entry = Entry(entry_frame,textvariable=self.n_subjects)
        
        
        sendButton = Button(entry_frame,text="Get More",command=self.get_more_images,bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")

        title_frame.pack()
        title_label.pack(pady=10)
        number_label.pack(pady=10)
        error_label.pack(pady=10)
        log_label.pack(pady=10)

        entry_frame.pack(pady=10)
        n_subjects_label.grid(row=0,column=0)
        n_subjects_entry.grid(row=0,column=1)

        sendButton.grid(row=1,columnspan=2)



        """images_frame = Frame(self,bg=self.controller.pink)
        images_frame.pack(pady=10)

        base_row=4
        for i, filename in enumerate(os.listdir(self.controller.directory)):
            
            image = Image.open(self.controller.directory + "/" + filename)
            image = image.resize((img_w, img_w), Image.ANTIALIAS)

            photo = ImageTk.PhotoImage(image)
            user_img = Label(images_frame,image=photo)
            user_img.image = photo

            row = base_row + int(i/n_collumns)
            collumn = int(i%n_collumns)
            user_img.grid(row=row,column=collumn)"""

    def get_more_images(self):
        
        if not self.isSearching:
            n_subjects = 0
            self.isSearching = True
            while n_subjects < int(self.n_subjects.get()):

                headers2 = {'User-Agent': 'Tinder Android Version 3.2.0', 'Content-Type': 'application/json', 'X-Auth-Token': self.controller.tinder_token}
                r2 = requests.get('https://api.gotinder.com/user/recs', headers=headers2)
                
                if 'results' in r2.json():
                    subjects = r2.json()['results']

                    for i, subject in enumerate(subjects):
                        n_subjects+=1
                        if n_subjects > int(self.n_subjects.get()):
                            break
                        self.log.set("Retrieving subject " + str(n_subjects))
                        self.controller.update()
                        sid = subject['_id']
                        pictures = subject['photos']
                        processed_picURL = str(pictures[0]['processedFiles'][3]['url'])
                        urllib.request.urlretrieve(processed_picURL, self.controller.directory + '/' + sid + '.jpg')

                        F = open("user/bd.txt","a") 
                        F.write(sid + ".null\n")
                        F.close()

                        self.tinderAPI_passSubject(subject)
                else:
                    self.error.set("Limit exceeded! Try again later...")
                    self.log.set("")
                    self.isSearching = False
            self.isSearching = False
            self.controller.show_frame(DatasetPage)
        


    def tinderAPI_passSubject(self,subject):
        _id = subject['_id']
        headers3 = {'X-Auth-Token': self.controller.tinder_token, 'User-Agent': 'Tinder Android Version 3.2.0'}
        r3 = requests.get('https://api.gotinder.com/pass/' + _id, headers=headers3) 


class TreinarPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
                
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.controller.get_data()
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - Rate Data")
        self.config(bg=self.controller.pink)
    

    def set_page(self):

        title_frame = Frame(self,bg=self.controller.pink)
        title_frame.pack(pady=20)

        rated_label = Label(title_frame,text="Data Rated:",bg=self.controller.pink,fg=self.controller.black,font=10)
        not_rated_label = Label(title_frame,text="Data Not Rated:",bg=self.controller.pink,fg=self.controller.black,font=10)
        not_saved_label = Label(title_frame,text="Rating Not Saved:",bg=self.controller.pink,fg=self.controller.red,font=10)
       
        not_rated = 0
        rated = 0
        self.not_rated_data = []
        for data in self.controller.bd:
            if data['rate'] == "null\n":
                not_rated += 1
                self.not_rated_data.append(data)
            else:
                rated += 1
        
        self.rated = StringVar()
        self.rated.set(str(rated))
        self.not_rated = StringVar()
        self.not_rated.set(not_rated)

        self.not_saved = StringVar()
        self.not_saved.set("0")

        rated_label_num = Label(title_frame,textvariable=self.rated,bg=self.controller.pink,fg=self.controller.red,font=20)
        not_rated_label_num = Label(title_frame,textvariable=self.not_rated,bg=self.controller.pink,fg=self.controller.red,font=20)
        not_saved_num = Label(title_frame,textvariable=self.not_saved,bg=self.controller.pink,fg=self.controller.red,font=20)
        save_button = Button(title_frame,text="Save Ratings",command=self.save_rated_data,bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")
            

        rated_label.grid(row=0,column=0)
        not_rated_label.grid(row=1,column=0)
        rated_label_num.grid(row=0,column=1)
        not_rated_label_num.grid(row=1,column=1)
        not_saved_label.grid(row=2,column=0)
        not_saved_num.grid(row=2,column=1)
        save_button.grid(row=3,columnspan=2)

        self.error = StringVar()
        self.error.set("")
        error_label = Label(self,textvariable=self.error,bg=self.controller.pink,fg=self.controller.red,font=20)
        error_label.pack(pady=10)

        self.current_data = self.get_next_not_rated_data()

        if self.current_data:
            image = Image.open(self.controller.directory + "/" + self.current_data['file_name'])
            image = image.resize((200, 200), Image.ANTIALIAS)

            photo = ImageTk.PhotoImage(image)
        
            self.user_img = Label(self,image=photo)
            self.user_img.image = photo

            self.user_img.pack(pady=20)

            buttons_frame = Frame(self,bg=self.controller.pink)
            buttons_frame.pack(pady=20)

            dislike_button = Button(buttons_frame,text="Dislike",command=lambda: self.rate_data(self.current_data['file_name'],"dislike\n"),bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")
            like_button = Button(buttons_frame,text="Like",command=lambda: self.rate_data(self.current_data['file_name'],"like\n"),bg=self.controller.green,fg="white",activebackground=self.controller.green_active,activeforeground="white")
            dislike_button.grid(row=0,column=0,padx=10)
            like_button.grid(row=0,column=1,padx=10)

    def get_next_not_rated_data(self):
        if(len(self.not_rated_data)>0):
            data = self.not_rated_data.pop(0)
            return data
        else:
            self.error.set("No more data to rate...")
            return None

    def save_rated_data(self):
        F = open("user/bd.txt","w")
        for data in self.controller.bd:
            F.write(data['file_name'].split(".")[0] + "." + data['rate'])
        F.close()
        self.controller.show_frame(TreinarPage)

    def rate_data(self,file_name,rate):
        for data in self.controller.bd:
            if data['file_name'] == file_name:
                data['rate'] = rate

        not_saved = int(self.not_saved.get()) + 1
        self.not_saved.set(not_saved)

        not_rated = int(self.not_rated.get()) -1
        self.not_rated.set(not_rated)

        rated = int(self.rated.get()) + 1
        self.rated.set(rated)

        self.current_data = self.get_next_not_rated_data()

        image = Image.open(self.controller.directory + "/" + self.current_data['file_name'])
        image = image.resize((200, 200), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(image)
        self.user_img.configure(image=photo)
        self.user_img.image = photo
        self.controller.update()
        
class TreinarRedePage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
                
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.controller.get_data()
        self.set_page()
        self.get_curren_nn_data()

    def set_screen(self):
        self.controller.title("MatchMe! - Train Neural Network")
        self.config(bg=self.controller.pink)
    

    def set_page(self):
        
        title_frame = Frame(self,bg=self.controller.pink)
        title_frame.pack(pady=20)

        self.accuracy = StringVar()
        self.accuracy.set("")

        self.train = StringVar()
        self.train.set("")

        self.test = StringVar()
        self.test.set("")

        self.error = StringVar()
        self.error.set("")

        self.new_data = StringVar()
        self.new_data.set("")

        self.log = StringVar()
        self.log.set("")

        error_label = Label(title_frame,textvariable=self.error,bg=self.controller.pink,fg=self.controller.red,font=20)
        
        accuracy_label = Label(title_frame,text="Accuracy",bg=self.controller.pink,fg=self.controller.black,font=10)
        accuracy_label_value = Label(title_frame,textvariable=self.accuracy,bg=self.controller.pink,fg=self.controller.red,font=30)
        
        train_label = Label(title_frame,text="Trained",bg=self.controller.pink,fg=self.controller.black,font=10)
        train_label_value = Label(title_frame,textvariable=self.train,bg=self.controller.pink,fg=self.controller.red,font=10)

        test_label = Label(title_frame,text="Tested",bg=self.controller.pink,fg=self.controller.black,font=10)
        test_label_value = Label(title_frame,textvariable=self.test,bg=self.controller.pink,fg=self.controller.red,font=10)

        new_label = Label(title_frame,text="New Data",bg=self.controller.pink,fg=self.controller.black,font=10)
        new_label_value = Label(title_frame,textvariable=self.new_data,bg=self.controller.pink,fg=self.controller.red,font=10)

        train_button = Button(title_frame,text="Train Neural Network",command=self.train_data,bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")
        
        log_value = Label(title_frame,textvariable=self.log,bg=self.controller.pink,fg=self.controller.black,font=10)

        error_label.grid(row=0,columnspan=2)
        accuracy_label.grid(row=1,columnspan=2)
        accuracy_label_value.grid(row=2,columnspan=2)
        train_label.grid(row=3,column=0)
        train_label_value.grid(row=4,column=0)
        test_label.grid(row=3,column=1)
        test_label_value.grid(row=4,column=1)
        new_label.grid(row=5,columnspan=2)
        new_label_value.grid(row=6,columnspan=2)
        train_button.grid(row=7,columnspan=2,pady=10)
        log_value.grid(row=8,columnspan=2,pady=10)
        

    def get_curren_nn_data(self):
        try:
            F = open("user/nn.txt","r")
            F_text = F.readline()
            self.accuracy.set(F_text.split("\n")[0])
            F_text = F.readline()
            self.train.set(F_text.split(".")[0])
            self.test.set(F_text.split(".")[1])
            trained = int(self.train.get()) + int(self.test.get())

            count = len(open("user/bd.txt","r").readlines())
            F = open("user/bd.txt","r")
            all_set = 0
            for i in range(0,count):
                F_text = F.readline()
                if F_text.split(".")[1] != 'null\n':
                    all_set+=1
            F.close()

            self.new_data.set(str(all_set - trained))
            
        except:
            self.accuracy.set("0")
            self.train.set("0")
            self.test.set("0")

            count = len(open("user/bd.txt","r").readlines())
            F = open("user/bd.txt","r")
            all_set = 0
            for i in range(0,count):
                F_text = F.readline()
                if F_text.split(".")[1] != 'null\n':
                    all_set+=1
            F.close()
            self.new_data.set(str(all_set))
            self.error_label.set("Neural Network Not Trained")

    def train_data(self):

        if self.new_data.get() !='' and int(self.new_data.get()) > 0:
            self.error.set("")

            train_x,train_y,test_x,test_y = self.create_data_set_and_labels()

            self.controller.n_classes = 2
            batch_size = 100

            self.controller.input_size = len(train_x[0])
            self.controller.input_width = int(math.sqrt(self.controller.input_size))

            x = tf.placeholder('float', [None, self.controller.input_size])
            y = tf.placeholder('float')
            curren_epoch = tf.Variable(0)

            self.controller.saver = tf.train.Saver()

            prediction = self.controller.convolutional_neural_network_model(x)
            cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(logits=prediction,labels=y))

            optimizer = tf.train.AdamOptimizer().minimize(cost)

            hm_epochs = 7

            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())

                for epoch in range (hm_epochs):

                    epoch_loss = 0

                    i = 0
                    while i < len(train_x):
                        start = i
                        end = i + batch_size

                        batch_x = np.array(train_x[start:end])
                        batch_y = np.array(train_y[start:end])


                        _,c = sess.run([optimizer,cost], feed_dict = {x:batch_x,y:batch_y})
                        epoch_loss += c
                        i+=batch_size

                    log = self.log.get()
                    new_log = log + "Epoch " + str(epoch) + " completed out of " + str(hm_epochs) + ". Loss: " + str(epoch_loss) + "\n"
                    self.log.set(new_log)
                    self.controller.update()
                
                correct = tf.equal(tf.argmax(prediction,1),tf.argmax(y,1))

                accuracy = tf.reduce_mean(tf.cast(correct,'float'))

                self.controller.saver.save(sess,'tf_model/model.ckpt')

                accuracy_eval = accuracy.eval({x:test_x,y:test_y})

                F = open("user/nn.txt","w")
                F.write(str(accuracy_eval) + "\n")
                F.write(str(len(train_x)) + "." + str(len(test_x)))
                F.close()

                self.controller.show_frame(TreinarRedePage)
        else:
            self.error.set("There is no new data to train")

    def create_data_set_and_labels(self):

        first_img = Image.open(os.path.join(self.controller.directory, os.listdir(self.controller.directory)[0]))
        
        #GRAY
        first_img = first_img.convert('LA')
        first_imgmat = np.array(list(first_img.getdata(band=0)), int)
        
        #COLORED
        #first_imgmat = np.array(first_img, int)
        
        first_imgmat = np.reshape(first_imgmat,(1, -1))

        dimension = first_imgmat.shape[1]

        test_size=0.1 
        count = len(open("user/bd.txt","r").readlines())
        F = open("user/bd.txt","r")
        data_set_and_labels = []
        lines_read = []
        for i in range(0,count):
            F_text = F.readline()
            if F_text.split(".")[1] == 'null\n':
                continue
            has_read_line = False
            for line in lines_read:
                if line == F_text:
                    has_read_line = True
                    break
            if has_read_line:
                continue
            for filename in os.listdir(self.controller.directory):
                if F_text.split(".")[0] + ".jpg" == filename:
                    rate = [0,1]
                    if F_text.split(".")[1] == 'like\n':
                        rate = [1,0]
                    img = Image.open(os.path.join(self.controller.directory, filename))
                    img = img.convert('LA')
                    imgmat = list(img.getdata(band=0))
                    if(len(imgmat) == dimension):
                        data = [imgmat,rate]
                        data_set_and_labels.append(data)
                    break
            lines_read.append(F_text)
        F.close()

        l = 0
        d = 0
        for data in data_set_and_labels:
            if data[1][0] == 1:
                l+=1
            else:
                d+=1
        
        n = min(l,d)
        l = 0
        d = 0

        print('dataset',len(data_set_and_labels))

        print("n",n*2)

        dataset = []
        for data in data_set_and_labels:
            if data[1][0] == 1 and l<n:
                dataset.append(data)
                l+=1
            elif  data[1][0] == 0 and d<n:
                dataset.append(data)
                d+=1


        random.shuffle(dataset)
        dataset = np.array(dataset)
        
        testing_size = int(test_size*len(dataset))

        train_x = list(dataset[:,0][:-testing_size])
        train_y = list(dataset[:,1][:-testing_size])

        test_x = list(dataset[:,0][-testing_size:])
        test_y = list(dataset[:,1][-testing_size:])

        return train_x,train_y,test_x,test_y

class SvdPage(Frame):

    nOfImages = 10000

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
                
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.controller.get_data()
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - SVD")
        self.config(bg=self.controller.pink)

    def set_page(self):

        pady=10

        data = self.get_plot_data()

        title_label = Label(self, text="Dataset - Logistic Regression", font=10,bg=self.controller.pink)
        title_label.pack(pady=pady)

        logistic_data = {
            'x': [],
            'y': []
        }
        for i in range(0,len(data[0])):
            if(data[2][i] == 'like\n'):
                logistic_data['x'].append(data[0][i])
                logistic_data['y'].append(1)
            else:
                logistic_data['x'].append(data[0][i])
                logistic_data['y'].append(0)
        
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot(logistic_data['x'],logistic_data['y'],'bo')

        clf = linear_model.LogisticRegression(C=1e5)
        logistic_data['x'] = np.array(logistic_data['x'])
        logistic_data['y'] = np.array(logistic_data['y'])
        logistic_data['x'] = np.reshape(logistic_data['x'],(-1, 1))

        same = True
        r_type = logistic_data['y'][0]
        for j in range(0,len(logistic_data['y'])):
            if r_type != logistic_data['y'][j]:
                same = False
        
        if not same:
            clf.fit(logistic_data['x'], logistic_data['y'])

            X_test = np.linspace(-0.3, 0.3, 300)

            def model(x):
                return 1 / (1 + np.exp(-x))
            loss = model(X_test * clf.coef_ + clf.intercept_).ravel()

            a.plot(X_test, loss,color='red', linewidth=3)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)


        title_label = Label(self, text="Dataset SVD 2D", font=10,bg=self.controller.pink)
        title_label.pack(pady=pady)
        
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)

        liked = {
            'x': [],
            'y': []
        }
        disliked = {
            'x': [],
            'y': []
        }
        not_rated = {
            'x': [],
            'y': []
        }

        for i in range(0,len(data[0])):
            if(data[2][i] == 'null\n'):
                not_rated['x'].append(data[0][i])
                not_rated['y'].append(data[1][i])
            elif(data[2][i] == 'like\n'):
                liked['x'].append(data[0][i])
                liked['y'].append(data[1][i])
            else:    
                disliked['x'].append(data[0][i])
                disliked['y'].append(data[1][i])


        a.plot(disliked['x'],disliked['y'],'ro')
        a.plot(liked['x'],liked['y'],'go')
        a.plot(not_rated['x'],not_rated['y'],'bo')

        regression_data = []
        regression_data_label = []
        for j in range(0,len(data[0])):
            regression_data.append([data[0][j],data[1][j]])
            if data[2][j] == 'like\n':
                regression_data_label.append(1)
            else:
                regression_data_label.append(0)
        
        regression_data = np.matrix(regression_data)
        regression_data_label = np.array(regression_data_label)

        same = True
        r_type = regression_data_label[0]
        for j in range(0,len(regression_data_label)):
            if r_type != regression_data_label[j]:
                same = False

        if not same:
            h = .001  # step size in the mesh

            logreg = linear_model.LogisticRegression(C=1e5)

            # we create an instance of Neighbours Classifier and fit the data.
            logreg.fit(regression_data, regression_data_label)

            x_min, x_max = regression_data[:, 0].min() - .1, regression_data[:, 0].max() + .1
            y_min, y_max = regression_data[:, 1].min() - .1, regression_data[:, 1].max() + .1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
            Z = logreg.predict(np.c_[xx.ravel(), yy.ravel()])

            Z = Z.reshape(xx.shape)
            a.pcolormesh(xx, yy, Z, cmap=plt.cm.Pastel1)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        title_label = Label(self, text="Dataset SVD 2D - pics", font=10,bg=self.controller.pink)
        title_label.pack(pady=pady)
        
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)


        first_img = Image.open(os.path.join(self.controller.directory, os.listdir(self.controller.directory)[0]))
        
        #GRAY
        first_img = first_img.convert('LA')
        first_imgmat = np.array(list(first_img.getdata(band=0)), int)
        
        #COLORED
        #first_imgmat = np.array(first_img, int)
        
        first_imgmat = np.reshape(first_imgmat,(1, -1))

        dimension = first_imgmat.shape[1]
        
        k=0
        for filename in os.listdir(self.controller.directory):
            img = Image.open(os.path.join(self.controller.directory, filename))

            #GRAY
            img = img.convert('LA')
            imgmat = np.array(list(img.getdata(band=0)), int)

            #COLORED
            #imgmat = np.array(img, int)

            imgmat = np.reshape(imgmat,(1, -1))
            if(imgmat.shape[0] == 1 and imgmat.shape[1] == dimension): 
                self.imscatter(data[0][k],data[1][k],os.path.join(self.controller.directory, filename),ax=a,zoom=0.4)
                k+=1
            if k>=self.nOfImages:
                break

        #a.plot(data[0],data[1],'ro')

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def imscatter(self,x, y, image, ax=None, zoom=1):
        
        if ax is None:
            ax = plt.gca()
        try:
            image = plt.imread(image)
        except TypeError:
            # Likely already an array...
            pass
      
        im = OffsetImage(image, zoom=zoom)
        x, y = np.atleast_1d(x, y)
        artists = []
        for x0, y0 in zip(x, y):
            ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
            artists.append(ax.add_artist(ab))
        ax.update_datalim(np.column_stack([x, y]))
        ax.autoscale()
        return artists

    def get_plot_data(self):

        A = None

        first_img = Image.open(os.path.join(self.controller.directory, os.listdir(self.controller.directory)[0]))
        
        #GRAY
        first_img = first_img.convert('LA')
        first_imgmat = np.array(list(first_img.getdata(band=0)), int)
        
        #COLORED
        #first_imgmat = np.array(first_img, int)
    
        first_imgmat = np.reshape(first_imgmat,(1, -1))

        dimension = first_imgmat.shape[1]

        count = len(open("user/bd.txt","r").readlines())
        F = open("user/bd.txt","r")
        data = []
        for i in range(0,count):
            F_text = F.readline()
            d = {   
                'file_name': F_text.split(".")[0] + ".jpg",
                'rate': F_text.split(".")[1]
            }
            data.append(d)
        F.close()

        rate = []
        for i,filename in enumerate(os.listdir(self.controller.directory)):

            img = Image.open(os.path.join(self.controller.directory, filename))

            #GRAY
            img = img.convert('L')
            imgmat = np.array(list(img.getdata(band=0)), int)
     
            #COLORED
            #imgmat = np.array(img, int)
            """r = []
            g = []
            b = []
            for i in range (len(imgmat[0])):
                for j in range (len(imgmat[0])):
                    r.append(imgmat[i][j][0])
                    g.append(imgmat[i][j][1])
                    b.append(imgmat[i][j][2])

            imgmat = np.append(r,g)
            imgmat = np.append(imgmat,b)"""
            #END COLORED

            imgmat = np.reshape(imgmat,(1, -1))

            if type(A) is not np.ndarray:
                A = np.empty((0,imgmat.shape[1]), int)

            if(imgmat.shape[0] == 1 and imgmat.shape[1] == dimension):
                for j in range(0,len(data)):
                    if data[j]['file_name'] == filename:
                        rate.append(data[j]['rate']) 
                A = np.append(A, imgmat, axis=0)

            if(i>=self.nOfImages):
                break

        U, sigma, V = np.linalg.svd(A,0)

        return [U[:,1],U[:,2],rate]


class AutoRatePage(Frame):

    likes_num = 0
    dislikes_num = 0
    matches_num = 0
    isSearching = False

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
                
    def load_page(self):
        self.set_screen()
        self.controller.set_toolbar(True)
        self.simulate_auto()
        self.set_page()

    def set_screen(self):
        self.controller.title("MatchMe! - Auto Tinder Rating")
        self.config(bg=self.controller.pink)

    def set_page(self):

        error_label = Label(self,textvariable=self.error,bg=self.controller.pink,fg=self.controller.red,font=20)
        error_label.pack(pady=10)

        test_button = Button(self,text="Simulate Auto Rating",command=lambda: self.controller.show_frame(AutoRatePage),bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")
        test_button.pack(pady=20)

        simulation_frame = Frame(self,bg=self.controller.pink)
        simulation_frame.pack(pady=20) 

        for i,photo in enumerate(self.simulation_photos):

            image = Image.open(photo)
            image = image.resize((200, 200), Image.ANTIALIAS)

            photo = ImageTk.PhotoImage(image)
            user_img = Label(simulation_frame,image=photo)
            user_img.image = photo

            user_img.grid(row=0,column=i)
 
        simulation_value_label = Label(self,text="Rating",bg=self.controller.pink,fg=self.controller.black,font=10)
        simulation_value_num = Label(self,textvariable=self.simulation_value,bg=self.controller.pink,fg=self.controller.red,font=30)
        
        simulation_value_label.pack()
        simulation_value_num.pack()

        self.error_2 = StringVar()
        self.error_2.set("")

        error_label_2 = Label(self,textvariable=self.error_2,bg=self.controller.pink,fg=self.controller.red,font=20)
        error_label_2.pack(pady=10)

        self.n_subjects = StringVar()
        self.n_subjects.set("10")

        n_subjects_label = Label(self,text="Number of subjects to Rate",bg=self.controller.pink,fg=self.controller.black,font=10)
        n_subjects_entry = Entry(self,textvariable=self.n_subjects)

        n_subjects_label.pack(pady=10)
        n_subjects_entry.pack(pady=10)

        rate_button = Button(self,text="Tinder Auto Rating",command=self.tinder_auto,bg=self.controller.red,fg="white",activebackground=self.controller.red_active,activeforeground="white")
        rate_button.pack(pady=20)

        self.tinder_frame = Frame(self,bg=self.controller.pink)
        self.tinder_frame.pack(pady=20) 

        self.likes = StringVar()
        self.likes.set("0")

        self.dislikes = StringVar()
        self.dislikes.set("0")

        self.matches = StringVar()
        self.matches.set("0")

        likes_label = Label(self.tinder_frame,text="Likes",bg=self.controller.pink,fg=self.controller.black,font=10)
        likes_label_num = Label(self.tinder_frame,textvariable=self.likes,bg=self.controller.pink,fg=self.controller.red,font=30)
       
        matches_label = Label(self.tinder_frame,text="Matchs",bg=self.controller.pink,fg=self.controller.black,font=10)
        matches_label_num = Label(self.tinder_frame,textvariable=self.matches,bg=self.controller.pink,fg=self.controller.red,font=30)

        dislikes_label = Label(self.tinder_frame,text="Dislikes",bg=self.controller.pink,fg=self.controller.black,font=10)
        dislikes_label_num = Label(self.tinder_frame,textvariable=self.dislikes,bg=self.controller.pink,fg=self.controller.red,font=30)

        likes_label.grid(row=0,column=0)
        likes_label_num.grid(row=1,column=0)
        matches_label.grid(row=0,column=1)
        matches_label_num.grid(row=1,column=1)
        dislikes_label.grid(row=0,column=2)
        dislikes_label_num.grid(row=1,column=2)
        

    def tinder_auto(self):

        if not self.isSearching:
            n_subjects = 0
            self.isSearching = True
            while n_subjects < int(self.n_subjects.get()):

                self.controller.n_classes = 2

                headers2 = {'User-Agent': 'Tinder Android Version 3.2.0', 'Content-Type': 'application/json', 'X-Auth-Token': self.controller.tinder_token}
                r2 = requests.get('https://api.gotinder.com/user/recs', headers=headers2)
                
                if 'results' in r2.json():
                    subjects = r2.json()['results']

                    for j, subject in enumerate(subjects):

                        n_subjects+=1
                        if n_subjects > int(self.n_subjects.get()):
                            break

                        sid = subject['_id']
                        pictures = subject['photos']

                        data = []

                        for i,photo in enumerate(pictures):
                        
                            imgUrl = photo['processedFiles'][3]['url']
                            
                            urllib.request.urlretrieve(imgUrl, 'user/tinder_' + str(i) + '.jpg')
                            img = Image.open('user/tinder_' + str(i) + '.jpg')
                            img1 = img.convert('LA')
                            imgmat = list(img1.getdata(band=0))

                            self.controller.input_size = len(imgmat)
                            self.controller.input_width = int(math.sqrt(self.controller.input_size))
                            data.append(imgmat)

                        rate = self.use_neural_network(data)

                        imgUrl = pictures[0]['processedFiles'][0]['url']
                        urllib.request.urlretrieve(imgUrl, 'user/tinder_' + str(j) + '.jpg')

                        image = Image.open('user/tinder_' + str(j) + '.jpg')
                        image = image.resize((200, 200), Image.ANTIALIAS)

                        photo = ImageTk.PhotoImage(image)
                        user_img = Label(self.tinder_frame,image=photo)
                        user_img.image = photo

                        

                        if rate == "Like":
                            user_img.grid(row=2+self.likes_num,column=0)
                            self.likes_num+=1
                            self.likes.set(str(self.likes_num))
                            headers3 = {'X-Auth-Token': self.controller.tinder_token, 'User-Agent': 'Tinder Android Version 3.2.0'}
                            r3 = requests.get('https://api.gotinder.com/like/' + sid, headers=headers3)
                        else:
                            user_img.grid(row=2+self.dislikes_num,column=2)
                            self.dislikes_num+=1
                            self.dislikes.set(str(self.dislikes_num))
                            headers3 = {'X-Auth-Token': self.controller.tinder_token, 'User-Agent': 'Tinder Android Version 3.2.0'}
                            r3 = requests.get('https://api.gotinder.com/pass/' + sid, headers=headers3)

                        if 'match' in r3.json():
                            match = r3.json()['match'] 
                            if match:
                                self.matches_num+=1
                                self.matches.set(str(self.matches_num))

                        self.controller.update()


                else:
                    self.error_2.set("Limit exceeded! Try again later...")
                    self.isSearching = False
            self.isSearching = False


        

    
    def simulate_auto(self):
        
        headers2 = {'User-Agent': 'Tinder Android Version 3.2.0', 'Content-Type': 'application/json', 'X-Auth-Token': self.controller.tinder_token}
        r2 = requests.get('https://api.gotinder.com/user/recs', headers=headers2)
        
        self.error = StringVar()
        self.error.set("")

        self.simulation_value = StringVar()
        self.simulation_value.set("")

        if 'results' in r2.json():
            subjects = r2.json()['results']

            self.simulation_photos = []
            simulated_data = []
            self.controller.n_classes = 2
            for i,photo in enumerate(subjects[0]['photos']):

                imgUrl = photo['processedFiles'][3]['url']
                
                urllib.request.urlretrieve(imgUrl, 'user/simulation_' + str(i) + '.jpg')
                img = Image.open('user/simulation_' + str(i) + '.jpg')
                img1 = img.convert('LA')
                imgmat = list(img1.getdata(band=0))
                self.controller.input_size = len(imgmat)
                self.controller.input_width = int(math.sqrt(self.controller.input_size))
                simulated_data.append(imgmat)

                imgUrl = photo['processedFiles'][0]['url']
                urllib.request.urlretrieve(imgUrl, 'user/simulation_' + str(i) + '.jpg')
                self.simulation_photos.append('user/simulation_' + str(i) + '.jpg')
            
           
            self.simulation_value.set(self.use_neural_network(simulated_data))
                
        else:
            self.error.set("Limit exceeded! Try again later...")


    def use_neural_network(self,input_data):

        x = tf.placeholder('float', [None, self.controller.input_size])
        y = tf.placeholder('float')
        curren_epoch = tf.Variable(0)

        keep_rate = 0.8
        keep_prob = tf.placeholder(tf.float32)

        if self.controller.saver is None:
            print("oi")
            self.controller.saver = tf.train.Saver()

        prediction = self.controller.convolutional_neural_network_model(x)
        like = 0
        dislike = 0

        for data in input_data:

            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())

                self.controller.saver.restore(sess,'tf_model/model.ckpt')              
                result = sess.run( tf.argmax( prediction.eval( feed_dict={ x:[data] } ), 1 ) )

                if result[0] == 0:
                    like+=1
                elif  result[0] == 1:
                    dislike+=1
        
        if like > dislike:
            return "Like"
        else:
            return "Dislike"

app = App()
app.mainloop()
