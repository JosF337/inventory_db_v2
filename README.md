# 📦 Enlarz Inventory Management System

A professional, full-stack Inventory Management application built with **Python** and **Flask**. 
It features a modern **Glassmorphism UI**, QR Code generation, CSV data export, and smart warranty tracking logic.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## ✨ Features

* **Modern UI:** A clean, responsive "Glassmorphism" interface built with custom CSS and Bootstrap 5.
* **Smart Dashboard:** Live search with autocomplete suggestions and status indicators.
* **CRUD Operations:** Create, Read, Update, and Delete assets easily.
* **QR Code Integration:** Automatically generates QR codes linked to asset details.
* **Warranty Tracking:** Business logic automatically calculates warranty status (Active/Expired) based on purchase dates.
* **Data Export:** One-click CSV export for reporting.
* **Defensive Design:** Handles missing or null data gracefully without crashing.

---

## 🏗️ Project Architecture

This project follows the **MVC (Model-View-Controller)** pattern and adheres to **SOLID principles** for maintainability:

* **Controller (`app.py`):** Handles routing, request processing, and business logic.
* **Model (`inventory.db`):** SQLite database managed via raw SQL for performance and transparency.
* **View (`templates/`):** Jinja2 templates extending a `base.html` layout for DRY (Don't Repeat Yourself) code.
* **Assets (`static/`):** Separated CSS and logic for the frontend.

### Directory Structure
```text
inventory_project/
├── app.py                 # Application Entry Point
├── setup_db.py            # Database Initialization Script
├── requirements.txt       # Dependency List
├── data/
│   └── inventory.csv      # Raw Data Source
├── static/
│   └── css/
│       └── style.css      # Custom Theme (Glassmorphism)
└── templates/
    ├── base.html          # Master Layout
    ├── index.html         # Dashboard
    ├── detail.html        # Item Details
    └── form.html          # Add/Edit Form (Shared)