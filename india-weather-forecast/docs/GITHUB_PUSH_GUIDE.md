# Push to GitHub: step by step

## One-time setup
1. Install Git: https://git-scm.com/download/win (check with `git --version`)
2. Tell Git who you are:
   ```
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
3. On github.com click **New repository**, name it `india-weather-forecast`, set it to **Public**,
   and do **not** tick "Add a README", ".gitignore" or "license" (this project already has them).
4. Copy the repository URL, e.g. `https://github.com/YOUR-USERNAME/india-weather-forecast.git`

## Before pushing, put these in place
- [ ] The notebooks, run and **saved with outputs**, in `notebooks/`
- [ ] All charts in `reports/figures/` (01 to 12) plus your app screenshot `dashboard.png`
- [ ] The 5 CSVs in `reports/` and `data/monthly_temperature.csv`
- [ ] Your name in `LICENSE`

Then run the checker. It also verifies that every image in the README exists with the exact capital letters
(GitHub is case-sensitive, Windows is not):
```
python scripts/check_before_push.py
```

## Push (easy way)
Windows PowerShell, from the project folder:
```
.\scripts\push_to_github.ps1 -RepoUrl https://github.com/YOUR-USERNAME/india-weather-forecast.git
```
Mac/Linux/Git Bash:
```
bash scripts/push_to_github.sh https://github.com/YOUR-USERNAME/india-weather-forecast.git
```
If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process Bypass` first.

## Push (manual way)
```
git init
git add .
git commit -m "Add India weather analysis and forecasting project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/india-weather-forecast.git
git push -u origin main
```

## After the push
- Open the repo page and check that the README images and the notebooks display.
- Click the gear next to **About**: add a description, your live app link and topics
  (`time-series`, `forecasting`, `streamlit`, `weather`, `india`, `data-science`).
- Deploy on https://share.streamlit.io (repo `main`, file `app.py`), then paste the live link into the README.
- Pin the repository on your GitHub profile.

## Updating later
```
git add .
git commit -m "Describe what you changed"
git push
```
