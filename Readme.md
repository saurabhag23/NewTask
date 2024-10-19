# 🏦 Stock Price Prediction & Backtesting Django Application

This project provides a stock price prediction and backtesting platform built using Django, PostgreSQL, and machine learning. It allows users to perform backtesting on stock data, predict future stock prices, and generate reports in PDF format with visualizations comparing predictions to actual data.

## ✨ Features

- **Backtesting Module**: Test investment strategies based on historical data.
- **Stock Price Predictions**: Predict stock prices using a pre-trained machine learning model (linear regression).
- **Report Generation**: Download PDF reports comparing predicted and actual stock prices with key metrics and charts.
- **Dockerized Setup**: Containerized application for easy setup and deployment.
- **AWS Integration**: Ready to deploy using AWS ECS and RDS (PostgreSQL).
- **CI/CD Pipeline**: Automated deployment using GitHub Actions.

## 🛠️ Technologies Used

- Django: Backend framework.
- PostgreSQL: Relational database (AWS RDS in production).
- Docker: Containerization.
- AWS RDS: Managed PostgreSQL database service.
- AWS ECS: Elastic Container Service for deployment.
- Alpha Vantage API: For fetching historical stock data.
- GitHub Actions: CI/CD pipeline.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock-prediction-django.git
cd stock-prediction-django
```

### 2. Set Up the Environment

We recommend using a virtual environment to isolate dependencies. Run:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies

Install all the project dependencies listed in requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The project uses API keys and database credentials, so you need to configure environment variables. Create a `.env` file at the project root with the following content:

```bash
DEBUG=True
SECRET_KEY=YourSecretKeyHere
ALPHA_VANTAGE_API_KEY=YourAlphaVantageApiKeyHere
DATABASE_URL=postgres://dbuser:dbpassword@localhost:5432/dbname
```

🔒 **Note**: Keep your `.env` file secret and do not commit it to version control. Use environment variable management tools like dotenv or AWS Secrets Manager in production.

### 5. Run Migrations

```bash
python manage.py migrate
```

This will create the necessary database tables for your application.

### 6. Seed Stock Data

Use the custom management command to fetch and seed historical stock data into your database:

```bash
python manage.py fetch_stock_data AAPL
```

This command fetches daily stock prices for the symbol AAPL (Apple) from the Alpha Vantage API and stores them in your PostgreSQL database.

### 7. Run the Application

Once your environment is set up, run the Django development server:

```bash
python manage.py runserver
```

Your project will be available at http://127.0.0.1:8000/.

## 🐳 Docker Setup

### 1. Build and Run the Docker Containers

The project is fully Dockerized for easy deployment. To build and run the project in Docker:

```bash
docker-compose build
docker-compose up
```

This will start both the Django application and a PostgreSQL container.

### 2. Run Migrations & Seed Data in Docker

After the containers are running, you can run your migrations and seed data from inside the web container:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py fetch_stock_data AAPL
```

Now you should be able to access the application running on http://localhost:8000.

## 🔑 API Endpoints

Below is a list of key API endpoints:

### 1. Backtesting Module

- **URL**: `/stocks/backtest/`
- **Method**: POST
- **Payload**:
  ```json
  {
    "symbol": "AAPL",
    "initial_investment": 10000,
    "short_window": 50,
    "long_window": 200
  }
  ```
- **Response**: Backtesting results including total return, number of trades, and max drawdown.

### 2. Stock Price Prediction

- **URL**: `/stocks/predict/<symbol>/`
- **Method**: GET
- **Response**: JSON containing predicted stock prices for the next day based on a pre-trained linear regression model.

### 3. Report Generation

- **URL**: `/stocks/report/<symbol>/`
- **Method**: GET
- **Response**: A PDF report comparing predicted stock prices to actual prices, along with key metrics like mean, max, and min prices.

## ☁️ Deployment on AWS

The project is designed to be deployed on AWS using ECS for container orchestration and RDS for the PostgreSQL database.

### 1. Set Up AWS RDS (PostgreSQL)

1. Create a PostgreSQL RDS instance:
   - Go to the AWS RDS console and create a PostgreSQL database instance.
   - Set up the necessary VPC and security groups to allow traffic from your application.

2. Update Environment Variables:
   - In your `.env` file, update the `DATABASE_URL` to point to your RDS instance:
     ```bash
     DATABASE_URL=postgres://dbuser:dbpassword@rds-endpoint:5432/dbname
     ```
   - Replace `rds-endpoint` with your actual RDS instance endpoint.

### 2. Deploy the Application on AWS ECS

1. Create an ECS Cluster:
   - Use the AWS Management Console to create an ECS cluster with Fargate or EC2 launch type.

2. Create Docker Images and Push to AWS ECR:
   - Create a repository in AWS ECR and push your Docker image:
     ```bash
     docker build -t stock-prediction .
     docker tag stock-prediction:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/stock-prediction:latest
     docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/stock-prediction:latest
     ```

3. Set Up ECS Task Definition:
   - Create an ECS task definition that uses your Docker image from ECR and links it to your RDS database.

### 3. CI/CD Pipeline with GitHub Actions

The project comes with a predefined CI/CD pipeline using GitHub Actions. The pipeline is configured to:

- Run tests automatically on every push.
- Build Docker images and push them to AWS ECR.
- Deploy the new image to AWS ECS.

The CI/CD workflow is defined in `.github/workflows/deploy.yml`. You can configure this to suit your deployment setup.

## 🧪 Running Tests

The project includes unit tests to validate core functionality. You can run them with:

```bash
python manage.py test
```

The tests cover the following features:

- Stock data fetching from Alpha Vantage API.
- Backtesting logic and calculations.
- Stock price prediction using the pre-trained machine learning model.
- Key API endpoints.

## 📊 Report Generation Details

The report generated by this application contains the following:

- **Key Metrics**:
  - Mean, max, and min predicted prices.
  - Mean, max, and min actual prices.
- **Graph**:
  - Comparison between predicted and actual stock prices over a time period.
- **Output Formats**:
  - Downloadable PDF.
  - JSON response (for programmatic access).

## ⚙️ Additional Configuration

### Secrets & API Keys

- **Alpha Vantage API Key**: This is required for fetching stock data. You need to set this in the `.env` file as `ALPHA_VANTAGE_API_KEY`.
- **SECRET_KEY**: This is required for Django's cryptographic signing and must be set in the `.env` file.

### Custom Management Commands

- `fetch_stock_data`: Fetch stock data from Alpha Vantage.
- `generate_predictions`: Generates stock price predictions using a pre-trained model.

## 💡 Troubleshooting

- **Error: psql command not found**: Install PostgreSQL locally or use Docker for PostgreSQL.
- **Cannot connect to AWS RDS**: Make sure your security groups allow inbound traffic from your application to your RDS instance.

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.
