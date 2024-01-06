import torch

# Load the checkpoint
checkpoint_path = 'model/model.pth'
checkpoint = torch.load(checkpoint_path)

# Print the keys in the loaded dictionary
print(checkpoint.keys())