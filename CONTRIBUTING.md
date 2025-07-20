# Contributing to PCAP Replaya

Thank you for your interest in contributing to PCAP Replaya! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Linux environment (for network interface access)
- Git for version control
- Basic knowledge of Python (Flask) and JavaScript (React)

### Development Environment
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/pcap-replaya.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Quick Start
```bash
# Clone the repository
git clone https://github.com/blink-zero/pcap-replaya.git
cd pcap-replaya

# Start the development environment
sudo docker-compose up --build
```

### Local Development

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Contributing Process

### 1. Issue First
- Check existing issues before creating new ones
- For bugs, provide detailed reproduction steps
- For features, discuss the proposal in an issue first

### 2. Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### 3. Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(upload): add support for .cap files`
- `fix(websocket): resolve connection issues with dynamic hosts`
- `docs(readme): update installation instructions`

### 4. Pull Request Process
1. Ensure your code follows the coding standards
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Testing instructions

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Maximum line length: 88 characters (Black formatter)

### JavaScript (Frontend)
- Use ES6+ features
- Follow React best practices
- Use meaningful variable and function names
- Add JSDoc comments for complex functions

### General Guidelines
- Write self-documenting code
- Add comments for complex logic
- Use meaningful commit messages
- Keep functions small and focused

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Start the application
sudo docker-compose up --build -d

# Test API endpoints
curl http://localhost:5000/api/health

# Test file upload
curl -X POST -F "file=@test.pcap" http://localhost:5000/api/upload
```

## Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Contact @blink-zero for questions or security issues

Thank you for contributing to PCAP Replaya!
