from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (classification_report,confusion_matrix)
from sklearn.model_selection import (train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (OneHotEncoder)

BASE_DIR = Path(__file__).resolve().parent
DATASET = (BASE_DIR / "datos_sinteticos.csv")
MODEL = (BASE_DIR / "modelo_cognitivo.pkl")

FEATURES_NUMERICS =[
    "puntuacion_normalizada",
    "fallos_normalizados",
    "tiempo_total",
    "dificultad",
    "nivel_maximo_alcanzado",
    "reaccion_normalizada"
]

FEATURES_CATEGORIES = ["juego"]
TARGET = "indicador_rendimiento"
df = pd.read_csv(DATASET)
X = df[FEATURES_NUMERICS + FEATURES_CATEGORIES]
y = df[TARGET]
X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
)

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median",
            add_indicator=True,
        ),
    ),
])


categorical_pipeline = Pipeline([
    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore",
        ),
    ),
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        FEATURES_NUMERICS,
    ),
    (
        "categorical",
        categorical_pipeline,
        FEATURES_CATEGORIES,
    ),
])


classifier = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
)


pipeline = Pipeline([
    (
        "preprocessor",
        preprocessor,
    ),
    (
        "classifier",
        classifier,
    ),
])


pipeline.fit(
    X_train,
    y_train,
)


y_pred = pipeline.predict(
    X_test
)


print(
    "\nREPORTE DE CLASIFICACIÓN\n"
)

print(
    classification_report(
        y_test,
        y_pred,
        digits=3,
    )
)


print(
    "\nMATRIZ DE CONFUSIÓN\n"
)

labels = [
    "Bajo",
    "Intermedio",
    "Alto",
]

print(
    confusion_matrix(
        y_test,
        y_pred,
        labels=labels,
    )
)


print(
    "\nDISTRIBUCIÓN DE CLASES\n"
)

print(
    y.value_counts(
        normalize=True
    ).round(3)
)


joblib.dump(
    pipeline,
    MODEL,
)


print(
    f"\nModelo guardado en: {MODEL}"
)