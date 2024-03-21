import pandas as pd
import numpy as np
from einops import rearrange
import torch
from bartlett import Bartlett
import random
import matplotlib.image as plm
import os
from tqdm import tqdm

# Set the random seed
np.random.seed(0)
random.seed(0)

gateways_scenes_dict = {
    "BlockP_leftbehind": {"gateway1": [0,0,0], "gateway2": [-4.100,6.536,0], "gateway3": [0,6.536,0]}, 
    "BlockP_leftbehind_setting2": {"gateway1": [0,0,0], "gateway2": [0.864,7.252,0], "gateway3": [0,6.536,0]}, 
    "BlockP_right": {"gateway1": [0,0,0], "gateway2": [14.833,0,0], "gateway3": [14.833,-9.686,0]}, 
    "BlockP_rightfront": {"gateway1": [0,0,0], "gateway2": [10.208,0,0], "gateway3": [11.859,-2.601,-0.263]}, 
    "BlockQ_behind": {"gateway1": [0,0,0], "gateway2": [0,-4.753,0], "gateway3": [8.398,1.820,0.290]}, 
    "BlockQ_behind_setting2": {"gateway1": [0,0,0], "gateway2": [0,-8.184,0.290], "gateway3": [10.818,1.820,0.290]}, 
    "BlockQ_left": {"gateway1": [0,0,0], "gateway2": [7.120,-6.207,0.705], "gateway3": [7.120,5.309,0.705]},         
    "BlockR": {"gateway1": [0,0,0], "gateway2": [10.463,12.157,0.845], "gateway3": [10.763,0,0]}, 
    "BlockR_setting2": {"gateway1": [0,0,0], "gateway2": [12.125,-11.163,0.845], "gateway3": [10.763,0,0]}, 
    "PQ504": {"gateway1": [0,0,0], "gateway2": [11.496,-1.435,0], "gateway3": [8.011,-8.408,0]}, 
    "PQ504_corridor": {"gateway1": [0,0,0], "gateway2": [11.496,-1.435,0], "gateway3": [8.011,-8.408,0]}, 
    "PQ504_meetingroom": {"gateway1": [0,0,0], "gateway2": [11.496,-1.435,0], "gateway3": [8.011,-8.408,0]}, 
    "PQ505": {"gateway1": [0,0,0], "gateway2": [-1.765,-2.012,0], "gateway3": [2.596,-2.012,0]}, 
    "PQ512": {"gateway1": [0,0,0], "gateway2": [0.861,-0.495,0], "gateway3": [-0.847,-0.495,0]}, 
    "btw Q & T": {"gateway1": [0,0,0], "gateway2": [-14.020,14.048,0], "gateway3": [-4.077,-12.250,0.205]}
    }


def get_seq_index(num_seq, seq_len=10, max_step=3):
    """
    return
    ----------
    seqs: [num_seq, 10]
    """
    ind = [i for i in range(num_seq*seq_len)]
    seqs = []

    for i in range(num_seq):
        seq = [ind.pop(0)]
        old_pointer = 0
        for j in range(seq_len-1):
            step = random.randint(0,max_step-1)
            new_pointer = old_pointer + step
            if new_pointer > len(ind)-1:
                new_pointer = 0
                old_pointer = 0
            if ind[new_pointer] - seq[-1] <= max_step or new_pointer == old_pointer:
                seq.append(ind.pop(new_pointer))
            elif new_pointer > old_pointer:
                while new_pointer > old_pointer:
                    new_pointer = new_pointer - 1
                    if ind[new_pointer] - seq[-1] <= max_step:
                        seq.append(ind.pop(new_pointer))
                        break
                    elif new_pointer == old_pointer:
                        seq.append(ind.pop(new_pointer))
                        break
            old_pointer = new_pointer
            seq.sort()
        seqs.append(seq)

    return np.array(seqs)


if __name__ == "__main__":

    seq_len = 1
    scenes = list(gateways_scenes_dict.keys())
    
    for scene in scenes:

        blt = Bartlett()
        data_path = f"./csv_data/{scene}.csv"
        df = pd.read_csv(data_path)

        data = df.values
        N, dim = data.shape
        data = data[:N//seq_len*seq_len]
        n_seq = N//seq_len
        ind = get_seq_index(n_seq, seq_len)  # [n_seq, seq_len]
        data_seq = data[ind]    # [n_seq, seq_len, dim]

        np.random.shuffle(data_seq)
        data_seq = torch.from_numpy(data_seq)

        data_len, b, n = data_seq.shape

        # [timestamp_1 + scenario_1 + pos_3 + spt_324]
        data_all = torch.zeros((data_len, b, 1+1+3+9*36))
        data_all[...,0] = data_seq[...,0]
        data_all[...,1] = scenes.index(scene)

        for i in tqdm(range(0, len(data_seq))):
            batch_data = data_seq[i]  # (seq_len, 3+16)
            batch_freq = batch_data[:,1]
            heatmap = blt.get_aoa_heatmap(batch_data[:,3:3+16], batch_freq).detach().cpu().unsqueeze(1)  # [B, 1, 9, 36]
            # figure = np.zeros((9,36,3))
            # figure[:,:,0] = heatmap1[0,0].numpy()
            # plm.imsave(f"test{i}.png", figure)
            heatmap = rearrange(heatmap, 'b c h w -> b (c h w)')  # [seq_len, 4*9*36]
            data_all[i,:,2:5] = torch.tensor(gateways_scenes_dict[scene][f"gateway{int(batch_data[:,2].numpy())}"])
            data_all[i,:,5:] = heatmap

        train_len = int(len(data_all) * 0.8)
        train_data = data_all[0:train_len]
        test_data = data_all[train_len:]

        print("len train_data", len(train_data))
        print("len test_data", len(test_data))

        train_path = "./train_data"
        test_path = "./test_data"
        if not os.path.exists(train_path):
            os.makedirs(train_path)
        if not os.path.exists(test_path):
            os.makedirs(test_path)

        torch.save(train_data, f"{train_path}/train_{scene}.t")
        torch.save(test_data, f"{test_path}/test_{scene}.t")
        print(f"Save {scene} data successfully")
