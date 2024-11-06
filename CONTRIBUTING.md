# Contributing to Weather Station Monitoring System

## Welcome Contributors! 🌦️

We're thrilled that you're interested in contributing to our Weather Station Monitoring System. This document provides guidelines and instructions for contributing to the project.

## 🌟 Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We are committed to providing a welcoming and inspiring community for all.

## 🚀 How to Contribute

There are many ways to contribute to our project:

### 1. Reporting Bugs 🐛
- Use GitHub Issues
- Provide a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Include system details and Python version
- Add error messages or screenshots if applicable

### 2. Suggesting Enhancements 💡
- Open a GitHub Issue
- Clearly describe the proposed enhancement
- Provide context and rationale
- Include potential implementation details if possible

### 3. Code Contributions 💻

#### Development Setup

1. Fork the repository
2. Clone your fork
```bash
git clone https://github.com/your-username/weather-station.git
cd weather-station
```

3. Create a virtual environment
```bash
uv venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows
```

4. Install development dependencies
```bash
uv pip install -e ".[dev]"
```

5. Install pre-commit hooks
```bash
pre-commit install
```

#### Development Workflow

1. Create a new branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

2. Make your changes
- Follow PEP 8 style guidelines
- Write clear, concise code
- Add/update tests
- Update documentation

3. Run checks before committing
```bash
task lint      # Run linters
task format    # Format code
task test      # Run tests
```

4. Commit your changes
```bash
git add .
git commit -m "Description of changes"
```

5. Push to your fork
```bash
git push origin feature/your-feature-name
```

6. Open a Pull Request
- Provide a clear PR title
- Describe the changes in detail
- Reference any related issues

### 4. Documentation 📚
- Improve existing documentation
- Add examples
- Fix typos or clarify explanations
- Update docstrings

### 5. Testing 🧪
- Write unit tests
- Improve test coverage
- Test edge cases
- Verify sensor simulations

## 🛠 Development Tasks

We use `task` for common development workflows:

```bash
# Install dependencies
task deps:install

# Run tests
task test

# Run tests with watch
task test:watch

# Lint code
task lint

# Format code
task format

# Build documentation
task docs:build

# Serve documentation
task docs:serve
```

## 🤝 Contribution Guidelines

### Code Quality
- Write clean, readable code
- Follow type hints
- Use meaningful variable names
- Add docstrings
- Write comprehensive tests

### Performance
- Optimize for memory efficiency
- Use async programming patterns
- Minimize computational complexity

### Sensor Integration
- Create generic, reusable sensor interfaces
- Provide clear documentation
- Include error handling
- Support multiple sensor types

## 🏆 Recognition

Contributors will be recognized in:
- README.md
- Documentation
- Release notes
- GitHub Contributors graph

## 📋 Review Process

1. Automated checks will run
2. Maintainers will review the PR
3. Feedback and suggestions may be provided
4. Changes may be requested
5. Once approved, the PR will be merged

## 💬 Communication

- GitHub Issues
- Discussion Forums
- Email: support@weatherstation.dev

## 🔒 Security

If you discover a security vulnerability, please:
1. Do not open a public issue
2. Email security@weatherstation.dev
3. Provide detailed information
4. Allow time for investigation

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping improve the Weather Station Monitoring System!** 🌈
