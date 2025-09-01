# Testing Guide for AI Contract Generator Backend

This document explains how to run tests for the backend service.

## Test Structure

The test suite is organized into several categories:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test how components work together
- **API Tests**: Test HTTP endpoints and responses
- **Model Tests**: Test Pydantic model validation
- **Database Tests**: Test database operations (mocked)

## Prerequisites

1. Install test dependencies:
```bash
make install-test
# or
uv pip install -r requirements-test.txt
```

2. Ensure you have pytest and related packages:
```bash
uv pip install pytest pytest-asyncio pytest-mock pytest-cov httpx
```

## Running Tests

### Run All Tests
```bash
make test
# or
uv run pytest test_main.py -v
# or
python run_tests.py
```

### Run Specific Test Categories

**Unit Tests Only:**
```bash
make test-unit
# or
uv run pytest test_main.py -m "not integration" -v
```

**Integration Tests Only:**
```bash
make test-integration
# or
uv run pytest test_main.py -m "integration" -v
```

**Tests with Coverage:**
```bash
make test-cov
# or
uv run pytest test_main.py --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Tests

**Run a specific test class:**
```bash
uv run pytest test_main.py::TestModels -v
```

**Run a specific test method:**
```bash
uv run pytest test_main.py::TestModels::test_business_context_valid -v
```

**Run tests matching a pattern:**
```bash
uv run pytest test_main.py -k "contract" -v
```

### Test Execution Options

**Fast execution (stop on first failure):**
```bash
make test-fast
# or
uv run pytest test_main.py -x --tb=no
```

**Debug mode (verbose output):**
```bash
make test-debug
# or
uv run pytest test_main.py -v -s --tb=long
```

## Test Categories

### 1. Model Tests (`TestModels`)
- Pydantic model validation
- Field constraints and validators
- Business logic validation

### 2. Health Endpoint Tests (`TestHealthEndpoints`)
- Root endpoint (HTML response)
- Health check endpoint
- Response format validation

### 3. Contract Generation Tests (`TestContractGeneration`)
- Contract generation streaming
- Error handling for invalid requests
- AI client error scenarios
- Mocked AI responses

### 4. Contract Retrieval Tests (`TestContractRetrieval`)
- Contract retrieval by ID
- Not found scenarios
- Response format validation

### 5. Contract Listing Tests (`TestContractListing`)
- Contract listing with pagination
- Empty result handling
- Query parameter validation

### 6. Contract Deletion Tests (`TestContractDeletion`)
- Successful contract deletion
- Not found scenarios
- Response validation

### 7. Database Manager Tests (`TestDatabaseManager`)
- Database statistics
- Mocked database operations

### 8. Contract Engine Tests (`TestContractEngine`)
- Engine initialization
- Contract type retrieval
- Mocked responses

### 9. AI Client Tests (`TestAIClient`)
- Health check functionality
- Mocked AI responses

### 10. Error Handling Tests (`TestErrorHandling`)
- Invalid JSON handling
- Missing field validation
- CORS headers
- Process time headers

### 11. Integration Tests (`TestIntegration`)
- Complete contract lifecycle
- End-to-end workflow testing
- Mocked external dependencies

## Test Data

The test suite uses predefined test data:

- **Sample Business Context**: SaaS company description
- **Sample Contract Request**: Terms of service generation request
- **Sample Contract Sections**: Mock contract content

## Mocking Strategy

Tests use extensive mocking to avoid external dependencies:

- **AI Client**: Mocked to return predefined responses
- **Database**: Mocked to return test data
- **Contract Engine**: Mocked parsing and HTML generation
- **External Services**: All external calls are mocked

## Test Configuration

### pytest.ini
- Configures test discovery patterns
- Sets default options for verbose output
- Configures asyncio mode for async tests

### test.env
- Test-specific environment variables
- Uses test API keys and database URLs
- Debug logging for test execution

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- Fast execution (under 30 seconds)
- No external dependencies
- Comprehensive coverage reporting
- Clear pass/fail indicators

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure test dependencies are installed
2. **Async Issues**: Check pytest-asyncio configuration
3. **Mock Errors**: Verify patch decorators match import paths
4. **Database Errors**: Ensure test database is accessible

### Debug Mode

For debugging test failures:

```bash
make test-debug
# or
uv run pytest test_main.py -v -s --tb=long
```

### Coverage Analysis

Generate detailed coverage reports:

```bash
make test-cov
```

This creates:
- Terminal coverage summary
- HTML coverage report in `htmlcov/` directory

## Best Practices

1. **Test Isolation**: Each test is independent
2. **Mock External Dependencies**: No real API calls or database writes
3. **Clear Assertions**: Each test has specific, verifiable assertions
4. **Descriptive Names**: Test names clearly describe what they test
5. **Comprehensive Coverage**: All endpoints and error cases are tested

## Adding New Tests

When adding new functionality:

1. Create corresponding test classes
2. Mock external dependencies
3. Test both success and failure scenarios
4. Add appropriate markers for test categorization
5. Update this documentation

## Performance

- **Unit Tests**: < 5 seconds
- **Integration Tests**: < 10 seconds
- **Full Suite**: < 30 seconds
- **With Coverage**: < 45 seconds

The test suite is optimized for fast feedback during development.
