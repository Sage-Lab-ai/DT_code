
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import os
from sklearn.model_selection import GridSearchCV
import json
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import datetime
from sklearn.model_selection import KFold
import shap
import pickle

save_model_dir = '../../../Model/XGB_PC/models_pred'
tab_data_df = pd.read_csv('df_pred2h.csv', index_col='Evlp Id No')
real_df = pd.read_csv('df_real1h2h.csv', index_col='Evlp Id No')
real_df = real_df[[col for col in real_df.columns if col.startswith('70_')]]

tab_data_df = pd.merge(tab_data_df, real_df, on='Evlp Id No')


# read Image PC data
image_pc1h_path_torex = 'torex_pca-1h-features.csv'
image_pc3h_path_torex = 'torex_pca-3h-features.csv'
image_pc1h_torex = pd.read_csv(image_pc1h_path_torex, index_col='Evlp Id No')
image_pc3h_torex = pd.read_csv(image_pc3h_path_torex, index_col='Evlp Id No')

image_pc1h_path = 'pca-1h-features.csv'
image_pc3h_path = 'pca-3h-features.csv'
image_pc1h = pd.read_csv(image_pc1h_path, index_col='Evlp Id No')
image_pc3h = pd.read_csv(image_pc3h_path, index_col='Evlp Id No')

image_pc1h = pd.concat([image_pc1h, image_pc1h_torex])
image_pc3h = pd.concat([image_pc3h, image_pc3h_torex])
image_pc1h.columns = ['1h_' + col_name for col_name in image_pc1h.columns if col_name != 'Evlp Id No']
image_pc3h.columns = ['3h_' + col_name for col_name in image_pc3h.columns if col_name != 'Evlp Id No']

# merge three dataframes on 'Evlp Id No', keep only rows that are present in both dataframes
merged_df = pd.merge(tab_data_df, image_pc1h, on='Evlp Id No')
merged_df = pd.merge(merged_df, image_pc3h, on='Evlp Id No')

# log trans
columns_to_transform = [col for col in merged_df.columns if 'STEEN' in col or 'PVR' in col]
merged_df[columns_to_transform] = merged_df[columns_to_transform].apply(np.log1p)

merged_df = merged_df.dropna()


date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_dir = '../../../Model/XGB_PC/results_pred_hyper'
os.makedirs(save_dir, exist_ok=True)
merged_df = merged_df.sample(frac=1.0, random_state=42)
y = merged_df[[col_name for col_name in merged_df.columns if '3h_' in col_name]]
X= merged_df[[col_name for col_name in merged_df.columns if col_name not in y.columns]]
X= X[[col_name for col_name in X.columns if not 'STEEN' in col_name]]
results = []
n_jobs = 10

to_tune = [{
    'model__objective': ["reg:squarederror", "reg:absoluteerror"],
    'model__n_estimators': [10,30],
    'model__learning_rate': [0.1],
    'model__gamma': [0, 0.2,0.4, 0.8],
    'model__max_depth': [2,3,4, 5],
    'model__min_child_weight': [5, 10],
    'model__alpha': [5, 10], 
    'model__lambda': [5, 10] 
}]

select_keys = list(to_tune[0].keys())

scores = ['neg_mean_absolute_error' , 'neg_mean_squared_error']

categorical_list = ['Donor Sex', 'Donor Type']
numeric_list = [x for x in X.columns if x not in categorical_list]



for col_name in y.columns: 
    np.random.seed(42) 
    y_col = y[col_name]    
    pipeline = XGBRegressor(n_jobs=n_jobs) 

    pipeline.fit(X, y_col)
    explainer = shap.Explainer(pipeline, X)
    shap_values = explainer(X)
    mean_shap_values = np.abs(shap_values.values).mean(axis=0)

    if col_name == '3h_feature_pca_0':
        N = 5
    else:
        N = 5

    top_indices = np.argsort(mean_shap_values)[-N:]
    top_features = X.columns[top_indices]
    pca = col_name.replace('3h_feature_', '')
    with open(os.path.join(save_dir, f'top_features_{pca}.txt'), 'w') as f:
        for feature in top_features:
            f.write(f"{feature}\n")
    Xfeat = X[top_features]
    Xfeat = X[top_features]

    pipeline = Pipeline([
        ('scaler', StandardScaler()),  # Normalization
        ('model', XGBRegressor(n_jobs=n_jobs))  # XGBRegressor model
    ])

    grid_search_model = GridSearchCV(pipeline, param_grid=to_tune, 
                                     scoring='neg_mean_squared_error', return_train_score=True,
                                     cv=KFold(n_splits=10))
    grid_search_model.fit(Xfeat, y_col)
    best_pipeline = grid_search_model.best_estimator_
    with open(os.path.join(save_model_dir, f'{col_name}_model.pkl'), 'wb') as file:
        pickle.dump(best_pipeline, file)
    
    results_grid = grid_search_model.cv_results_

    best_params = grid_search_model.best_params_
    best_index = None
    for i, params in enumerate(results_grid['params']):
        if params == best_params:
            best_index = i
            break
    for cv, (tr_indices, ts_indices) in enumerate(grid_search_model.cv.split(X)):
        tr_x, ts_x = Xfeat.iloc[tr_indices], Xfeat.iloc[ts_indices]
        tr_y, ts_y = y.iloc[tr_indices], y.iloc[ts_indices]
        val_loss = -results_grid[f'split{cv}_test_score'][best_index]
        tr_loss = -results_grid[f'split{cv}_train_score'][best_index]
        baseline_ts_x = X.iloc[ts_indices]
        baseline_mse = mean_squared_error(baseline_ts_x[col_name.replace('3h', '1h')], ts_y[col_name])

    y_pred = grid_search_model.predict(Xfeat)
    y_col_test = y[col_name]
    mse = mean_squared_error(y_col_test, y_pred)
    mae = mean_absolute_error(y_col_test, y_pred)
    mpe = np.mean(np.abs((y_col_test - y_pred) / y_col_test)) * 100
    best_estimator_params = grid_search_model.best_estimator_.get_params()
    best_estimator_params = {key: best_estimator_params[key] for key in select_keys if key in best_estimator_params}
    params = {'column_name': col_name, 'mse': mse, 'mae': mae, 'mpe': mpe}
    params.update(best_estimator_params)
    results.append(params)

results_df = pd.DataFrame(results)
results_df.to_csv(save_dir + '/results04.csv', index=False)

