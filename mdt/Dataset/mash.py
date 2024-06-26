import os
import numpy as np
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader

from mdt.Config.shapenet import CATEGORY_IDS
from mdt.Method.dataset import center_crop_arr, random_crop_arr


class MashDataset(Dataset):
    def __init__(
        self,
        resolution,
        random_crop=False,
    ):
        super().__init__()
        self.resolution = resolution
        self.random_crop = random_crop

        self.dataset_root_folder_path = "/home/chli/Dataset/"
        self.split = "train"

        self.mash_folder_path = self.dataset_root_folder_path + "Mash/"
        self.split_folder_path = self.dataset_root_folder_path + "Split/"

        assert os.path.exists(self.mash_folder_path)
        assert os.path.exists(self.split_folder_path)

        self.paths_list = []

        dataset_name_list = os.listdir(self.split_folder_path + "mash/")

        for dataset_name in dataset_name_list:
            mash_split_folder_path = (
                self.split_folder_path + "mash/" + dataset_name + "/"
            )

            categories = os.listdir(mash_split_folder_path)

            for i, category in enumerate(categories):
                rel_file_path_list_file_path = (
                    mash_split_folder_path + category + "/" + self.split + ".txt"
                )
                if not os.path.exists(rel_file_path_list_file_path):
                    continue

                with open(rel_file_path_list_file_path, "r") as f:
                    rel_file_path_list = f.read().split()

                print("[INFO][MashDataset::__init__]")
                print(
                    "\t start load dataset: "
                    + dataset_name
                    + "["
                    + category
                    + "], "
                    + str(i + 1)
                    + "/"
                    + str(len(categories))
                    + "..."
                )
                for rel_file_path in tqdm(rel_file_path_list):
                    mash_file_path = (
                        self.mash_folder_path
                        + dataset_name
                        + "/mash/"
                        + category
                        + "/"
                        + rel_file_path
                    )

                    self.paths_list.append([mash_file_path, CATEGORY_IDS[category]])

        return

    def __len__(self):
        return len(self.paths_list)

    def __getitem__(self, idx):
        mash_file_path, category_id = self.paths_list[idx]

        mash_params = np.load(mash_file_path, allow_pickle=True).item()

        mask_params = mash_params["mask_params"]
        sh_params = mash_params["sh_params"]
        rotate_vectors = mash_params["rotate_vectors"]
        positions = mash_params["positions"]

        mash_params = np.hstack([mask_params, sh_params, rotate_vectors, positions])
        mash_params = mash_params[np.random.permutation(mash_params.shape[0])]

        if self.random_crop:
            arr = random_crop_arr(mash_params, self.resolution)
        else:
            arr = center_crop_arr(mash_params, self.resolution)

        out_dict = {}
        out_dict["y"] = np.array(category_id, dtype=np.int64)
        return np.transpose(arr, [2, 0, 1]), out_dict


loader = DataLoader(
    MashDataset(),
    batch_size=batch_size,
    shuffle=False,
    num_workers=1,
    drop_last=True,
)
