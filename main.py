from salvador import define_discriminator, define_gan, define_generator, load_real_samples, train, \
    create_gif, remove_plots, remove_models, plot_history, generate_fake_samples, load_from_path

# webdriver_path = '/Users/tinyrogue/PycharmProjects/Salvador/chromedriver'

# Path to database folder
path = 'images/horizontal_forests'

print('Starting ')
latent_dim = 100

print('Defining discriminator...')
d_model = define_discriminator()
print('Discriminator defined')

print('Defining generator...')
g_model = define_generator(latent_dim)
print('Generator defined')

print('Defining GAN...')
gan_model = define_gan(g_model, d_model)
print('GAN defined')

print('Loading dataset...')
dataset = load_from_path(path)
# dataset = load_real_samples(True)
print('Dataset loaded')

print('Training model...')
n_batch_cifar = 64
n_batch_for_real = 64
d_loss_real_hist, d_loss_fake_hist, g_loss_hist = list(), list(), list()
train(d_loss_real_hist, d_loss_fake_hist, g_loss_hist, g_model, d_model, gan_model, dataset, latent_dim, n_epochs=31,
      n_batch=n_batch_for_real)

# plot_history(d_loss_real_hist, d_loss_fake_hist, g_loss_hist)
print('Model trained')

# create_gif('landscapes')
# remove_plots()
# remove_models()

# from salvador import generate_from_model

# generate_from_model('models/generator_model_009.h5', n_images=20)
