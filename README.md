# DevOps Microservices Demo

A simple microservices architecture demonstration featuring a Python Flask backend API and a web frontend dashboard, designed for DevOps practices including containerization, monitoring, and CI/CD pipelines.

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST API    ┌──────────────────┐
│  Frontend       │◄──────────────────►│  Backend         │
│  Dashboard      │                     │  User API        │
│  (Port 8084)    │                     │  (Port 8086)     │
└─────────────────┘                     └──────────────────┘
```

## 📋 Services Overview

### Backend Service (`backend_service.py`)
- **Purpose**: RESTful API for user management
- **Technology**: Python Flask with CORS support
- **Port**: 8086 (configurable via `PORT` env var)
- **Features**:
  - CRUD operations for user management
  - Health check endpoint
  - Service statistics
  - In-memory database (easily replaceable with real DB)
  - Comprehensive logging
  - Error handling

### Frontend Service (`frontend_service.py`)
- **Purpose**: Web dashboard for user management
- **Technology**: Python Flask with HTML templates
- **Port**: 8084 (configurable via `PORT` env var)
- **Features**:
  - Web-based user interface
  - Real-time service status monitoring
  - Add/Delete user functionality
  - Service health dashboard
  - Responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### 1. Install Dependencies
```bash
cd hiring-account-actions
pip install -r requirements.txt
```

### 2. Start the Backend Service
```bash
python backend_service.py
```
The backend API will be available at `http://localhost:8086`

### 3. Start the Frontend Service
In a new terminal:
```bash
python frontend_service.py
```
The web dashboard will be available at `http://localhost:8084`

### 4. Access the Application
Open your web browser and navigate to `http://localhost:8084` to access the user management dashboard.

## 📚 API Documentation

### Backend Endpoints

#### Health Check
```http
GET /health
```
Returns service health status and metadata.

#### User Management
```http
GET    /api/users           # Get all users
GET    /api/users/{id}      # Get specific user
POST   /api/users           # Create new user
PUT    /api/users/{id}      # Update user
DELETE /api/users/{id}      # Delete user
```

#### Service Statistics
```http
GET /api/stats              # Get service statistics
```

### Frontend Endpoints

#### Dashboard
```http
GET  /                      # Main dashboard
GET  /health                # Frontend health check
POST /add_user              # Add user form submission
GET  /delete_user/{id}      # Delete user action
GET  /api/frontend-stats    # Frontend service stats
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8086 (backend), 8084 (frontend) | Port to run the service |
| `DEBUG` | False | Enable debug mode |
| `ENVIRONMENT` | development | Environment name |
| `BACKEND_URL` | http://localhost:8086 | Backend service URL (frontend only) |

### Example Configuration
```bash
# Backend
export PORT=8086
export DEBUG=true
export ENVIRONMENT=production

# Frontend
export PORT=8084
export BACKEND_URL=http://backend-service:8086
export ENVIRONMENT=production
```

## 🐳 Docker Support

### Backend Dockerfile Example
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend_service.py .
EXPOSE 8086
CMD ["python", "backend_service.py"]
```

### Frontend Dockerfile Example
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY frontend_service.py .
EXPOSE 8084
ENV BACKEND_URL=http://backend:8086
CMD ["python", "frontend_service.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    dockerfile: Dockerfile.backend
    ports:
      - "8086:8086"
    environment:
      - ENVIRONMENT=docker
  
  frontend:
    build: .
    dockerfile: Dockerfile.frontend
    ports:
      - "8084:8084"
    environment:
      - BACKEND_URL=http://backend:8086
      - ENVIRONMENT=docker
    depends_on:
      - backend
```

## ☸️ Kubernetes Deployment

### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        ports:
        - containerPort: 8086
        env:
        - name: ENVIRONMENT
          value: "kubernetes"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8086
    targetPort: 8086
```

## 📊 Monitoring

### Health Checks
- Backend: `GET http://localhost:8086/health`
- Frontend: `GET http://localhost:8084/health`

### Metrics Endpoints
- Backend Stats: `GET http://localhost:8086/api/stats`
- Frontend Stats: `GET http://localhost:8084/api/frontend-stats`

### Sample Health Check Response
```json
{
  "status": "healthy",
  "service": "backend-user-service",
  "timestamp": "2025-08-12T15:30:00.000Z",
  "version": "1.0.0"
}
```

## 🔐 Security Considerations

### Development
- Services run with CORS enabled for cross-origin requests
- No authentication implemented (demo purposes)
- In-memory storage (data not persistent)

### Production Recommendations
- Implement proper authentication/authorization
- Use HTTPS/TLS encryption
- Implement rate limiting
- Use persistent storage (database)
- Add input validation and sanitization
- Enable security headers

## 🧪 Testing

### Manual Testing
1. Start both services
2. Open `http://localhost:8084`
3. Add a new user via the web form
4. Verify the user appears in the table
5. Delete a user and verify removal

### API Testing with curl
```bash
# Test backend health
curl http://localhost:8086/health

# Get all users
curl http://localhost:8086/api/users

# Create a user
curl -X POST http://localhost:8086/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","role":"user"}'

# Get stats
curl http://localhost:8086/api/stats
```

## 🚨 Troubleshooting

### Common Issues

#### Frontend can't connect to backend
- Verify backend is running on port 8086
- Check `BACKEND_URL` environment variable
- Ensure no firewall blocking connections

#### Port already in use
```bash
# Find process using port
lsof -i :8086
lsof -i :8084

# Kill process if needed
kill -9 <PID>
```

#### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📁 Project Structure

```
hiring-account-actions/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── backend_service.py           # Backend REST API
├── frontend_service.py          # Frontend web dashboard
├── delete_user_resources.py     # AWS resource cleanup tool
├── policy.json                  # AWS IAM policy
└── user_resource_cleanup.log    # Cleanup script logs
```

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new routes to `backend_service.py`
2. **Frontend**: Update templates and routes in `frontend_service.py`
3. **API**: Follow RESTful conventions
4. **UI**: Update HTML templates with proper styling

### Code Quality
- Follow PEP 8 style guidelines
- Add proper logging for debugging
- Handle errors gracefully
- Write descriptive commit messages

## 📝 AWS Integration

This project includes AWS resource management tools:
- `delete_user_resources.py`: Cleanup script for AWS resources
- `policy.json`: IAM policy for restricted AWS access
- See individual files for detailed documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for demonstration purposes. Use at your own risk in production environments.

---

**Created for DevOps demonstration and learning purposes** 🚀
