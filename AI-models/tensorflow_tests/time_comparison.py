from time import process_time

def testgpu():
    t0 = process_time()
    import tensorflow as tf
    tf.config.list_physical_devices()
    cifar = tf.keras.datasets.cifar100
    (x_train, y_train), (x_test, y_test) = cifar.load_data()
    model = tf.keras.applications.ResNet50(
        include_top=True,
        weights=None,
        input_shape=(32, 32, 3),
        classes=100,)
    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
    model.compile(optimizer="adam", loss=loss_fn, metrics=["accuracy"])
    model.fit(x_train, y_train, epochs=5, batch_size=64)
    t1 = process_time()
    print("Total time with gpu: ", t1-t0)

def testcpu():
    t0 = process_time()
    import tensorflow as tf
    with tf.device('/CPU:0'):
        tf.config.list_physical_devices()
        cifar = tf.keras.datasets.cifar100
        (x_train, y_train), (x_test, y_test) = cifar.load_data()
        model = tf.keras.applications.ResNet50(
            include_top=True,
            weights=None,
            input_shape=(32, 32, 3),
            classes=100,)
        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        model.compile(optimizer="adam", loss=loss_fn, metrics=["accuracy"])
        model.fit(x_train, y_train, epochs=5, batch_size=64)
        t1 = process_time()
        print("Total time with cpu: ", t1-t0)

if __name__ == '__main__':
    testgpu()
    testcpu()