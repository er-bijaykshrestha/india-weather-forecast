# LinkedIn post draft

Edit the bracketed parts, add 1-2 images (dashboard screenshot + the NASA vs ERA5 chart or warming stripes), and put the links in the first comment if you want better reach.

---

I spent my internship forecasting India's temperatures. The most useful result was a humbling one. 🌦️

I built an end-to-end project on 45 years of daily weather data for 8 Indian cities (Delhi, Mumbai, Chennai, Kolkata, Bengaluru, Hyderabad, Jaipur, Shimla):

📊 Cleaned and analysed the data (seasonality, trends, monsoon variability)
🔍 Checked the data against a second source (ERA5) before trusting it
🤖 Compared 6 forecasting models with rolling cross-validation and a held-out 2026 test
🖥️ Built a Streamlit dashboard with 12-month forecasts and uncertainty bands

What I found:

→ SARIMA won, with about 0.8°C average error and well-calibrated prediction intervals
→ A simple "average of the same month over 10 years" came very close to it, and XGBoost didn't help. Monthly temperature is mostly seasonal
→ Two respected datasets (NASA POWER and ERA5) agreed on year-to-year ups and downs, but NOT on long-term trends in most cities. Validating the data changed what I could honestly claim

Biggest lesson: a model is only as trustworthy as its data, and a simple baseline is the best way to keep yourself honest.

🔗 Live app: [link]
💻 Code: [GitHub link]

Thanks to [mentor / team name] for the guidance. Feedback welcome, especially from anyone working with IMD station data!

#DataScience #MachineLearning #TimeSeries #Python #Streamlit #Weather #India #Internship
