import os
import tensorflow as tf
import keras
from keras import layers, models, callbacks, optimizers
from keras.applications import EfficientNetB0
import urllib.request
import zipfile
import shutil

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

# 2. Descarga y Extracción del Dataset EuroSAT (RGB)
DATASET_URL = "https://zenodo.org/records/7711810/files/EuroSAT_RGB.zip"
DATASET_DIR = "datasets/eurosat"
ZIP_FILE = "datasets/eurosat.zip"

os.makedirs("datasets", exist_ok=True)

if not os.path.exists(DATASET_DIR):
    if not os.path.exists(ZIP_FILE):
        # Si ya descargamos test_eurosat.zip, lo usamos
        if os.path.exists("../test_eurosat.zip"):
            print("Copiando test_eurosat.zip descargado...")
            shutil.copy2("../test_eurosat.zip", ZIP_FILE)
        elif os.path.exists("test_eurosat.zip"):
            print("Copiando test_eurosat.zip...")
            shutil.copy2("test_eurosat.zip", ZIP_FILE)
        else:
            print(f"Descargando EuroSAT RGB desde {DATASET_URL}...")
            urllib.request.urlretrieve(DATASET_URL, ZIP_FILE)
            print("Descarga completada.")
    
    print("Extrayendo dataset...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall("datasets")
    
    # Adaptar estructura
    extracted_folders = ["datasets/EuroSAT_RGB", "datasets/2750", "datasets/EuroSAT-master", "datasets/EuroSAT"]
    for folder in extracted_folders:
        if os.path.exists(folder):
            os.rename(folder, DATASET_DIR)
            break
    print("Dataset listo en:", DATASET_DIR)
else:
    print("EuroSAT dataset ya existe localmente.")

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
NUM_CLASSES = len(class_names)
print("Clases detectadas:", class_names)

# Optimización para CPU si no hay GPU (reducir tamaño del dataset)
if not is_gpu:
    print("Slicing datasets para entrenamiento rápido en CPU...")
    train_ds = train_ds.take(15)  # 480 imágenes
    val_ds = val_ds.take(5)      # 160 imágenes
    EPOCHS_CNN = 2
    EPOCHS_TL = 2
    EPOCHS_FT = 2
else:
    EPOCHS_CNN = 10
    EPOCHS_TL = 15
    EPOCHS_FT = 15

# Optimizar rendimiento de carga de datos
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# 4. Data Augmentation
data_augmentation = models.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.15),
], name="data_augmentation")

os.makedirs("../backend/model", exist_ok=True)

# ==========================================
# 5. MODELO 1: CNN PROPIA DESDE CERO
# ==========================================
print("\n=== ENTRENANDO MODELO 1: CNN PROPIA DESDE CERO ===")
cnn_model = models.Sequential([
    layers.Rescaling(1./255, input_shape=(160, 160, 3)),
    data_augmentation,
    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(NUM_CLASSES, activation="softmax")
])

cnn_model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

cnn_path = "../backend/model/cnn_eurosat.keras"
callbacks_cnn = [
    callbacks.EarlyStopping(patience=3, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ModelCheckpoint(cnn_path, save_best_only=True, monitor="val_accuracy")
]

cnn_model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_CNN,
    callbacks=callbacks_cnn
)
print(f"Modelo CNN propia guardado en: {cnn_path}")


# ==========================================
# 6. MODELO 2: TRANSFER LEARNING (CONGELADO)
# ==========================================
print("\n=== ENTRENANDO MODELO 2: TRANSFER LEARNING CON EFFICIENTNETB0 ===")
base_model = EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(160, 160, 3)
)
base_model.trainable = False  # Congelar base model

inputs = layers.Input(shape=(160, 160, 3))
x = data_augmentation(inputs)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)
efficient_model = models.Model(inputs, outputs)

efficient_model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-3),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

tl_path = "../backend/model/efficientnet_eurosat.keras"
callbacks_tl = [
    callbacks.EarlyStopping(patience=3, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ModelCheckpoint(tl_path, save_best_only=True, monitor="val_accuracy")
]

efficient_model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_TL,
    callbacks=callbacks_tl
)
print(f"Modelo Transfer Learning guardado en: {tl_path}")


# ==========================================
# 7. MODELO 3: FINE-TUNING (DESCONGELADO PARCIAL)
# ==========================================
print("\n=== ENTRENANDO MODELO 3: FINE-TUNING DE EFFICIENTNETB0 ===")
base_model.trainable = True
# Congelar todas excepto las últimas 20 capas del base_model
for layer in base_model.layers[:-20]:
    layer.trainable = False

efficient_model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

final_path = "../backend/model/modelo_final_eurosat.keras"
callbacks_ft = [
    callbacks.EarlyStopping(patience=3, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ModelCheckpoint(final_path, save_best_only=True, monitor="val_accuracy")
]

efficient_model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FT,
    callbacks=callbacks_ft
)
print(f"Modelo Fine-Tuning guardado en: {final_path}")

# Copiar el modelo final para el enrutador jerárquico del backend
shutil.copy2(final_path, "../backend/model/satellite_classifier.keras")
print("Copia del modelo final creada en: ../backend/model/satellite_classifier.keras")
