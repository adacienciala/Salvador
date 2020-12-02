from numpy import zeros, ones
from numpy.random import randn, randint
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, Reshape, Flatten, Conv2D, Conv2DTranspose, LeakyReLU, Dropout
from keras.datasets.cifar10 import load_data
from matplotlib import pyplot
from glob import glob
from numpy import array, asarray
from PIL import Image
import imageio
from os import remove


def define_discriminator(in_shape=(128, 128, 3)):
    model = Sequential()
    model.add(Conv2D(64, (3, 3), padding='same', input_shape=in_shape))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2D(128, (3, 3), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2D(128, (3, 3), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2D(256, (3, 3), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Flatten())
    model.add(Dropout(0.4))
    model.add(Dense(1, activation='sigmoid'))
    opt = Adam(lr=0.0002, beta_1=0.5)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model


def define_generator(latent_dim):
    model = Sequential()
    n_nodes = 256 * 16 * 16
    model.add(Dense(n_nodes, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Reshape((16, 16, 256)))
    model.add(Conv2DTranspose(128, (4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2DTranspose(128, (4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2DTranspose(128, (4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Conv2D(3, (3, 3), activation='tanh', padding='same'))
    return model


def define_gan(g_model, d_model):
    d_model.trainable = False
    model = Sequential()
    model.add(g_model)
    model.add(d_model)
    opt = Adam(lr=0.0002, beta_1=0.5)
    model.compile(loss='binary_crossentropy', optimizer=opt)
    return model


def to_load():
    file_list = glob("/content/drive/MyDrive/images/landscapes/*")
    temp = []
    i = 0
    for file in file_list:
        img = Image.open(file).resize((128, 128))
        temp.append(asarray(img))
        print(f"loaded {i}/{len(file_list)}: {file}")
        i = i + 1
    x = array(temp)
    return x


def load_real_samples(real_ones):
    if real_ones:
        train_x = to_load()
    else:
        (train_x, _), (_, _) = load_data()
    x = train_x.astype('float32')
    x = (x - 127.5) / 127.5
    return x


def generate_real_samples(dataset, n_samples):
    ix = randint(0, dataset.shape[0], n_samples)
    x = dataset[ix]
    y = ones((n_samples, 1))
    return x, y


def generate_latent_points(latent_dim, n_samples):
    x_input = randn(latent_dim * n_samples)
    x_input = x_input.reshape(n_samples, latent_dim)
    return x_input


def generate_fake_samples(g_model, latent_dim, n_samples):
    x_input = generate_latent_points(latent_dim, n_samples)
    x = g_model.predict(x_input)
    y = zeros((n_samples, 1))
    return x, y


def save_plot(examples, epoch, n=7):
    examples = (examples + 1) / 2.0
    for i in range(n * n):
        pyplot.subplot(n, n, 1 + i)
        pyplot.axis('off')
        pyplot.imshow(examples[i])
    pyplot.suptitle(f'Epoch: {epoch}')
    filename = 'plot%04d.png' % epoch
    pyplot.savefig(f'plots/{filename}')
    pyplot.close()


def summarize_performance(epoch, g_model, d_model, dataset, latent_dim, n_samples=150):
    x_real, y_real = generate_real_samples(dataset, n_samples)
    _, acc_real = d_model.evaluate(x_real, y_real, verbose=0)
    x_fake, y_fake = generate_fake_samples(g_model, latent_dim, n_samples)
    _, acc_fake = d_model.evaluate(x_fake, y_fake, verbose=0)
    print('>Accuracy real: %.0f%%, fake: %.0f%%' % (acc_real * 100, acc_fake * 100))
    filename = 'generator_model_%03d.h5' % epoch
    g_model.save(f'models/{filename}')


def train(d_loss_real_hist, d_loss_fake_hist, g_loss_hist, g_model, d_model, gan_model, dataset, latent_dim, n_epochs=200, n_batch=128):
    batch_per_epoch = int(dataset.shape[0] / n_batch)
    half_batch = int(n_batch / 2)
    for i in range(n_epochs):
        for j in range(batch_per_epoch):
            x_real, y_real = generate_real_samples(dataset, half_batch)
            d_loss1, _ = d_model.train_on_batch(x_real, y_real)
            x_fake, y_fake = generate_fake_samples(g_model, latent_dim, half_batch)
            d_loss2, _ = d_model.train_on_batch(x_fake, y_fake)
            x_gan = generate_latent_points(latent_dim, n_batch)
            y_gan = ones((n_batch, 1))
            g_loss = gan_model.train_on_batch(x_gan, y_gan)
            d_loss_real_hist.append(d_loss1)
            d_loss_fake_hist.append(d_loss2)
            g_loss_hist.append(g_loss)
            print('>%d, %d/%d, d1=%.3f, d2=%.3f g=%.3f' %
                  (i + 1, j + 1, batch_per_epoch, d_loss1, d_loss2, g_loss))
        if (i + 1) % 10 == 0:
            summarize_performance(i, g_model, d_model, dataset, latent_dim)
        x_fakes, _ = generate_fake_samples(g_model, latent_dim, 150)
        save_plot(x_fakes, i)


def create_gif(filename):
    with imageio.get_writer(f'{filename}.gif', mode='I') as writer:
        filenames = glob('plots/*')
        filenames.sort()
        for filename in filenames:
            print(filename)
            image = imageio.imread(filename)
            writer.append_data(image)


def remove_plots():
    for file in glob('plots/*'):
        remove(file)


def remove_models():
    for file in glob('models/*'):
        remove(file)

def plot_history(d1_hist, d2_hist, g_hist):
  # plot loss
  fig = pyplot.figure(figsize=(80, 8))
  pyplot.subplot(1, 1, 1)
  pyplot.plot(d1_hist, label='d-real')
  pyplot.plot(d2_hist, label='d-fake')
  pyplot.plot(g_hist, label='gen')
  pyplot.legend()
  pyplot.savefig('plot_loss.png')
  pyplot.close()