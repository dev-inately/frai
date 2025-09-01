# 🤖 AI Contract Generator

An AI-powered contract generation platform that creates professional legal contracts using advanced language models. The platform features real-time streaming generation, contract management, and a modern web interface.

## 🏗️ Project Structure

```
FirstReadAI/
├── backend/                 # FastAPI backend service
│   ├── app/                # Application modules
│   ├── main.py            # FastAPI application entry point
│   ├── requirements.txt   # Python dependencies
│   ├── pyproject.toml     # Project configuration
│   └── Makefile          # Development commands
├── frontend/               # React + TypeScript frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
├── shared/                 # Shared utilities and types
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm or yarn
- **OpenAI API Key** (or compatible AI provider)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd FirstReadAI
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
make install-dev

# Copy environment file
cp env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=your_actual_api_key_here

# Start development server
make start
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env with your backend URL
# VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Backend Development

### Installation

```bash
cd backend

# Production dependencies only
make install

# Development dependencies (includes testing, linting, formatting)
make install-dev

# Test dependencies
make install-test
```

### Running the Backend

```bash
# Development server with auto-reload
make start

# Production server
make start-prod

# Custom port (if needed)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Development Commands

```bash
# Run tests
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-cov               # Tests with coverage
make test-fast              # Fast execution (stop on first failure)

# Code quality
make format                 # Format code with black and isort
make lint                   # Run flake8 linting
make type-check            # Run mypy type checking
make check                 # Run all quality checks

# Cleanup
make clean                 # Remove generated files
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
AI_BASE_URL=https://openrouter.ai/api/v1

# API Configuration
CORS_ORIGINS="*"

# AI Model Configuration
DEFAULT_MODEL=openai/gpt-4o-mini

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Contract Generation
MAX_TOKENS_PER_SECTION=100000

# Logging
LOG_LEVEL=INFO
```

## 🎨 Frontend Development

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

### Running the Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint
```

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Cloudflare Configuration (optional)
VITE_CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id_here
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
make test

# Run specific test categories
make test-unit              # Unit tests only
make test-integration       # Integration tests only

# Run with coverage
make test-cov               # Generates HTML coverage report

# Debug tests
make test-debug             # Verbose output with full tracebacks
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run tests in watch mode
npm run test -- --watch
```

## 📚 API Documentation

Once the backend is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔌 API Endpoints

### Core Endpoints

- `POST /api/generate-contract` - Generate contract with streaming
- `POST /api/generate-contract-full` - Retrieve complete contract
- `GET /api/contracts` - List all contracts
- `DELETE /api/contracts/{id}` - Delete a contract
- `GET /health` - Health check
- `GET /` - API information page

### Example Usage

```bash
# Generate a contract
curl -X POST "http://localhost:8000/api/generate-contract" \
  -H "Content-Type: application/json" \
  -d '{
    "business_context": {
      "description": "A SaaS company providing project management tools",
      "industry": "SaaS",
      "location": "California",
      "company_size": "Startup"
    },
    "contract_type": "terms_of_service",
    "language": "en"
  }'

# List contracts
curl "http://localhost:8000/api/contracts?limit=10&offset=0"
```

## 🚀 Deployment

### Backend Deployment

```bash
cd backend

# Install production dependencies
make install

# Start production server
make start-prod

# Or with custom configuration
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# The built files will be in the `dist/` directory
# Deploy this directory to your hosting provider
```

## 🛠️ Development Workflow

### 1. Start Both Services

```bash
# Terminal 1 - Backend
cd backend
make start

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Make Changes

- Backend changes auto-reload with `--reload` flag
- Frontend changes auto-reload with Vite HMR
- Both services watch for file changes

### 3. Run Tests

```bash
# Backend tests
cd backend
make test

# Frontend tests
cd frontend
npm run test
```

### 4. Code Quality

```bash
# Backend
cd backend
make format
make lint
make type-check

# Frontend
cd frontend
npm run lint
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if port 8000 is available
lsof -i :8000

# Check Python version
python --version  # Should be 3.9+

# Check uv installation
uv --version

# Reinstall dependencies
cd backend
make clean
make install-dev
```

#### Frontend Won't Start
```bash
# Check if port 3000 is available
lsof -i :3000

# Check Node.js version
node --version  # Should be 18+

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Issues
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Ensure VITE_API_URL is correct in frontend/.env

# Check network requests in browser DevTools
```

### Logs

- **Backend logs**: Check `backend/logs/app.log`
- **Frontend logs**: Check browser console and terminal output
- **API logs**: Backend logs show all requests and errors

## 📖 Additional Resources

- [Backend Testing Guide](backend/TESTING.md) - Comprehensive testing documentation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Task Documentation](Task.md) - Project requirements and specifications
- [Checklist](checklist.md) - Development checklist and milestones

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test` (backend) and `npm run test` (frontend)
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Check the logs for error details
- Open an issue in the repository

---

**Happy coding! 🚀**
