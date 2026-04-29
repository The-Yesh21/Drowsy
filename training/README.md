# Drowsiness Detector — Stage 1b: XGBoost Training Pipeline

Train an XGBoost classifier on a drowsiness detection dataset using
MediaPipe-extracted facial features, then export to ONNX for real-time inference.

---

## 1. Dataset

### Option A — Kaggle (instant, recommended)

Download any **Drowsy / Non Drowsy** image dataset from Kaggle, for example:
- [Driver Drowsiness Dataset](https://www.kaggle.com/datasets/ismailnasri20/driver-drowsiness-dataset-ddd)
- [Drowsiness Detection Dataset](https://www.kaggle.com/datasets/dheerajperumandla/drowsiness-dataset)

Place the folders inside `data/raw/` so the structure looks like:

```
training/
└── data/
    └── raw/
        ├── Drowsy/
        │   ├── img001.jpg
        │   ├── img002.jpg
        │   └── ...
        └── Non Drowsy/
            ├── img001.jpg
            ├── img002.jpg
            └── ...
```

### Option B — NTHU Dataset (video-based)

Request access at <http://cv.cs.nthu.edu.tw/php/callforpaper/datasets/DDD/>.

```
training/
└── data/
    └── raw/
        ├── 001/
        │   ├── nonsleepyCombination.avi
        │   ├── sleepyCombination.avi
        │   └── ...
        └── ...
```

### Label Mapping

The script auto-detects labels from **folder/file names**:

| Keyword in folder/filename                       | Label    |
|--------------------------------------------------|----------|
| `non drowsy`, `nonsleepy`, `alert`, `awake`      | `alert`  |
| `drowsy`, `sleepy`, `yawn`, `nodding`, `slowblink`| `drowsy` |

---

## 2. Setup

```bash
cd training
pip install -r requirements.txt
```

---

## 3. Run the Pipeline

Execute these scripts **in order**:

### Step 1 — Feature Extraction

```bash
python preprocess.py
```

For **images**: processes each image with MediaPipe FaceMesh (takes ~5-10 min for a few thousand images).
For **videos**: samples every 5th frame and computes temporal features too.

Saves 10 features per frame/image to `outputs/features.csv`.

### Step 2 — Train XGBoost (< 2 min)

```bash
python train.py
```

Applies SMOTE oversampling, trains XGBoost with 5-fold cross-validation, saves model to `outputs/model.json`.

### Step 3 — Evaluate

```bash
python evaluate.py
```

Generates plots in `outputs/plots/`:
- `confusion_matrix.png` — normalised confusion matrix
- `feature_importance.png` — ranked feature importances
- `roc_curves.png` — per-class ROC curves with AUC

### Step 4 — Export to ONNX

```bash
python export_onnx.py
```

Converts `model.json` → `model.onnx` with input shape `[None, 10]`.

### Step 5 — Verify ONNX

```bash
python verify_onnx.py
```

Runs inference with both the original XGBoost model and the ONNX model and confirms outputs match.

---

## 4. Integration with Stage 1

```bash
copy outputs\model.onnx ..\detector\model.onnx
```

---

## 5. Features Extracted (10 total)

| # | Feature          | Description                               |
|---|------------------|-------------------------------------------|
| 1 | `ear`            | Average eye aspect ratio (both eyes)      |
| 2 | `mar`            | Mouth aspect ratio                        |
| 3 | `pitch`          | Head pitch angle (degrees)                |
| 4 | `yaw`            | Head yaw angle (degrees)                  |
| 5 | `roll`           | Head roll angle (degrees)                 |
| 6 | `ear_variance`   | EAR variance over last 15 frames*         |
| 7 | `mar_variance`   | MAR variance over last 15 frames*         |
| 8 | `blink_rate`     | Estimated blinks/minute (last 90 frames)* |
| 9 | `left_ear`       | Left eye EAR only                         |
|10 | `right_ear`      | Right eye EAR only                        |

\* Temporal features are set to 0 for image-only datasets (no video context).
