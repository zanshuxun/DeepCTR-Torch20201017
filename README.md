## Experiment

### avazu

1. download and extract the [avazu dataset](https://www.kaggle.com/c/avazu-ctr-prediction/data), then put `train.csv` into the corresponding directory

2. select data in the first 3 days

`python 0_avazu_data_proc.py`

3. run the models

`python 5avazu_test_l2_0.py`

`python 6avazu_test_l2_1e-4.py`

### criteo

1. download criteo dataset: https://figshare.com/articles/dataset/Kaggle_Display_Advertising_Challenge_dataset/5732310

2. unzip

   `tar -zxvf dac.tar.gz`

3. extract first 12m lines and put `criteo_12m.txt` into the corresponding directory

   `head -n 12000000 train.txt > criteo_12m.txt`

4. run the model

   `python deepfm_criteo.py`

   `python afn_criteo.py`

   

   