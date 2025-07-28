# RecruitConnect API Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
   - [Auth](#auth)
   - [Jobs](#jobs)
   - [Job Views](#job-views)
   - [Applications](#applications)
   - [Messages](#messages)
   - [Feedback](#feedback)
   - [FAQs](#faqs)
   - [Admin](#admin-endpoints)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [CORS](#cors)
8. [Examples](#examples)

## Introduction
Welcome to the RecruitConnect API documentation. This API powers the RecruitConnect platform, providing endpoints for job postings, applications, messaging, and more.

## Base URL
All API endpoints are prefixed with `/api/v1`.

## Authentication
Most endpoints require authentication using JWT (JSON Web Tokens). Include the token in the `Authorization` header:
```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Auth

#### Register New User
- **Endpoint:** `POST /auth/register`
- **Description:** Create a new user account
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Success Response:** `201 Created`

#### Login
- **Endpoint:** `POST /auth/login`
- **Description:** Authenticate and receive access token
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Success Response:** `200 OK`
  ```json
  {
    "access_token": "<jwt_token>",
    "refresh_token": "<refresh_token>",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "job_seeker"
    }
  }
  ```

### Jobs

#### Get All Jobs
- **Endpoint:** `GET /jobs`
- **Description:** Retrieve all job postings
- **Query Params:** None
- **Success Response:** `200 OK`
  ```json
  [
    {
      "id": 1,
      "title": "Software Engineer",
      "description": "Job description...",
      "location": "Remote",
      "requirements": "Requirements...",
      "created_at": "2023-07-25T10:00:00Z"
    }
  ]
  ```

#### Get Job Details
- **Endpoint:** `GET /jobs/:id`
- **Description:** Get details of a specific job (records a view)
- **Success Response:** `200 OK`

### Job Views

#### Get Monthly Views
- **Endpoint:** `GET /job_views/monthly?year=2023&month=7`
- **Description:** Get monthly job views (Admin only)
- **Success Response:** `200 OK`
  ```json
  {
    "data": [
      {
        "job_id": 1,
        "total_views": 15
      }
    ],
    "message": "Monthly job views retrieved successfully"
  }
  ```

### Applications

#### Create Application
- **Endpoint:** `POST /applications`
- **Description:** Apply for a job
- **Request Body:**
  ```json
  {
    "user_id": 1,
    "job_posting_id": 1
  }
  ```
- **Success Response:** `201 Created`

### Messages

#### Send Message
- **Endpoint:** `POST /messages`
- **Description:** Send a message to another user
- **Request Body:**
  ```json
  {
    "sender_id": 1,
    "receiver_id": 2,
    "content": "Hello, I'm interested in your profile."
  }
  ```
- **Success Response:** `201 Created`

### Feedback

#### Submit Feedback
- **Endpoint:** `POST /feedback`
- **Description:** Submit feedback for an application
- **Request Body:**
  ```json
  {
    "user_id": 1,
    "job_application_id": 1,
    "rating": 5,
    "comment": "Excellent candidate!"
  }
  ```
- **Success Response:** `201 Created`

### FAQs

#### Get All FAQs
- **Endpoint:** `GET /faqs`
- **Description:** Retrieve all FAQs
- **Success Response:** `200 OK`
  ```json
  [
    {
      "id": 1,
      "question": "How do I apply for a job?",
      "answer": "Click on the job and press Apply.",
      "category": "General"
    }
  ]
  ```

### Admin Endpoints

#### Get All Users
- **Endpoint:** `GET /admin/users`
- **Description:** List all users (Admin only)
- **Success Response:** `200 OK`

## Error Handling
Standard HTTP status codes are used:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Example error response:
```json
{
  "message": "Error message here",
  "code": 400
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: 100 requests per minute

## CORS
- Allowed Origin: `http://localhost:5173`
- Credentials: Allowed

## Examples

### Frontend Integration Example
```javascript
const API_BASE = '/api/v1';

// Get all jobs
async function getJobs() {
  const response = await fetch(`${API_BASE}/jobs`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}

// Submit application
async function applyForJob(jobId, userId) {
  const response = await fetch(`${API_BASE}/applications`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      job_posting_id: jobId
    })
  });
  return await response.json();
}
```

## Support
For support, please contact support@recruitconnect.com
