# Social Media API
This project provides a set of APIs to implement various social media features. It is built using Python, Django, and the Django Rest Framework.

## Installation Instructions (Docker)

To run the project using Docker, follow these steps:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Build the Docker image:
   ```
   docker-compose build
   ```
3. Start the Docker containers:
   ```
   docker-compose up
   ```
## The main features of this project include:

- Token-based Login/Signup: Users can register and log in using their credentials. The login/signup process is token-based for authentication.
- Search API: Users can search for other users based on their first name, last name, or email address.
- Friend Request API: Users can send friend requests to other users and receive pending friend requests.
- Accept/Reject Friend Request API: Users can accept or reject friend requests received from other users.
- Friend List API: Users can retrieve a list of their friends.
- Docker Containerization: The project is containerized using Docker for easy deployment and scalability.
- Test Cases: Test cases are implemented to ensure the correctness of the APIs.
- Pre-commit Integration: Pre-commit hooks are set up to enforce code quality standards and formatting guidelines.
- Swagger integration with djangoREST.


#### This will start the project and make it accessible at `http://localhost:8000`.

# Swagger Link
![image](https://github.com/VISHU1999/DRF-with-swagger-example/assets/70027559/d542616c-667f-442c-9a8d-b8395aa00b02)

```
http://0.0.0.0:8000/doc/
```
API doc
```
http://0.0.0.0:8000/api/redoc/
```

## API Documentation

The API endpoints provided by this project are as follows:

- **Token-based Login/Signup API**:
  - `POST /login/`: User login with email and password.
  - `POST /register/`: User registration with username, password, email, first name, and last name.

- **Search API**:
  - `GET /search_user/`: Search for users based on first name, last name, or email.

- **Friend Request API**:
  - `POST /friend_request/`: Send a friend request to a user.
  - `GET /friend_request/`: Get a list of pending friend requests.

- **Accept/Reject Friend Request API**:
  - `PUT /friend_request/{request_id}/accept_request/`: Accept a friend request.
  - `PUT /friend_request/{request_id}/reject_request/`: Reject a friend request.

- **Friend List API**:
  - `GET /user_friend_list/`: Get a list of friends for the current user.

Please refer to the source code and the provided test cases for more details on how to use these APIs.

## Test Cases

The project includes test cases to verify the functionality and correctness of the implemented APIs. These test cases cover various scenarios and ensure that the APIs are working as expected. To run the test cases, use the following command:

```
docker-compose run django-web bash -c "pytest"
```

## Code Quality and Formatting

This project follows code quality standards and formatting guidelines to ensure clean and maintainable code. It includes pre-commit hooks that automatically enforce these standards and formatting rules before committing changes. The hooks are set up to run `black` code formatter and other code quality checks. It is recommended to run `pre-commit install` to enable the pre-commit hooks.

Please review the `.pre-commit-config.yaml` file and the project's documentation for more details on the specific code quality checks and formatting rules applied.
