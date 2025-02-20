import torch
import numpy as np
import os
import pandas as pd
from src.GRU.util.baselines import average_of_tail
from src.GRU.EVLPMultivariateBreathDataset import EVLPMultivariateBreathDataset
from torch.utils.data import DataLoader
from src.GRU.forecasting_pipeline import param_idx
from src.GRU.GRU import GRU

# Read in the synthetic data 
simulated_data = pd.read_csv(os.path.join("../Data", "ts_data_simulated.csv"))

setups = ["A1F50_A2F50", "A1F50A2F50_A3F50", "A1F50PA2F50_A3F50", "A1F50_A3F50"]
parameters = ["Dy_comp", "P_peak", "P_mean", "Ex_vol"]
parameter_column_names = ["Dy_comp(mL/cmH2O)", "P_peak(cmH2O)", "P_mean(cmH2O)", "Ex_vol(mL)"]

# Create 3d array (cases , timesteps = 50, features = 4) from the synthetic data for each of A1F50, A2F50, A3F50
donor_ids = simulated_data["Simulated Donor Id"].unique()
arrays = []
for setup in ["A1F50", "A2F50", "A3F50"]:
    all_case_data = []
    for id in donor_ids:
        case_data = []
        for param in parameter_column_names:
            case_param_data = simulated_data[(simulated_data["Simulated Donor Id"] == id) & (simulated_data["Simulated Parameter"] == f"{setup}_{param.replace('/', '_')}")]
            # Get all columns of case_param_data from "Breath_1" to "Breath_50"
            breath_cols = ["Breath_" + str(i) for i in range(1, 51)]
            case_param_data = case_param_data[breath_cols].values.flatten()
            case_data.append(case_param_data)

        case_data = np.array(case_data).transpose()
        all_case_data.append(case_data)
    
    all_case_data = np.array(all_case_data)
    arrays.append(all_case_data)

# Do inference for each setup and parameter combination
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
static = None


for setup in setups:
    for param in parameters: 
        datasets = {
            "A1F50_A2F50": EVLPMultivariateBreathDataset(donor_ids, arrays[0], arrays[1][:, :, param_idx[param]: param_idx[param] +1], static),
            "A1F50_A3F50": EVLPMultivariateBreathDataset(donor_ids, arrays[0], arrays[2][:, :, param_idx[param]: param_idx[param] +1], static),
            "A1F50A2F50_A3F50": EVLPMultivariateBreathDataset(donor_ids, np.concatenate([arrays[0], arrays[1]], axis=1), arrays[2][:, :, param_idx[param]: param_idx[param] +1], static)
        }

        # Load the saved model 
        model_setup_to_use = setup
        if setup == "A1F50PA2F50_A3F50":
            model_setup_to_use = "A1F50A2F50_A3F50"
            datasets["A1F50PA2F50_A3F50"] = EVLPMultivariateBreathDataset(donor_ids, np.concatenate([arrays[0], arrays[3]], axis=1), arrays[2][:, :, param_idx[param]: param_idx[param] +1], static)

        Model_Folder = os.path.join("../Model", "GRU", model_setup_to_use, param, "seed_42_multivariate")
        torch.serialization.add_safe_globals([GRU])
        model = torch.load(os.path.join(Model_Folder, f"locked_model.pt"), map_location=device, weights_only=False)
        model.eval()

        avg_of_X = average_of_tail(datasets[setup].X)[:, :, param_idx[param]: param_idx[param] +1]
        true_Y = datasets[setup].Y

        test_loader = DataLoader(datasets[setup], batch_size=1, shuffle=False)
        y_preds = []
        with torch.no_grad():
            for (x, s), _ in test_loader:
                x = x.to(device, non_blocking=True)
                s = s.to(device, non_blocking=True)
                y_pred = model(x, s)
                y_preds.append(y_pred.detach().cpu().numpy())

        y_preds = np.concatenate(y_preds)
        y_preds = y_preds + avg_of_X

        results = pd.DataFrame()
        results["case_id"] = np.repeat(donor_ids, 50)
        results["true_y"] = true_Y.flatten()
        results["pred_y"] = y_preds.flatten()

        if not os.path.exists(os.path.join("../Output", "High-resolution time series", setup)):
            os.makedirs(os.path.join("../Output", "High-resolution time series", setup))

        results.to_csv(os.path.join("../Output", "High-resolution time series", setup, f"{param}_true_pred.csv"), index=False)

        # Save A2 predictions to be used for A1F50PA2F50_A3F50 setup
        if setup == "A1F50_A2F50":
            np.save(os.path.join("../Output", "High-resolution time series", setup, f"{param}_y_pred.npy"), y_preds)
            if param == parameters[-1]: 
                # Add "PA2F50" to arrays
                PA2F50_y_pred = []
                for p in parameters:
                    y_pred = np.load(os.path.join("../Output", "High-resolution time series", "A1F50_A2F50", f"{p}_y_pred.npy"))
                    PA2F50_y_pred.append(y_pred)
                PA2F50_y_pred = np.concatenate(PA2F50_y_pred, axis=2)
                arrays.append(PA2F50_y_pred)
