import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from sklearn.model_selection import cross_val_score
import ydata_profiling

# read dataset
titanic_df = pd.read_csv('./Data/train.csv')  # to train
X_test = pd.read_csv('./Data/test.csv')  # to test
y_test = pd.read_csv('./Data/gender_submission.csv')  # to validation
X_train = titanic_df.drop('Survived', axis=1)
y_train = titanic_df['Survived']

# check the dataset profile report first
ydata_profiling.ProfileReport(titanic_df).to_file('./titanic_df_profile_report.html')

# define Pipeline for numeric transformer for imputation
number_tranformer_median = Pipeline(
    steps=[('imputer_median', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
number_tranformer_constant = Pipeline(
    steps=[('imputer_constant', SimpleImputer(strategy='constant', fill_value=0)), ('scaler', StandardScaler())])

# define Piple for categorical transformer by OneHoeEncoder and OridnalEncoder
categorical_tranformer = OneHotEncoder(handle_unknown='ignore', sparse=False)
# categorical_tranformer = OrdinalEncoder()

# set preprocessor
preprocessor = ColumnTransformer(transformers=[('numb_median', number_tranformer_median, ['Age']),
                                               ('numb_constant', number_tranformer_constant, ['Fare']),
                                               ('drop_out', 'drop', ['PassengerId', 'Name', 'Ticket']),
                                               ('category', categorical_tranformer, ['Embarked', 'Sex', 'Pclass'])])

# set Pipleline for each MDL
lr_clf = Pipeline(steps=[('prepro', preprocessor), (
'classifier', LogisticRegression(solver='liblinear', warm_start=True, tol=0.01, random_state=20))])
dt_clf = Pipeline(steps=[('prepro', preprocessor), ('classifier', DecisionTreeClassifier(random_state=20))])
rf_clf = Pipeline(steps=[('prepro', preprocessor),
                         ('classifier', RandomForestClassifier(random_state=20, n_estimators=300, max_depth=23))])
lgb_clf = Pipeline(
    steps=[('prepro', preprocessor), ('classifier', lgb.LGBMClassifier(random_state=20, n_estimators=300))])


# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=20)


def get_score(n_estimators):
    """
    temp test function: get cross-validation by negative MAE score(not for titanicML, this will be removed)
    :param n_estimators:
    :return: mean of 5 cross validation scores
    """
    my_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                  ('classifier', RandomForestRegressor(random_state=20, n_estimators=n_estimators))])
    scores = -1 * cross_val_score(my_pipeline, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')

    return scores.mean()


# scores = {}
# for i in range(1, 10):
#     scores[50*i] = get_score(50*i)
#
# n_estimators_best = min(scores, key=scores.get)
# print(n_estimators_best)

lr_clf.fit(X_train, y_train)
lr_pred = lr_clf.predict(X_test)
print(f'LogisticRegression model score: {lr_clf.score(X_train, y_train):.4f}')
# print(f'LogisticRegression MAE : {mean_absolute_error(y_test["Survived"], lr_pred):.4f}')

dt_clf.fit(X_train, y_train)
dt_pred = dt_clf.predict(X_test)
print(f'DecisionTreeClassifier model score: {dt_clf.score(X_train, y_train):.4f}')
# print(f'LogisticRegression MAE : {mean_absolute_error(y_test["Survived"], dt_pred):.4f}')

rf_clf.fit(X_train, y_train)
rf_pred = rf_clf.predict(X_test)
print(f'RandomForestClassifier model score: {rf_clf.score(X_train, y_train):.4f}')
# print(f'LogisticRegression MAE : {mean_absolute_error(y_test["Survived"], rf_pred):.4f}')

lgb_clf.fit(X_train, y_train)
lgb_pred = lgb_clf.predict(X_test)
print(f'LGBMClassifier model score: {lgb_clf.score(X_train, y_train):.4f}')
# print(f'LogisticRegression MAE : {mean_absolute_error(y_test["Survived"], lgb_pred):.4f}')
