import os
import numpy as np
import tensorflow as tf
import keras
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import json

# 1. Configuración de GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

def evaluate_model(model_path, dataset_dir, img_size, output_name):
    print(f"\n=== EVALUANDO MODELO: {model_path} ===")
    if not os.path.exists(model_path):
        print(f"Error: Modelo no encontrado en {model_path}")
        return
        
    # Cargar modelo
    model = keras.models.load_model(model_path, compile=False)
    
    # Cargar dataset de validación
    val_ds = keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=img_size,
        batch_size=32,
        label_mode="categorical",
        shuffle=False # Muy importante: False para alinear predicciones y etiquetas
    )
    
    class_names = val_ds.class_names
    
    if not tf.config.list_physical_devices('GPU'):
        print("Slicing validation dataset para evaluación rápida en CPU...")
        val_ds = val_ds.take(5) # 160 imágenes para métricas rápidas
    
    # Obtener etiquetas verdaderas e imágenes
    y_true = []
    y_pred = []
    
    print("Realizando inferencia en el conjunto de validación...")
    for images, labels in val_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))
        
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Calcular reporte de clasificación
    labels_list = list(range(len(class_names)))
    report = classification_report(y_true, y_pred, labels=labels_list, target_names=class_names, output_dict=True, zero_division=0)
    print("\nReporte de Clasificación:")
    print(classification_report(y_true, y_pred, labels=labels_list, target_names=class_names, zero_division=0))
    
    # Guardar reporte JSON
    os.makedirs("results", exist_ok=True)
    with open(f"results/{output_name}_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    # Calcular y graficar matriz de confusión
    cm = confusion_matrix(y_true, y_pred, labels=labels_list)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Matriz de Confusion - {output_name.upper()}')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45, ha="right")
    plt.yticks(tick_marks, class_names)
    
    # Agregar valores en celdas
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
            
    plt.tight_layout()
    plt.ylabel('Clase Real')
    plt.xlabel('Prediccion')
    
    plot_path = f"results/{output_name}_confusion_matrix.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Matriz de confusión guardada en: {plot_path}")

if __name__ == "__main__":
    # Evaluar Satelital (EuroSAT)
    evaluate_model(
        model_path="../backend/model/satellite_classifier.keras",
        dataset_dir="datasets/eurosat",
        img_size=(160, 160),
        output_name="satellite"
    )
    
    # Evaluar Terrestre
    evaluate_model(
        model_path="../backend/model/terrestrial_classifier.keras",
        dataset_dir="datasets/terrestrial",
        img_size=(160, 160),
        output_name="terrestrial"
    )
