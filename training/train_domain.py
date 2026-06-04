import os
import shutil
import random
import tensorflow as tf
import keras
from keras import layers, models, callbacks, optimizers
from keras.applications import MobileNetV3Small

# 1. Configuración de GPU
gpus = tf.config.list_physical_devices('GPU')
is_gpu = len(gpus) > 0

if is_gpu:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("No se detectó GPU. Corriendo clasificación de dominio en modo CPU optimizado.")

# 2. Generación dinámica del dataset de Dominio (Satelital vs Terrestre)
SRC_SAT = "datasets/eurosat"
SRC_TERR = "datasets/terrestrial"
DST_DOMAIN = "datasets/domain"

print("Preparando dataset binario de dominio...")

if not os.path.exists(SRC_SAT) or not os.path.exists(SRC_TERR):
    print("Error: Por favor corre primero 'train_satellite.py' y 'train_terrestrial.py' para descargar los datasets base.")
    exit(1)

# Crear carpetas de destino
os.makedirs(os.path.join(DST_DOMAIN, "satellite"), exist_ok=True)
os.makedirs(os.path.join(DST_DOMAIN, "terrestrial"), exist_ok=True)

# Limpiar si ya existen imágenes viejas para evitar acumulación
shutil.rmtree(os.path.join(DST_DOMAIN, "satellite"))
shutil.rmtree(os.path.join(DST_DOMAIN, "terrestrial"))
os.makedirs(os.path.join(DST_DOMAIN, "satellite"), exist_ok=True)
os.makedirs(os.path.join(DST_DOMAIN, "terrestrial"), exist_ok=True)

# Contar cuántas imágenes copiar
NUM_SAMPLES = 2000 if is_gpu else 150

def collect_and_copy_images(src_root, dest_folder, limit):
    all_images = []
    for root, _, files in os.walk(src_root):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                all_images.append(os.path.join(root, f))
    
    random.shuffle(all_images)
    selected = all_images[:limit]
    
    print(f"Copiando {len(selected)} imágenes hacia {dest_folder}...")
    for idx, path in enumerate(selected):
        ext = os.path.splitext(path)[1]
        dest_path = os.path.join(dest_folder, f"img_{idx}{ext}")
        shutil.copy2(path, dest_path)

# Copiar imágenes
collect_and_copy_images(SRC_SAT, os.path.join(DST_DOMAIN, "satellite"), NUM_SAMPLES)
collect_and_copy_images(SRC_TERR, os.path.join(DST_DOMAIN, "terrestrial"), NUM_SAMPLES)

# 3. Carga de datos
IMG_SIZE = (128, 128) # Más pequeño para eficiencia del clasificador binario
BATCH_SIZE = 32

train_ds = keras.utils.image_dataset_from_directory(
    DST_DOMAIN,
    validation_split=0.2,
    subset="training",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

val_ds = keras.utils.image_dataset_from_directory(
    DST_DOMAIN,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

# Prefetching
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# 4. Definición de Modelo Binario Liviano (MobileNetV3)
base_model = MobileNetV3Small(
    input_shape=(128, 128, 3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

inputs = layers.Input(shape=(128, 128, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(1, activation="sigmoid", name="output")(x)

model = models.Model(inputs, outputs)

# 5. Compilación y Callbacks
checkpoint_path = "../backend/model/domain_classifier.keras"
my_callbacks = [
    callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ModelCheckpoint(checkpoint_path, save_best_only=True, monitor="val_accuracy")
]

model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-3),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# 6. Entrenamiento
EPOCHS = 8 if is_gpu else 2
print("\n=== ENTRENANDO CLASIFICADOR DE DOMINIO ===")
model.fit(
    train_ds,
    epochs=EPOCHS,
    validation_data=val_ds,
    callbacks=my_callbacks
)

print(f"\nModelo de clasificación de dominio guardado en: {checkpoint_path}")
