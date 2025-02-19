# Digital Twins of Ex Vivo Lungs 

## Purpose
In addition to the source code files (/Code/src), we have prepared a demonstration of the digital twin (DT) approach. Below are the instructions for running the demo and, specifically, how to generate a digital twin (forecasted data) of a human lung using baseline ex vivo data.

## System requirements
To run inference files, please make sure to have the following libraries installed: Pandas – 2.2.2; NumPy – 1.26.3; PyTorch – 2.3.1; XGBoost – 2.10; Scikit-learn – 1.5.1; SHAP – 0.46.0; SciPy – 1.13.0; wandb – 0.17.3 in Python (version 3.11.8)<br />
Inference files located in /DT Code/Code/ can be executed on a laptop. However, using an embedded GPU for running these files can significantly improve performance, enabling near real-time inference. 

## Files
The DT Code file contains one document and four folders. Below is a description of the DT Code file structure to guide you through the demo process:<br />
  1)	Data: contains a cohort of n=50 EVLP cases and the associated lung functional parameter data, separated by the different data modalities [Note: there is nothing that requires manual edits or changes in this folder]. <br />
  All existing data paths have been implemented in the inference code files under /DT Code/Code/ folder and are ready to use. <br />
  3)	Model: All digital twin models required during demo inference phase. <br />
  4)	Code: <br />
    a.	src: Source code files on data preprocessing and model training for all models presented in this study. There is nothing that needs to be manually changed in this folder. <br />
    b.	XGB_inference.py<br />
    c.	XGB_PC_dynamic.py<br />
    d.	XGB_PC_static.py<br />
    e.	XGB_inference_step2.py<br />
    f.	GRU_inference.py<br />
  5)	Output: The demo results will be saved here after the completion of model inference

## Steps
  1.	Open DT Code in PyCharm or other development environments that can read python files.
  2.	Run inference files according to the order presented below:<br />
    a.	XGB_inference.py<br />
    b.	XGB_PC_dynamic.py<br />
    c.	XGB_PC_static.py<br />
    d.	XGB_inference_step2.py<br />
    e.	GRU_inference.py<br />
4.	Check all the output files in the /DT Code/Output/ folder to see the full demo results:<br />

<ins> Folders named Hourly, Protein, and Transcriptomics:</ins> <br />
After running the XGB_inference_step2.py file, under path /DT Code/Output/, you will see a folder named Hourly or Protein or Transcriptomics that stores the observed and predicted parameter values for the hourly parameters. For each folder in the path /DT Code/Output/Hourly or /DT Code/Output/Protein or /DT Code/Output/Transcriptomics, we standardized the file naming conventions across various folders for ease of navigation:
- true_Y.csv: the observed parameter values for hourly parameters according to Simulated Lung Profile ID<br />
-	predicted_Y_XGBoost.csv: the predicted parameter values for hourly parameters according to Simulated Lung Profile ID <br />
[Note: this file can be compared to see how the model performs when compared with the true_Y.csv file] <br />
-	performance_XGBoost.csv: summary metrics of MAEs and MAPEs for each parameter<br />
-	test_X.csv: input parameter values during inference<br />

<ins>Folder named ImagePC:</ins><br />
After running XGB_PC_dynamic.py and XGB_PC_static.py files, under path /DT Code/Output/, you will see a folder named ImagePC that stores all the observed and predicted image principal component (PC) values. Under this folder, you will see the forecasted PC values for both static and dynamic digital twin models.
  
<ins>Folder named High-resolution time series:</ins><br />
After running GRU_inference.py file, under path /DT Code/Output/, you will see a folder named High-resolution time series that stores all the observed and predicted high-resolution breath parameter values. Under this folder, you will see you will see the forecasted PC values for both static and dynamic digital twin models:
  -	Demo results on the static digital twin approach can be found in folders: <br />
    o	A1F50_A2F50<br />
    o	A1F50_A3F50<br />
    o	A1F50PA2F50_A3F50<br />
  -	Demo results on the dynamic digital twin approach can be found in folder:<br />
    o	A1F50A2F50_A3F50<br />





