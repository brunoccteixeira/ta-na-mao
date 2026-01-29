import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('renders the dashboard', () => {
    render(<App />);
    // Check if main heading is present
    const heading = screen.getByText(/Dashboard de Benefícios/i);
    expect(heading).toBeInTheDocument();
  });
});






