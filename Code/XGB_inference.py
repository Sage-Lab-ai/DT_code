from src.XGB.inference import *


hourly_model_folder = "../Model/XGB/Hourly"
protein_model_folder = "../Model/XGB/Protein"
transcriptomics_model_folder = "../Model/XGB/Transcriptomics"

hourly_save_folder = "../Output/Hourly"
protein_save_folder = "../Output/Protein"
transcriptomics_save_folder = "../Output/Transcriptomics"

new_hourly_data_path = "../Data/hourly_data_simulated.csv"
new_edema_data_path = "../Data/edema_data_simulated.csv"
new_pc_1h_data_path = "../Data/PC1h_data_simulated.csv"
new_pc_3h_data_path = "../Data/PC3h_data_simulated.csv"
new_protein_data_path = "../Data/protein_data_simulated_withslopes.csv"
new_transcriptomics_x_data_path = "../Data/transcriptomics1_data_simulated.csv"
new_transcriptomics_y_data_path = "../Data/transcriptomics2_data_simulated.csv"

inference_suffix = " inference"

models = ["XGBoost"]

new_hourly_data = pd.read_csv(new_hourly_data_path, index_col=1)
new_hourly_data = new_hourly_data.drop(new_hourly_data.columns[0], axis=1)
new_edema_data = pd.read_csv(new_edema_data_path, index_col=1)
new_edema_data = new_edema_data.drop(new_edema_data.columns[0], axis=1)
hourly_inference_new_cases(
    new_data=pd.concat([new_hourly_data, new_edema_data], axis=1),
    model_folder=hourly_model_folder,
    save_folder=hourly_save_folder,
    suffix=inference_suffix,
    models=models,
)

new_pc_1h_data = pd.read_csv(new_pc_1h_data_path, index_col=1)
new_pc_1h_data = new_pc_1h_data.drop(new_pc_1h_data.columns[0], axis=1)
new_protein_data = pd.read_csv(new_protein_data_path, index_col=1)
new_protein_data = new_protein_data.drop(new_protein_data.columns[0], axis=1)
protein_inference_new_cases_dynamic(
    new_data=pd.concat([new_protein_data, new_hourly_data, new_pc_1h_data], axis=1),
    model_folder=protein_model_folder,
    save_folder=protein_save_folder,
    suffix=inference_suffix,
    models=models,
)

hourly_true_h1 = pd.read_csv(os.path.join(hourly_save_folder, f"H1_to_H2{inference_suffix}/test_X.csv"), index_col=0)
hourly_pred_h2 = pd.read_csv(os.path.join(hourly_save_folder, f"H1_to_H2{inference_suffix}/predicted_Y_XGBoost.csv"), index_col=0)
protein_inference_new_cases_static(
    new_data=pd.concat([new_protein_data, hourly_true_h1, hourly_pred_h2, new_pc_1h_data], axis=1),
    model_folder=protein_model_folder,
    save_folder=protein_save_folder,
    suffix=inference_suffix,
    models=models,
)

new_pc_3h_data = pd.read_csv(new_pc_3h_data_path, index_col=1)
new_pc_3h_data = new_pc_3h_data.drop(new_pc_3h_data.columns[0], axis=1)
new_pc_1h_data.columns = [col + "_x" for col in new_pc_1h_data.columns]
new_pc_3h_data.columns = [col + "_y" for col in new_pc_3h_data.columns]
new_transcriptomics_x_data = pd.read_csv(new_transcriptomics_x_data_path, index_col=1)
new_transcriptomics_x_data = new_transcriptomics_x_data.drop(new_transcriptomics_x_data.columns[0], axis=1)
new_transcriptomics_y_data = pd.read_csv(new_transcriptomics_y_data_path, index_col=1)
new_transcriptomics_y_data = new_transcriptomics_y_data.drop(new_transcriptomics_y_data.columns[0], axis=1)
new_transcriptomics_data = pd.concat([new_transcriptomics_x_data, new_transcriptomics_y_data], axis=1)
transcriptomics_inference_new_cases_dynamic(
    new_data=pd.concat([new_transcriptomics_data, new_hourly_data, new_pc_1h_data, new_pc_3h_data], axis=1),
    model_folder=transcriptomics_model_folder,
    save_folder=transcriptomics_save_folder,
    suffix=inference_suffix,
    models=models,
)