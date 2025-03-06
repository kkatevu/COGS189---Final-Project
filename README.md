# EEG-Based Cognitive Focus & Short-Form Video Impact

## Project Overview
This project investigates the impact of short-form video content on cognitive focus using EEG. The experimental design includes the following phases:

1. **Control Recording** - Baseline EEG recording.
2. **Break** - Rest period to reset cognitive state.
3. **Attention Test** - Initial attention assessment.
4. **Doom Scroll** - Exposure to short-form video content (e.g., TikTok, YouTube Shorts).
5. **Attention Task** - Post-exposure attention evaluation.

Using **EEG data**, we aim to analyze how short-form video consumption affects cognitive performance.

## Repository Structure
```
├── data/                   # EEG datasets
├── notebooks/
│   ├── eeg_data_collection.ipynb  # Notebook for collecting EEG data
│   ├── eeg_data_analysis.ipynb    # Notebook for processing and analyzing EEG data
├── src/
│   ├── collect_eeg.py      # Python script for EEG data collection
│   ├── process_eeg.py      # Script for preprocessing and analyzing EEG signals
│   ├── utils.py            # Helper functions
├── README.md               # Project documentation
├── requirements.txt        # Required dependencies
└── LICENSE                 # License information
```

## Installation
### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/yourusername/COGS189---Final-Project.git
 cd COGS189---Final-Project.git
```

### 2️⃣ Set Up Virtual Environment
```sh
python -m venv COGS189
source COGS189/bin/activate  # macOS/Linux
COGS189\Scripts\Activate     # Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

## Usage
### **1️⃣ Collect EEG Data**
To start an EEG recording session:
```sh
python src/collect_eeg.py
```
Alternatively, open and run the **eeg_data_collection.ipynb** notebook in Jupyter.

### **2️⃣ Process EEG Data**
To analyze EEG data and extract features:
```sh
python src/process_eeg.py
```
Or, use **eeg_data_analysis.ipynb** for step-by-step processing in Jupyter Notebook.

## Dependencies
- `numpy`
- `matplotlib`
- `scipy`
- `mne`
- `brainflow`
- `scikit-learn`
- `psychopy`

Install all dependencies with:
```sh
pip install -r requirements.txt
```

## Experiment Design
The experiment consists of five phases:
1. **Control Recording**: Baseline EEG recording.
2. **Break**: Short rest period.
3. **Attention Test**: Initial cognitive assessment.
4. **Doom Scroll**: Participants engage with short-form video content.
5. **Attention Task**: Post-exposure attention test.

## Resources
- **BrainFlow** (EEG data acquisition) - [BrainFlow Documentation](https://brainflow.readthedocs.io/en/stable/)
- **MNE** (EEG processing) - [MNE Tools](https://mne.tools/)
- **PsychoPy** (Stimulus presentation) - [PsychoPy Website](https://www.psychopy.org/)

## License
This project is licensed under the MIT License.

## Contributors
- **Eric Cito Silberman**

Feel free to fork, contribute, and share ideas!

