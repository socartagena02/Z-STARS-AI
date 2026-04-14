import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
ruta_csv = BASE_DIR / "datos_sinteticos.csv"

df = pd.read_csv(ruta_csv)

X = df[
    [
        'fallos',
        'tiempo_reaccion_promedio',
        'puntuacion',
        'tiempo_total',
        'dificultad',
        'juego'
    ]
]

y = df['estado_cognitivo']

x_train, x_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

preprocessor = ColumnTransformer(
    transformers=[
        ('juego_cat', OneHotEncoder(handle_unknown='ignore'), ['juego'])
    ],
    remainder='passthrough'
)

pipeline = Pipeline([
    ('prep', preprocessor),
    ('model', RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    ))
])

pipeline.fit(x_train, y_train)

joblib.dump(pipeline, BASE_DIR / "modelo_cognitivo.pkl")

y_pred = pipeline.predict(x_test)

print("Reporte de Clasificación")
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=sorted(y.unique()),
    yticklabels=sorted(y.unique())
)

plt.xlabel('Predicción IA')
plt.ylabel('Valor real')
plt.title('Matriz de Confusión - Z-STARS AI')
plt.show()