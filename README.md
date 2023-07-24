# Cash Management System API

This is a Restful API for a cash management system that allows users to manage their cash flow by creating and updating transactions, tracking balances, and generating reports.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/cash-management-system.git
   cd cash-management-system
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate   # For Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Development Server

Run the following command to start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

## API Endpoints

### Authentication

- `POST /users/api/register/`: Register a new user with a username and password.
- `POST /users/api/login/`: Authenticate and get an access token.

### Transaction Management

- `POST /api/transaction/`: Create a new transaction.
- `GET /api/transaction/`: List all transactions with filtering and sorting options.
- `GET /api/transaction/{id}/`: Retrieve details of a specific transaction.
- `PATCH /api/transaction/{id}/`: Update a specific transaction.
- `DELETE /api/transaction/{id}/`: Delete a specific transaction.

### Reports

- `POST /api/reports/monthly-summary/`: Generate a monthly summary report.
- `POST /api/reports/category-wise-expense/`: Generate a category-wise expense report.

## Testing

Run the unit tests and integration tests with the following command:

```bash
python manage.py test
```

## Dockerization

To dockerize the application, you can use Docker and Docker Compose. The configuration files for Docker are provided in the repository.

### Build and Run the Docker Containers

To build and run the Docker containers, use the following command:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000/`.

## Documentation

The API endpoints are documented using Postman. The Postman documentation is available in the `docs` folder of the project. To view the documentation, follow these steps:

1. Open Postman application.

2. Import the Postman collection and environment files from the `docs` folder.

3. Once imported, you will have access to the detailed documentation of each API endpoint, including request parameters, response examples, and allowed methods.

4. Explore and test the API endpoints directly from the Postman documentation.