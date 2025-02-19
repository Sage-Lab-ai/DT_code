# Digital Twins of Ex Vivo Lungs 

## Purpose
In addition to the source code files (/Code/src), we have prepared a demonstration of the digital twin (DT) approach. Below are the instructions for running the demo and, specifically, how to generate a digital twin (forecasted data) of a human lung using baseline ex vivo data.

## System requirements
To run inference files, please make sure to have following libraries installed: Pandas – 2.2.2; NumPy – 1.26.3; PyTorch – 2.3.1; XGBoost – 2.10; Scikit-learn – 1.5.1; SHAP – 0.46.0; SciPy – 1.13.0; wandb – 0.17.3 in Python (version 3.11.8)
Inference files located in /DT Code/Code/ can be executed on a laptop. However, using an embedded GPU for running these files can significantly improve performance, enabling near real-time inference. 

## Files
The DT Code file contains one document and four folders. Below is a description of the DT Code file structure to guide you through the demo process:
  1)	Demo instruction: this document describes how to run the digital twin demo with step-by-step instructions. This is the current document. 
  2)	Data: contains a cohort of n=50 EVLP cases and the associated lung functional parameter data, separated by the different data modalities [Note: there is nothing that requires manual edits or changes in this folder]. All existing data paths have been implemented in the inference code files under /DT Code/Code/ folder and are ready to use. 
  3)	Model: All digital twin models required during demo inference phase. 
  4)	Code: 
    a.	src: Source code files on data preprocessing and model training for all models presented in this study. There is nothing that needs to be manually changed in this folder. 
    b.	XGB_inference.py
    c.	XGB_PC_dynamic.py
    d.	XGB_PC_static.py
    e.	XGB_inference_step2.py
    f.	GRU_inference.py
  5)	Output: The demo results will be saved here after the completion of model inference

## Steps
  1.	Open DT Code in PyCharm or other development environments that can read python files.
  2.	Run inference files according to the order presented below:
    a.	XGB_inference.py
    b.	XGB_PC_dynamic.py
    c.	XGB_PC_static.py
    d.	XGB_inference_step2.py
    e.	GRU_inference.py
3.	Check all the output files in the /DT Code/Output/ folder to see the full demo results:
<ins>Folders named Hourly, Protein, and Transcriptomics:<ins>
After running the XGB_inference_step2.py file, under path /DT Code/Output/, you will see a folder named Hourly or Protein or Transcriptomics that stores the observed and predicted parameter values for the hourly parameters. For each folder in the path /DT Code/Output/Hourly or /DT Code/Output/Protein or /DT Code/Output/Transcriptomics, we standardized the file naming conventions across various folders for ease of navigation:
-	true_Y.csv: the observed parameter values for hourly parameters according to Simulated Lung Profile ID
-	predicted_Y_XGBoost.csv: the predicted parameter values for hourly parameters according to Simulated Lung Profile ID 
[Note: this file can be compared to see how the model performs when compared with the true_Y.csv file] 
-	performance_XGBoost.csv: summary metrics of MAEs and MAPEs for each parameter
-	test_X.csv: input parameter values during inference
Folder named ImagePC:
After running XGB_PC_dynamic.py and XGB_PC_static.py files, under path /DT Code/Output/, you will see a folder named ImagePC that stores all the observed and predicted image principal component (PC) values. Under this folder, you will see the forecasted PC values for both static and dynamic digital twin models.
Folder named High-resolution time series:
After running GRU_inference.py file, under path /DT Code/Output/, you will see a folder named High-resolution time series that stores all the observed and predicted high-resolution breath parameter values. Under this folder, you will see you will see the forecasted PC values for both static and dynamic digital twin models:
-	Demo results on the static digital twin approach can be found in folders: 
o	A1F50_A2F50
o	A1F50_A3F50
o	A1F50PA2F50_A3F50
-	Demo results on the dynamic digital twin approach can be found in folder:
o	A1F50A2F50_A3F50
![image](https://github.com/user-attachments/assets/6bee1bea-75f5-43ea-a005-faacabcc6bd4)





