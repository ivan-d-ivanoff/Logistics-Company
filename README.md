# Logistics Company Project

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/ivan-d-ivanoff/Logistics-Company.git
```

2. **Create and Activate a Virtual Environment**
```bash
python -m venv venv
.venv/Scripts/activate # For Linux: source ./venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
## Coding
In order to maintain the same code structure, we would need to follow some of the base coding principles (**SOLID**, **DRY**, **OOP**).

## **Run the Project**

1. **Activate your Virtual Environment**

2. **Run the Django Project**
```bash
python manage.py runserver
```

## **Commit Strategy**

1. **Run pre-commit hooks**
```bash
pre-commit run --all-files
```

2. **Go to the main branch and create your branch**
```bash
git checkout main
git branch your-branch-name
git checkout your-branch-name

```
3. **Add the files that you want and push them**
```bash
git add your-file-name # If you want to add all the files - git add .
git commit -m "My Commit Message"
git push -u origin your-branch-name # If you have already pushed your branch - git push
```
