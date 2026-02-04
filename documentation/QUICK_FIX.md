# ✅ Quick Fix: Jupyter Notebook ModuleNotFoundError

## The Problem
You got: `ModuleNotFoundError: No module named 'posydon'`

## The Solution

### Step 1: Make Sure You're Using the Right Kernel

In your Jupyter notebook (`CE_research_project.ipynb`):

1. Look at the **top-right corner** of the notebook
2. You should see **"Python (posydon)"**
3. If you see "Python 3" or something else:
   - Click **Kernel** → **Change kernel** → **Python (posydon)**
   - Or click the kernel name and select **Python (posydon)**

### Step 2: Restart the Kernel

After changing the kernel:
- Click **Kernel** → **Restart Kernel**

### Step 3: Run the First Cell

The first cell (newly added) sets up environment variables:

```python
# ⚙️ Setup POSYDON Environment Paths
import os
from pathlib import Path

# Set POSYDON paths (required before importing POSYDON)
project_dir = Path.cwd()
os.environ['PATH_TO_POSYDON'] = str(project_dir / "POSYDON")
os.environ['PATH_TO_POSYDON_DATA'] = str(project_dir / "grids" / "POSYDON_data")

print("="*60)
print("POSYDON ENVIRONMENT SETUP")
print("="*60)
print(f"✓ Project directory: {project_dir}")
print(f"✓ PATH_TO_POSYDON: {os.environ['PATH_TO_POSYDON']}")
print(f"✓ PATH_TO_POSYDON_DATA: {os.environ['PATH_TO_POSYDON_DATA']}")
print("="*60)
```

### Step 4: Now Try Importing POSYDON

Run the second cell (imports):

```python
import posydon
from posydon.binary_evol.simulationproperties import SimulationProperties
from posydon.binary_evol.binarystar import BinaryStar
...
```

**It should work now!** ✅

---

## Still Not Working?

### Verify the kernel is installed:

```bash
jupyter kernelspec list
```

You should see:
```
posydon    /Users/josephrodriguez/Library/Jupyter/kernels/posydon
```

### If not listed, reinstall it:

```bash
conda activate posydon
python -m ipykernel install --user --name posydon --display-name "Python (posydon)"
```

### Restart Jupyter completely:

1. Stop Jupyter (Ctrl+C in terminal or File → Quit)
2. Restart it:
   ```bash
   conda activate posydon
   jupyter notebook
   ```

---

## Visual Check

**Look for this in the top-right of your notebook:**

✅ **Correct**: `Python (posydon)` 

❌ **Wrong**: `Python 3` or `Python 3.13` or anything else

---

## Alternative: Start Jupyter from Posydon Environment

Instead of changing kernels, you can start Jupyter from within the posydon environment:

```bash
conda activate posydon
cd /Users/josephrodriguez/CEphysics/CEphysics
jupyter notebook CE_research_project.ipynb
```

This automatically uses the posydon kernel!

---

## Need More Help?

See `JUPYTER_KERNEL_SETUP.md` for detailed troubleshooting.
