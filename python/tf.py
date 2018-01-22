import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from PIL import Image, ImageTk
import numpy as np
import random
import matplotlib.pyplot as plt
import math

def create_data_set_and_labels(test_size=0.1): 

    directory = "images"
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
        for filename in os.listdir(directory):
            if F_text.split(".")[0] + ".jpg" == filename:
                rate = [0,1]
                if F_text.split(".")[1] == 'like\n':
                    rate = [1,0]
                img = Image.open(os.path.join(directory, filename))
                img = img.convert('LA')
                imgmat = list(img.getdata(band=0))
                data = [imgmat,rate]
                data_set_and_labels.append(data)
        lines_read.append(F_text)
    F.close()

    random.shuffle(data_set_and_labels)
    data_set_and_labels = np.array(data_set_and_labels)
    
    testing_size = int(test_size*len(data_set_and_labels))

    train_x = list(data_set_and_labels[:,0][:-testing_size])
    train_y = list(data_set_and_labels[:,1][:-testing_size])

    test_x = list(data_set_and_labels[:,0][-testing_size:])
    test_y = list(data_set_and_labels[:,1][-testing_size:])

    return train_x,train_y,test_x,test_y

def conv2d(x,W):
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')

def maxpool2d(x):
    return tf.nn.max_pool(x,ksize=[1,2,2,1], strides=[1,2,2,1],padding='SAME')

def convolutional_neural_network_model(x):

    W_fc_input_size = int(input_width/4)

    weights = {'W_conv1' : tf.Variable(tf.random_normal([5,5,1,32])), 
               'W_conv2' : tf.Variable(tf.random_normal([5,5,32,64])),
               'W_fc' : tf.Variable(tf.random_normal([W_fc_input_size*W_fc_input_size*64,1024])),
               'out' : tf.Variable(tf.random_normal([1024,n_classes]))}

    biases = {'b_conv1' : tf.Variable(tf.random_normal([32])), 
              'b_conv2' : tf.Variable(tf.random_normal([64])),
              'b_fc' : tf.Variable(tf.random_normal([1024])),
              'out' : tf.Variable(tf.random_normal([n_classes]))}

    x = tf.reshape(x,shape=[-1,input_width,input_width,1])

    conv1 = conv2d(x, weights['W_conv1']) + biases['b_conv1'] 
    conv1 = maxpool2d(conv1) 
    
    conv2 = conv2d(conv1, weights['W_conv2']) + biases['b_conv2'] 
    conv2 = maxpool2d(conv2)

    fc = tf.reshape(conv2,[-1,W_fc_input_size*W_fc_input_size*64])
    fc = tf.nn.relu( tf.matmul( fc, weights['W_fc'] ) + biases['b_fc'] )

    #fc = tf.nn.dropout(fc,keep_rate)

    output = tf.matmul( fc, weights['out'] ) + biases['out']
    

    return output

def neural_network_model(data):

    # (input_data * weights) + biases

    n_nodes_hl1 = 500
    n_nodes_hl2 = 500
    n_nodes_hl3 = 500

    hidden_1_layer = {'weights' : tf.Variable(tf.random_normal([input_size,n_nodes_hl1])), 'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights' : tf.Variable(tf.random_normal([n_nodes_hl1,n_nodes_hl2])), 'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights' : tf.Variable(tf.random_normal([n_nodes_hl2,n_nodes_hl3])), 'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights' : tf.Variable(tf.random_normal([n_nodes_hl3,n_classes])), 'biases': tf.Variable(tf.random_normal([n_classes]))}

    l1 = tf.add(tf.matmul(data,hidden_1_layer['weights']) , hidden_1_layer['biases'] )
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weights']) , hidden_2_layer['biases'] )
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weights']) , hidden_3_layer['biases'] )
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

    return output

def train_neural_network(x,train_x,train_y,test_x,test_y):

    prediction = convolutional_neural_network_model(x)
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(logits=prediction,labels=y))

    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 6

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

            print("Epoch", epoch, 'completed out of',hm_epochs,'loss:',epoch_loss)
        
        correct = tf.equal(tf.argmax(prediction,1),tf.argmax(y,1))

        accuracy = tf.reduce_mean(tf.cast(correct,'float'))

        saver.save(sess,'tf_model/model.ckpt')

        accuracy_eval = accuracy.eval({x:test_x,y:test_y})

        print('Accuracy:',accuracy_eval)

        F = open("user/nn.txt","w")
        F.write(str(accuracy_eval) + "\n")
        F.write(str(len(train_x)) + "." + str(len(test_x)))
        F.close()


def use_neural_network(x,input_data):

    prediction = neural_network_model(x)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        try:
            saver.restore(sess,'tf_model/model.ckpt')
        except:
            print("model not found")
            return None

        result = sess.run( tf.argmax( prediction.eval( feed_dict={ x:[input_data] } ), 1 ) )
        if result[0] == 0:
            return "like"
        elif  result[0] == 1:
            return "dislike"

def test_neural_network():
    count = len(os.listdir(directory))
    i = random.randint(0, count-1)
    filename = os.listdir(directory)[i]
    print(filename.split(".")[0])
    img = Image.open(os.path.join(directory, filename))
    img1 = img.convert('LA')
    imgmat = list(img1.getdata(band=0))
    rate = use_neural_network(x,imgmat)
    print(rate)
    plt.imshow(img)
    plt.show()

train_x,train_y,test_x,test_y = create_data_set_and_labels()

n_classes = 2
batch_size = 100

input_size = len(train_x[0])
input_width = int(math.sqrt(input_size))

x = tf.placeholder('float', [None, input_size])
y = tf.placeholder('float')
curren_epoch = tf.Variable(0)

keep_rate = 0.8
keep_prob = tf.placeholder(tf.float32)

saver = tf.train.Saver()

directory = "images"
train_neural_network(x,train_x,train_y,test_x,test_y)
#test_neural_network()

