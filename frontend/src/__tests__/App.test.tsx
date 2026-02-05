import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Home from '../views/Home';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('Home', () => {
  it('renders the homepage heading', () => {
    renderWithProviders(<Home />);
    const heading = screen.getByText(/Descubra seus direitos/i);
    expect(heading).toBeInTheDocument();
  });

  it('shows the social proof section', () => {
    renderWithProviders(<Home />);
    // The redesigned Home has a stats section with data sources
    const section = screen.getByText(/Dados oficiais de:/i);
    expect(section).toBeInTheDocument();
  });
});
