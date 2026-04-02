import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder 
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

BASE_DIR = Path(__file__).resolve().parent
ruta_csv = BASE_DIR / "datos_sinteticos.csv"

df = pd.read_csv(ruta_csv)
le = LabelEncoder()
df['estado_cognitivo'] = le.fit_transform(df['estado_cognitivo'])

X = df[['fallos', 'tiempo_reaccion_promedio']]
y = df['estado_cognitivo']

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)

joblib.dump(model, BASE_DIR / "modelo_cognitivo.pkl")
joblib.dump(le, BASE_DIR / "label_encoder.pkl")

importances = model.feature_importances_
features = X.columns 

plt.figure(figsize=(10, 5))
plt.barh(features, importances, color='teal')
plt.xlabel('Importancia Relativa')
plt.title('Qué influye más en el diagnóstico de Z-STARS AI?')
plt.show()

y_pred = model.predict(x_test)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.xlabel('Predicción de la IA')
plt.ylabel('Valor Real (Sintético)')
plt.title('Matriz de Confusión - Z-STARS AI')
plt.show()
print("Reporte de Clasificación")
print(classification_report(y_test, y_pred, target_names=le.classes_))