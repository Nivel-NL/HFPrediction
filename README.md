These scripts are used to create machine learning models using general practicioner data as provided by Nivel to identify heart failure a year before diagnosis.
Article is submitted to ...

Using machine learning algorithms for the prediction of heart failure

The full algorithm consists of 4 segments:
1. Data conversion
2. Data preprocessing
3. Dataset creation
4. Training

The first three segments can be called upon from the Main.py file. The last segment is a seperate JupyterLab Notebook

------------------------------------------------------------------------------------------------
1. Data conversion (folder 'Convertdata')

Data is converted from the format provided by the Nivel to a format used for further prepocessing.
Rich commenting is provided in-code.
In this way, a structured format is provided for preprocessing.

------------------------------------------------------------------------------------------------
2. Data preprocessing (folder 'preprocess')

Converted data is used to preprocess it further, i.e. identify cases, select time periods, extract features, create trends, etc.
This is started from the file 'preprocess_pattern'. 
Commenting is provided in-code for large parts.
Output are CSV files with data extracted from cases and controls.

------------------------------------------------------------------------------------------------
3. Dataset creation (folder 'Learning')

Preprocessed data is put in a format that machine learning algorithms can handle.
For instance, binary variables indicating presence of features.
Furthermore, datasets are divided into seperate subsets, such as age and gender or trend data.
Output are pickle files containing the relevant pandas.

------------------------------------------------------------------------------------------------
4. Training (folder 'Training')

A forward feature selection algorithm (up to 100 features) and hyperparameter optimalization is combined in the Training script.
This is performed on all sub-datasets for logistic regression, random forests and XGBoost.
For further details, see the article.

The plotCurves.py provides an algorithm to plot both the ROC curve and the clinical number of diagnoses curve.
These are used for information and in-article.
