# AI - ML Models

## Setup
### Setup GPU's on Apple Silicon
Get started
1. Set up the environment
- Virtual environment:
```bash
python3 -m venv ~/venv-metal
source ~/venv-metal/bin/activate
python -m pip install -U pip
```

2. Install base TensorFlow
- For TensorFlow version 2.13 or later:
```bash
python -m pip install tensorflow
For TensorFlow version 2.12 or earlier:
python -m pip install tensorflow-macos
```

3. Install tensorflow-metal plug-in
```bash
python -m pip install tensorflow-metal
```

4. Verify
You can verify using a simple script:
```python
import tensorflow as tf

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
```