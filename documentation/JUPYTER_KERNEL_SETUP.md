# Jupyter Kernel Setup for POSYDON

## ✅ Kernel Installed!

The **Python (posydon)** kernel has been registered and is now available in Jupyter notebooks.

## How to Use the Correct Kernel

### In Jupyter Notebook:

1. **Open your notebook**: `CE_research_project.ipynb`

2. **Change the kernel**:
   - Click on **Kernel** → **Change kernel** → **Python (posydon)**
   - Or click the kernel name in the top-right corner and select **Python (posydon)**

3. **Verify it's working**:
   Run the first cell - it should now import `posydon` successfully!

### Important: Add Environment Setup Cell

Add this as the **FIRST cell** in your notebook (before any imports):

```python
# Setup POSYDON environment paths
import os
from pathlib import Path

# Set POSYDON paths
project_dir = Path.cwd()
os.environ['PATH_TO_POSYDON'] = str(project_dir / "POSYDON")
os.environ['PATH_TO_POSYDON_DATA'] = str(project_dir / "grids" / "POSYDON_data")

print(f"✓ POSYDON paths configured")
print(f"  PATH_TO_POSYDON: {os.environ['PATH_TO_POSYDON']}")
print(f"  PATH_TO_POSYDON_DATA: {os.environ['PATH_TO_POSYDON_DATA']}")
```

## Troubleshooting

### If you still see "No module named 'posydon'":

1. **Check your kernel**: Look at the top-right corner of the notebook. It should say **Python (posydon)**, not "Python 3" or anything else.

2. **Restart the kernel**: Click **Kernel** → **Restart Kernel**

3. **Verify from command line**:
   ```bash
   # List available kernels
   jupyter kernelspec list
   
   # You should see "posydon" in the list
   ```

### If the kernel doesn't appear:

Run this command again:
```bash
conda activate posydon
python -m ipykernel install --user --name posydon --display-name "Python (posydon)"
```

Then restart Jupyter.

## Starting Jupyter with the Right Environment

You can also start Jupyter from within the posydon environment:

```bash
conda activate posydon
jupyter notebook
```

This ensures the correct Python environment is used by default.

## Quick Test

Once you've selected the **Python (posydon)** kernel, run this in a cell:

```python
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Should show the posydon environment path
# Expected: /opt/anaconda3/envs/posydon/bin/python
```

If the path shows `/opt/anaconda3/envs/posydon`, you're using the correct kernel! ✅
