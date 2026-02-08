import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (roc_auc_score, classification_report, 
                             confusion_matrix, ConfusionMatrixDisplay)

import lightgbm as lgb

import shap

import joblib
import matplotlib.pyplot as plt

print(f"dataframe creation")
df = pd.read_csv('data/cs-training.csv', index_col=0)
print(f"dataset length: {df.shape}")
print("first five rows:\n{df.head()}\n")
print(f"Columns information:\n")
df.info()
print(df['SeriousDlqin2yrs'].value_counts(normalize=True))

print(f"\n How many missing values are there?")
print(df.isnull().sum())

# creating backup
data = df.copy()

data['MonthlyIncome'].fillna(data['MonthlyIncome'].median(), inplace=True)
data['NumberOfDependents'].fillna(data['NumberOfDependents'].mode()[0], inplace=True)

numeric_cols = ['RevolvingUtilizationOfUnsecuredLines', 'DebtRatio', 'MonthlyIncome']
for col in numeric_cols:
    upper_limit = data[col].quantile(0.99)
    data.loc[data[col] > upper_limit, col] = upper_limit # cropping the outliers

X = data.drop('SeriousDlqin2yrs', axis=1)
y = data['SeriousDlqin2yrs']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nLength of train and test datsets:")
print(f"   X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"   X_test: {X_test.shape}, y_test: {y_test.shape}")

lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.05,
    num_leaves=31,
    max_depth=-1,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)


lgb_model.fit(X_train, y_train)

print(f"model has been trained")

# creating an arrays of statuses with 1 default and 0 vice versa
# second variable is an array of tuples of true and false robabilities
y_pred = lgb_model.predict(X_test)
y_pred_proba = lgb_model.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"base model score")
print(f"ROC-AUC: {roc_auc:.4f}")
print("classification Report:")
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap=plt.cm.Blues)
plt.title('confsion matrix')
plt.show()

# hyperparameters with cross-validation
param_grid = {
    'num_leaves': [20, 31, 40],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200],
    'min_child_samples': [10, 20, 30]
}

# creating model for lightgbm (gradient boosting, each 
# next tree makes better decisions)
lgb_tuner = lgb.LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1)

# cross-validation for BEST parameters
grid_search = GridSearchCV(
    estimator=lgb_tuner, # model
    param_grid=param_grid,
    scoring='roc_auc',
    cv=3,
    verbose=1,
    n_jobs=-1
)

# iterating through parameters, searching for the best model
grid_search.fit(X_train, y_train)

print(f"best parameters: {grid_search.best_params_}")
print(f"best roc-auc: {grid_search.best_score_:.4f}")

best_model = grid_search.best_estimator_

y_pred_best = best_model.predict(X_test)
y_pred_proba_best = best_model.predict_proba(X_test)[:, 1]

roc_auc_best = roc_auc_score(y_test, y_pred_proba_best)
print(f"final model score:")
print(f"roc-auc: {roc_auc_best:.4f}")
print(f"final model:")
print(classification_report(y_test, y_pred_best))

print(f"shap exPlanations...")

print("creting explainer based on best model")
explainer = shap.TreeExplainer(best_model)

# we can choose how many samples we want to use
shap_sample = X_test[:100]
shap_values = explainer.shap_values(shap_sample)

print("Features importance by shap")
shap.summary_plot(shap_values, shap_sample, plot_type="bar", show=False)
plt.title("Features importance by shap")
plt.tight_layout()
plt.show()

print("Features influence on predictions")
shap.summary_plot(shap_values, shap_sample, show=False)
plt.title("Features influence on predictions")
plt.tight_layout()
plt.show()

print("Client explanations")
print(explainer.expected_value)
sample_idx = 0
print(f"exPlanation for specific client id {sample_idx}")

single_shap_explanation = explainer(shap_sample.iloc[sample_idx: sample_idx + 1])

shap.force_plot(
    single_shap_explanation.base_values[0],  # base value
    single_shap_explanation.values[0],       # features influence
    shap_sample.iloc[sample_idx],            # features info
    matplotlib=True,
    show=False
)
plt.title(f"exPlanation for specific client id {sample_idx}")
plt.tight_layout()
plt.show()

import os
os.makedirs('saved_models', exist_ok=True)

joblib.dump(best_model, 'saved_models/lightgbm_credit_model.pkl')
joblib.dump(explainer, 'saved_models/shap_explainer.pkl')
joblib.dump(X_train.columns, 'saved_models/feature_names.pkl')

print("server futre integration...")

example_client_data = X_test.iloc[0:1].to_dict(orient='records')[0]
for key, value in example_client_data.items():
    print(f"   {key}: {value}")

# model's prediction based on the client's data
prediction = best_model.predict_proba(pd.DataFrame([example_client_data]))[0][1]
print(f"default probability: {prediction:.1%}")
print(f"congratulations, granny passed the credit check")