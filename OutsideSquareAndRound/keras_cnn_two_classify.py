# _*_coding:utf-8_*_
from keras.callbacks import TensorBoard
from keras.layers import Dense, Dropout, MaxPooling2D, Flatten, Convolution2D
from keras.models import Sequential
from keras import backend as K
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt


def load_train_test_data(train, test):
    np.random.shuffle(train)
    labels = train[:, -1]
    test = np.array(test)
    data, data_test = data_modify_suitable_train(train, True), data_modify_suitable_train(test, False)
    print(data.shape, data_test.shape)  # (4000, 40, 40, 1) (3550, 40, 40, 1)
    train_x, test_x, train_y, test_y = train_test_split(data, labels, test_size=0.33)  # test_size=0.7
    return train_x, train_y, test_x, test_y, data_test


def data_modify_suitable_train(data_set=None, type=True):
    if data_set is not None:
        data = []
        if type is True:
            np.random.shuffle(data_set)
            # data = data_set[:, 0: data_set.shape[1] - 1]
            data = data_set[:, 0: -1]
            print(data.shape)
        else:
            data = data_set
    data = np.array([np.reshape(i, (40, 40)) for i in data])
    data = np.array([median_filter(i, size=(3, 3)) for i in data])
    data = np.array([(i > 1) * 256 for i in data])
    data = np.array([np.reshape(i, (i.shape[0], i.shape[1], 1)) for i in data])
    return data


def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2 * ((precision * recall) / (precision + recall))


def bulit_model(train, test):
    model = Sequential()
    model.add(Convolution2D(filters=8,
                            kernel_size=(5, 5),
                            input_shape=(40, 40, 1),
                            activation='relu'))
    model.add(Convolution2D(filters=16,
                            kernel_size=(3, 3),
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(4, 4)))
    model.add(Convolution2D(filters=16,
                            kernel_size=(3, 3),
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(4, 4)))
    model.add(Flatten())
    model.add(Dense(units=128,
                    activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(units=1,
                    activation='sigmoid'))
    # 完成模型的搭建后，使用.compile方法来编译模型
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy', f1])
    model.summary()
    return model


def bulit_model_new(train, test):
    n_filter = 32
    model = Sequential()
    model.add(Convolution2D(filters=n_filter,
                            kernel_size=(5, 5),
                            input_shape=(40, 40, 1),
                            activation='relu'))
    model.add(Convolution2D(filters=n_filter,
                            kernel_size=(5, 5),
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Convolution2D(filters=n_filter,
                            kernel_size=(5, 5),
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Convolution2D(filters=n_filter,
                            kernel_size=(3, 3),
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(units=128,
                    activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy', f1])
    model.summary()
    return model

def train_models(train, test, batch_size=64, epochs=20, model=None):
    train_x, train_y, test_x, test_y, t = load_train_test_data(train, test)
    # print(train_x.shape, train_y.shape, test_x.shape, test_y.shape, t.shape)
    if model is None:
        # model = bulit_model(train, test)
        model = bulit_model_new(train, test)
        history = model.fit(train_x, train_y,
                            batch_size=batch_size,
                            epochs=epochs,
                            validation_split=0.2)
        print("刻画损失函数在训练与验证集的变化")
        plt.plot(history.history['loss'], label='train')
        plt.plot(history.history['val_loss'], label='valid')
        plt.legend()
        plt.show()
        #   ##### 注意这个t
        pred_prob = model.predict(t, batch_size=batch_size, verbose=1)
        pred = np.array(pred_prob > 0.5).astype(int)
        score = model.evaluate(test_x, test_y, batch_size=batch_size)
        print('score is %s' % score)
        print("刻画预测结果与测试结果")
        return pred


if __name__ == '__main__':
    train = pd.read_csv('datain/train.csv')
    test = pd.read_csv('datain/test.csv')
    # train = train.iloc[:,1:]
    # test = test.iloc[:,1:]
    # print(type(train))
    train = np.array(train.drop('id', axis=1))
    test = np.array(test.drop('id', axis=1))
    # print(type(train))

    load_train_test_data(train, test)

    # pred = train_models(train, test)
    # submit = pd.read_csv('datain/sample_submit.csv')
    # submit['y'] = pred
    # submit.to_csv('my_CNN_prediction.csv', index=False)
