import torch
from torch.utils.data import Dataset


class DFGData(Dataset):
    def __init__(self, list_IDs, labels):
        'initialization'
        self.labels = labels
        self.list_Ids = list_ids

    def __getidem__(self, index):
        'Return one sample of data'
        ID = self.list_IDs[index]

        x =torch.load('data/'+id+'.pt')
        y = self.labels['ID']

        return X, y

    def __len__(self):
        'Denotes the total number of data samples'
        return len(self.list_ids)


if __name__ == '__main__':
    print("Test for Dataset")
