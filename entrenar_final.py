from pandas import read_csv
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error
import os
import matplotlib.pyplot as plt

dataframe = read_csv("data.csv", header=None, sep=',')
dataset = dataframe.values

X = dataset[:, 2:]
Y = dataset[:, 0:2]

lr = 0.00001
filas_entrada = dataset.shape[0]
columnas_entrada = dataset.shape[1] - 2
batch_size = 32

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
X_test, X_val, Y_test, Y_val = train_test_split(X_test, Y_test, test_size=0.5)

red = Sequential()

red.add(Dense(units=columnas_entrada, activation='relu'))

red.add(Dense(units=int(columnas_entrada / 3), activation='relu'))
red.add(Dropout(0.3))

red.add(Dense(units=int(columnas_entrada / 5), activation='relu'))
red.add(Dropout(0.3))

red.add(Dense(units=2, activation='linear'))

red.compile(loss='mean_squared_error', optimizer=Adam(lr=lr), metrics=['MeanSquaredError'])

early_stopping = EarlyStopping(patience=200, restore_best_weights=True)

resultado = red.fit(x=X_train, y=Y_train, batch_size=batch_size,
                    epochs=10000, validation_data=(X_val, Y_val),
                    verbose=2, callbacks=[early_stopping])

print(min(resultado.history['val_loss']))

Y_pred = red.predict(X_test)

mse = mean_squared_error(Y_test, Y_pred)

print(mse)

plt.style.use("ggplot")
plt.figure()
plt.plot(resultado.history['loss'], label="train_loss")
plt.title("Training Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.figure()
plt.plot(resultado.history['val_loss'], label="val_loss")
plt.title("Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

dir = '../modelo'

if not os.path.exists(dir):
    os.mkdir(dir)
red.save('modelo/modelo.h5')
red.save_weights('modelo/pesos.h5')
