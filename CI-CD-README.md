# CARML - AI Powered Car Ownership Analytics

## DevOps Lab Project

### Student Details

**Name:** Aakash Raghu
**USN:** 1MS23IS002
**Course:** DevOps Laboratory

---

# Project Overview

CARML (Car Machine Learning Analytics) is an AI-powered web application that helps users compare used cars and predict long-term ownership value. The system uses a Linear Regression Machine Learning model to estimate vehicle depreciation and future resale value based on various factors such as car age, mileage, fuel type, ownership history, and market value.

The application allows users to:

* Search cars based on budget.
* Select and compare three vehicles.
* Predict depreciation using Machine Learning.
* Estimate future resale value.
* Analyze 5-year ownership costs.
* Generate a Best Buy Recommendation.

---

# Technology Stack

## Frontend

* HTML5
* CSS3
* Ferrari-inspired Premium UI Theme

## Backend

* Python
* FastAPI

## Machine Learning

* Scikit-Learn
* Linear Regression
* Pandas
* NumPy

## DevOps Tools

### Source Control

* Git
* GitHub

### Continuous Integration

* Jenkins

### Code Quality Analysis

* Flake8

### Vulnerability Scanning

* Trivy

### Containerization

* Docker

### Deployment

* Render

---

# Project Architecture

GitHub Repository

↓

Jenkins Pipeline

↓

Flake8 Code Quality Analysis

↓

Trivy Vulnerability Scan

↓

Docker Image Build

↓

GitHub Push

↓

Render Deployment

↓

Live Application

---

# Machine Learning Model

## Algorithm Used

Linear Regression

## Features Used

* Car Name
* Fuel Type
* Seller Type
* Transmission
* Present Price
* Kilometers Driven
* Owner Count
* Car Age

## Target Variable

Vehicle Depreciation

### Formula

Depreciation = Present Price − Selling Price

---

# Key Features

## Budget-Based Search

Users can search for vehicles within a specified price range.

## Multi-Car Comparison

The system allows users to compare three cars simultaneously.

## Depreciation Prediction

Machine Learning predicts future depreciation.

## Ownership Forecast

Predicts future vehicle value after 5 years.

## Best Buy Recommendation

The application identifies the most economical vehicle based on predicted future value.

---

# CI/CD Pipeline

The Jenkins pipeline performs the following tasks:

## Stage 1

Checkout source code from GitHub.

## Stage 2

Install Python dependencies.

## Stage 3

Run Flake8 code quality analysis.

## Stage 4

Run Trivy vulnerability scan.

## Stage 5

Build Docker image.

## Stage 6

Push Docker image (Optional Pipeline).

## Stage 7

Deploy application to Render.

---

# Jenkins Pipelines

## Pipeline 1

### Full CI/CD Pipeline

Includes:

* GitHub Checkout
* Dependency Installation
* Flake8 Analysis
* Trivy Scan
* Docker Build
* Docker Push
* Deployment

---

## Pipeline 2

### CI/CD Pipeline Without Docker Push

Includes:

* GitHub Checkout
* Dependency Installation
* Flake8 Analysis
* Trivy Scan
* Docker Build
* Deployment

Docker Push Stage Removed.

---

# Code Quality Analysis

Tool Used:

## Flake8

Flake8 performs:

* Style Checking
* Syntax Validation
* Error Detection
* PEP8 Compliance Checks
* Unused Import Detection

---

# Vulnerability Scanning

Tool Used:

## Trivy

Trivy scans:

* Python Dependencies
* Docker Images
* Operating System Packages
* Known CVEs

---

# Docker

## Build Command

```bash
docker build -t carml .
```

## Run Command

```bash
docker run -p 8000:8000 carml
```

---

# Running Locally

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start Application

```bash
uvicorn CARML.api:app --reload
```

## Access Application

```text
http://127.0.0.1:8000
```

---

# Deployment

Platform Used:

## Render

Application URL:

```text
https://carml.onrender.com
```

---

# Project Workflow

1. User enters budget range.
2. Application displays matching vehicles.
3. User selects three cars.
4. User enters annual running distance.
5. Machine Learning model predicts depreciation.
6. Future value is estimated for each car.
7. System compares all vehicles.
8. Best Buy Recommendation is generated.

---

# Future Enhancements

* Random Forest Regression
* XGBoost Model
* Real-Time Vehicle Market Data
* Price Trend Visualization
* User Authentication
* Vehicle Image Gallery
* Advanced Ownership Cost Analysis
* Fuel Cost Forecasting

---

# Conclusion

CARML combines Machine Learning and DevOps practices to create a complete end-to-end vehicle analytics platform. The project demonstrates source control management, CI/CD automation, code quality analysis, vulnerability scanning, containerization, cloud deployment, and predictive analytics in a single integrated solution.

The system enables users to make informed vehicle purchasing decisions through AI-driven depreciation forecasting and long-term ownership analysis.
changes1