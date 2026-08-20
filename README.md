# 📊 Interactive Data Analytics & SQL Portfolio Portal

![Dashboard Preview](dashboard_preview.jpg)

Welcome to the **Data Analytics & SQL Portfolio Portal**! This repository showcases end-to-end data analytics projects—featuring commercial sales trend analysis and restaurant loyalty program modeling—visualized through a custom, interactive full-stack web application.

---

## 🚀 Live Demo & Deployment

You can deploy this interactive application to the cloud for free using either **Render** or **Vercel**!

### Option A: Deploy with Vercel (Recommended)
1. Push this repository to your **GitHub** account.
2. Sign up or log in to **[Vercel.com](https://vercel.com/)**.
3. Click **Add New** and select **Project**.
4. Import your GitHub repository.
5. Vercel will automatically detect `vercel.json`, build the serverless Python environment, install your `requirements.txt`, and deploy the app.
6. You will get a fast, production-ready URL (e.g., `https://your-project.vercel.app`) to share with recruiters!

### Option B: Deploy with Render
1. Push this repository to your **GitHub** account.
2. Sign up or log in to **[Render.com](https://render.com/)**.
3. Click **New +** and select **Blueprint**.
4. Connect this GitHub repository. Render will read the `render.yaml` file and deploy the Flask server.
5. You will get a live URL (e.g., `https://your-project.onrender.com`).

---

## 🌟 Interactive Portal Features

### 1. 🛒 Amazon Sales Analysis Dashboard
An interactive dashboard displaying global sales statistics, margins, and distributions using real commercial data.
* **Key Metrics**: Dynamic calculations of Total Revenue, Total Profit, Profit Margin (%), Units Sold, and Average Order Value (AOV).
* **Interactive Charts** (via *Chart.js*):
  * Monthly Revenue & Profit Trendlines.
  * Product Category Revenue breakdowns.
  * Sales Channel mix (Online vs. Offline).
  * Regional Market share distribution.
* **Notebook Integration**: Access and read the full Python/Pandas analysis notebook directly inside the dashboard.

### 2. 🍜 Danny's Diner (SQL Case Study)
A SQL playground sandbox containing a complete dataset (Sales, Menu, Members tables) loaded into an in-memory SQLite database.
* **Preloaded Case Study Queries**: Quick-load any of the 10 loyalty case study questions (e.g., customer spending, point systems, and membership window promos).
* **Live SQL Runner**: Edit, write, and execute custom SQL queries directly in the browser and see real-time tables returned.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.11, Flask, Pandas, SQLite3 (multi-threaded shared cache)
- **Frontend**: HTML5, CSS3 (Glassmorphism layout, modern typography, transitions), JavaScript (ES6)
- **Data Visuals**: Chart.js (Interactive Charts CDN)
- **Deployment**: Render Blueprint (`render.yaml`), Gunicorn WSGI

---

## 💻 How to Run Locally

If you want to run this project on your local machine, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Data-Analytics-Projects-main.git
   cd Data-Analytics-Projects-main/Data-Analytics-Projects-main
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask Server**:
   ```bash
   python server.py
   ```

4. **Open in Browser**:
   Navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** to interact with the workspace!
