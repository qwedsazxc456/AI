# based on https://github.com/dawenl/vae_cf

import numpy as np
from scipy import sparse
import pandas as pd
import os
import bottleneck as bn




def load_train_data(csv_file, n_items, n_users, global_indexing=False):
    tp = pd.read_csv(csv_file)
    
    n_users = n_users if global_indexing else tp['uid'].max() + 1

    rows, cols = tp['uid'], tp['sid']
    data = sparse.csr_matrix((np.ones_like(rows),
                             (rows, cols)), dtype='float64',
                             shape=(n_users, n_items))
    return data


def load_tr_te_data(csv_file_tr, csv_file_te, n_items, n_users, global_indexing=False):
    tp_tr = pd.read_csv(csv_file_tr)
    tp_te = pd.read_csv(csv_file_te)

    if global_indexing:
        start_idx = 0
        end_idx = len(unique_uid) - 1
    else:
        start_idx = min(tp_tr['uid'].min(), tp_te['uid'].min())
        end_idx = max(tp_tr['uid'].max(), tp_te['uid'].max())

    rows_tr, cols_tr = tp_tr['uid'] - start_idx, tp_tr['sid']
    rows_te, cols_te = tp_te['uid'] - start_idx, tp_te['sid']

    data_tr = sparse.csr_matrix((np.ones_like(rows_tr),
                             (rows_tr, cols_tr)), dtype='float64', shape=(end_idx - start_idx + 1, n_items))
    data_te = sparse.csr_matrix((np.ones_like(rows_te),
                             (rows_te, cols_te)), dtype='float64', shape=(end_idx - start_idx + 1, n_items))
    return data_tr, data_te


def get_data(dataset, global_indexing=False):
    unique_sid = list()
    with open(os.path.join(dataset, 'unique_sid.txt'), 'r') as f:
        for line in f:
            unique_sid.append(line.strip())
    
    unique_uid = list()
    with open(os.path.join(dataset, 'unique_uid.txt'), 'r') as f:
        for line in f:
            unique_uid.append(line.strip())
            
    n_items = len(unique_sid)
    n_users = len(unique_uid)
    
    train_data = load_train_data(os.path.join(dataset, 'train.csv'), n_items, n_users, global_indexing=global_indexing)

    # test_data_tr, test_data_te = load_tr_te_data(os.path.join(dataset, 'test_tr.csv'),
    #                                              os.path.join(dataset, 'test_te.csv'),
    #                                              n_items, n_users, 
    #                                              global_indexing=global_indexing)
    
    data = train_data, # test_data_tr, test_data_te
    data = (x.astype('float32') for x in data)
    
    return data



def recall(X_pred, heldout_batch, k=10):
    batch_users = X_pred.shape[0]

    idx = bn.argpartition(-X_pred, k, axis=1)
    X_pred_binary = np.zeros_like(X_pred, dtype=bool)
    X_pred_binary[np.arange(batch_users)[:, np.newaxis], idx[:, :k]] = True

    X_true_binary = (heldout_batch > 0).toarray()
    tmp = (np.logical_and(X_true_binary, X_pred_binary).sum(axis=1)).astype(
        np.float32)
    recall = tmp / np.minimum(k, X_true_binary.sum(axis=1))
    return recall

# def result(X_pred,k):
#     items=[]
#     user = pd.read_csv('../unique_uid', header=None)
#     item = pd.read_csv('../unique_sid', header=None)
#     item = item.to_numpy()
#     batch_users = X_pred.shape[0]
#     idx = bn.argpartition(-X_pred, 10, axis=1)
#     X_pred_binary = np.zeros_like(X_pred, dtype=bool)
#     X_pred_binary[np.arange(batch_users)[:, np.newaxis], idx[:, :10]] = True
#     for i in X_pred_binary:
#         items.append(item[i])
#     users = user.repeat(10)
#     users = np.array(users).reshape(-1,1)
#     items = np.array(items).reshape(-1,1)
#     result = np.concatenate(users,items,axis=1)
#     result = pd.DataFrame(result, columns=['user','item'])
#     result.to_csv('result.csv', index=False)
