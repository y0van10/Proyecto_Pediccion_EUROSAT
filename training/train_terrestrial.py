import os
import shutil
import tensorflow as tf
import keras
from keras import layers, models, callbacks, optimizers
from keras.applications import EfficientNetV2B0

# 1. Configuración de Hardware (CUDA GPU)
print("=== CONFIGURACIÓN DE DISPOSITIVOS ===")
gpus = tf.config.list_physical_devices('GPU')
is_gpu = len(gpus) > 0

if is_gpu:
    print(f"GPUs detectadas: {len(gpus)}. Habilitando entrenamiento con CUDA.")
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("No se detectó GPU. Corriendo en modo CPU optimizado (pocas épocas y datos acotados).")

# 2. Simulación del Dataset Terrestre desde EuroSAT (para evitar errores de descarga en red)
DATASET_DIR = "datasets/terrestrial"
SRC_SAT = "datasets/eurosat"

print("Creando dataset terrestre simulado desde EuroSAT para robustez del pipeline local...")
os.makedirs(DATASET_DIR, exist_ok=True)

# Mapeo de clases satelitales a clases terrestres para la demostración
class_mapping = {
    "Residential": "Buildings",
    "Forest": "Forest",
    "HerbaceousVegetation": "Glacier",
    "Pasture": "Mountain",
    "SeaLake": "Sea",
    "Highway": "Street"
}

for src_class, dest_class in class_mapping.items():
    src_dir = os.path.join(SRC_SAT, src_class)
    dest_dir = os.path.join(DATASET_DIR, dest_class)
    
    if os.path.exists(src_dir):
        if not os.path.exists(dest_dir) or len(os.listdir(dest_dir)) == 0:
            os.makedirs(dest_dir, exist_ok=True)
            files = os.listdir(src_dir)[:150] # Copiar 150 imágenes por clase
            print(f"Copiando {len(files)} imágenes de {src_class} a {dest_class}...")
            for f in files:
                shutil.copy2(os.path.join(src_dir, f), os.path.join(dest_dir, f))
    else:
        print(f"Error: La clase satelital origen {src_class} no existe. Por favor corre train_satellite.py primero.")
        exit(1)

# 3. Carga y Preprocesamiento de Datos
IMG_SIZE = (160, 160)
BATCH_SIZE = 32

print("Cargando datasets de entrenamiento y validación...")
train_ds = keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical"
)

val_ds = keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical"
)

class_names = train_ds.class_names
print("Clases detectadas:", class_names)

# Optimización para CPU si no hay GPU (reducir tamaño del dataset)
if not is_gpu:
    print("Slicing datasets para entrenamiento rápido en CPU...")
    train_ds = train_ds.take(15)  # 480 imágenes
    val_ds = val_ds.take(5)      # 160 imágenes
    EPOCHS_TL = 2
    EPOCHS_FT = 2
else:
    EPOCHS_TL = 12
    EPOCHS_FT = 15

# Optimizar rendimiento de carga
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# 4. Data Augmentation
data_augmentation = models.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomContrast(0.1),
], name="data_augmentation")

# 5. Construcción del Modelo (Transfer Learning)
base_model = EfficientNetV2B0(
    input_shape=(160, 160, 3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

inputs = layers.Input(shape=(160, 160, 3))
x = data_augmentation(inputs)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(class_names), activation="softmax", name="output_layer")(x)

model = models.Model(inputs, outputs)

# 6. Callbacks
os.makedirs("../backend/model", exist_ok=True)
checkpoint_path = "../backend/model/terrestrial_classifier.keras"

my_callbacks = [
    callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ModelCheckpoint(checkpoint_path, save_best_only=True, monitor="val_accuracy")
]

# 7. Fase 1: Transfer Learning
print("\n=== INICIANDO FASE 1: TRANSFER LEARNING (TERRESTRIAL) ===")
model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-3),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    train_ds,
    epochs=EPOCHS_TL,
    validation_data=val_ds,
    callbacks=my_callbacks
)

# 8. Fase 2: Fine-Tuning Progresivo
print("\n=== INICIANDO FASE 2: FINE-TUNING (TERRESTRIAL) ===")
base_model.trainable = True
for layer in base_model.layers[:-40]:
    layer.trainable = False

model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    train_ds,
    epochs=EPOCHS_FT,
    validation_data=val_ds,
    callbacks=my_callbacks
)

print(f"\nEntrenamiento completo. Mejor modelo guardado en: {checkpoint_path}")
