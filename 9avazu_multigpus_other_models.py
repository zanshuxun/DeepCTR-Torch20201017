# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import torch
import sys
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

from deepctr_torch.inputs import SparseFeat, DenseFeat, get_feature_names
from deepctr_torch.models import *

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

if __name__ == "__main__":
    epochs=2
    batch_size=512

    # data = pd.read_csv('/HDD_sdb/wyw/zsx/avazu/avazu_first_3d.csv')
    # data = pd.read_csv('/HDD_sdb/wyw/zsx/avazu/avazu_first_3d.csv',nrows=50)

    sparse_features = ['hour', 'C1', 'banner_pos', 'site_id', 'site_domain',
                       'site_category', 'app_id', 'app_domain', 'app_category', 'device_id',
                       'device_model', 'device_type', 'device_conn_type',  # 'device_ip', 
                       'C14',
                       'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', ]
    print('len(sparse_features)',len(sparse_features))  # 去掉id click device_ip   不用day  25-4=21

    # data[sparse_features] = data[sparse_features].fillna('-1', )
    target = ['click']

    try:
        # read data from pkl directly
        data=pd.read_pickle('data_avazu_first_3d.pkl')
        print('read_pickle ok')
    except:    
        print('preprocess data and save it by pickle')
        data = pd.read_csv('avazu_first_3d.csv')
        # data = pd.read_csv('avazu_first_3d.csv',nrows=50)  # for test
        data[sparse_features] = data[sparse_features].fillna('-1', )
        # 1.Label Encoding for sparse features,and do simple Transformation for dense features
        for feat in sparse_features:
            lbe = LabelEncoder()
            data[feat] = lbe.fit_transform(data[feat])

        data.to_pickle('data_avazu_first_3d.pkl')
        print('to_pickle ok')
    
    print(data[:5])
    print(data['day'].unique())

    # 2.count #unique features for each sparse field,and record dense feature field name

    fixlen_feature_columns = [SparseFeat(feat, data[feat].nunique(), embedding_dim=8)
                              for feat in sparse_features]

    dnn_feature_columns = fixlen_feature_columns
    linear_feature_columns = fixlen_feature_columns

    feature_names = get_feature_names(
        linear_feature_columns + dnn_feature_columns)

    # 3.generate input data for model

    # train, test = train_test_split(data, test_size=0.2,random_state=2020)
    train=data[data['day']<23]
    test=data[data['day']==23]
    print('train.shape',train.shape)
    print('test.shape',test.shape)

    train_model_input = {name: train[name] for name in feature_names}
    test_model_input = {name: test[name] for name in feature_names}

    # 4.Define Model,train,predict and evaluate

    device = 'cpu'
    use_cuda = True
    if use_cuda and torch.cuda.is_available():
        print('cuda ready...')
        device = 'cuda:0'

    model = IFM(linear_feature_columns=linear_feature_columns, dnn_feature_columns=dnn_feature_columns,
                   task='binary',#cross_parameterization='matrix',
                   l2_reg_embedding=1e-5, device=device, gpus=[0, 1])

    # model = PNN(dnn_feature_columns=dnn_feature_columns,
    #                task='binary',#cross_parameterization='matrix',
    #                l2_reg_embedding=1e-5, device=device, gpus=[0, 1])

    print('model',model)

    model.compile("adam", "binary_crossentropy",
                  # metrics=["binary_crossentropy", ], )
                  metrics=["binary_crossentropy", "auc"], )

    for epoch in range(epochs):
        print('epoch',epoch)
        model.fit(train_model_input, train[target].values,
                  batch_size=batch_size, epochs=1, verbose=1)

        pred_ans = model.predict(test_model_input, batch_size*20)
        print("test LogLoss", round(log_loss(test[target].values, pred_ans), 4))
        print("test AUC", round(roc_auc_score(test[target].values, pred_ans), 4))
