# Funding Screener

## Project info

A web application for screening and comparing funding opportunities.

## How can I edit this code?

There are several ways of editing your application.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Testing

This project includes a comprehensive testing framework using Vitest and React Testing Library.

### Running Tests

```bash
# Run tests in watch mode (for development)
npm run test

# Run tests once and exit
npm run test:run

# Run tests with coverage report
npm run test:coverage

# Run tests with UI interface
npm run test:ui
```

### Test Structure

Tests are located alongside their corresponding source files:

- **Unit Tests**: `src/utils/spreadCalculator.test.ts` - Tests for business logic calculations
- **Integration Tests**: `src/hooks/useFundingRates.test.ts` - Tests for API integration hooks
- **Component Tests**: `src/components/FundingRatesTable.test.tsx` - Tests for React components

### Test Coverage

The project maintains high test coverage with thresholds set at 80% for:
- Branches
- Functions
- Lines
- Statements

Coverage reports are generated in the `coverage/` directory when running `npm run test:coverage`.

### Testing Best Practices

1. **Test File Naming**: Test files follow the pattern `*.test.ts` or `*.test.tsx`
2. **Test Organization**: Tests are grouped using `describe` blocks for logical organization
3. **Mocking**: External dependencies like API calls are properly mocked
4. **Assertions**: Clear, descriptive assertions using `expect` statements
5. **Test Data**: Realistic test data that matches production scenarios

### Writing Tests

When adding new features:

1. Create tests alongside your code
2. Test both happy path and edge cases
3. Mock external dependencies appropriately
4. Ensure tests are isolated and don't depend on each other
5. Write descriptive test names that explain what is being tested

Example test structure:
```typescript
describe('ComponentName', () => {
  it('should handle expected behavior', () => {
    // Arrange, Act, Assert
  })
  
  it('should handle edge cases', () => {
    // Test error conditions and edge cases
  })
})
```

## How can I deploy this project?

You can deploy this project using various hosting platforms like Vercel, Netlify, or GitHub Pages.