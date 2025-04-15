# Project Overview

This project is a Node.js API server that provides user authentication functionality using JWT tokens. It includes routes for user signup, login, and fetching user details. The project uses MongoDB as the database and sends emails for user notifications.

# Features

- User signup: Allows users to create a new account by providing their first name, last name, email, and password.
- User login: Enables users to log in using their email and password, generating a JWT access token for authentication.
- Fetch user details: Retrieves user information based on the user ID provided in the request.
- JWT token generation: Creates JWT tokens for user authentication and authorization.
- Email notifications: Sends emails for user notifications using the configured email provider.

# Usage Instructions

To use this project, follow these steps:
1. Clone the repository to your local machine.
2. Install Node.js and MongoDB on your system.
3. Set up environment variables for the project, including `PORT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_API_KEY`, `TOKEN_SECRET`, `ACCESS_TOKEN_EXPIRY`, `ACCESS_TOKEN_ALGO`, `REFRESH_TOKEN_EXPIRY`, `REFRESH_TOKEN_ALGO`.
4. Run `npm install` to install the project dependencies.
5. Start the MongoDB server.
6. Run `npm start` to start the Node.js server.
7. Use a tool like Postman to test the API endpoints for user signup, login, and fetching user details.

# Folder Structure

- `controllers`: Contains the route controller functions for handling user actions.
- `middlewares`: Includes middleware functions like authentication checks.
- `models`: Defines the MongoDB schema models for user data.
- `routes`: Contains the API routes for user actions.
- `services`: Includes business logic functions for user operations.
- `utils`: Contains utility functions like JWT token generation and error handling.

This README provides a high-level overview of the project, its features, usage instructions, and folder structure. For detailed implementation and code specifics, please refer to the project's source code.