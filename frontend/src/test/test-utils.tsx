import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a custom render function that includes providers
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  const testQueryClient = createTestQueryClient()
  
  return (
    <QueryClientProvider client={testQueryClient}>
      {children}
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock API responses
export const mockApiResponse = {
  success: {
    data: [
      {
        market: 'ETH-USD',
        dexRates: [
          { dex: 'GMX', rate: 45.2 },
          { dex: 'dYdX', rate: -12.8 },
          { dex: 'Hyperliquid', rate: 78.5 },
          { dex: 'Vertex', rate: -23.1 }
        ],
        volume24h: 125000000,
        openInterest: 890000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      },
      {
        market: 'BTC-USD',
        dexRates: [
          { dex: 'GMX', rate: 23.7 },
          { dex: 'dYdX', rate: 18.9 },
          { dex: 'Hyperliquid', rate: -45.6 },
          { dex: 'Vertex', rate: 67.8 }
        ],
        volume24h: 89000000,
        openInterest: 1200000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      }
    ],
    lastUpdate: '2024-01-15T10:30:00Z',
    totalMarkets: 2
  },
  error: {
    status: 500,
    statusText: 'Internal Server Error'
  }
}

// Helper function to create mock fetch responses
export const mockFetch = (response: any, ok = true, status = 200) => {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    json: async () => response,
  })
}

// Helper function to create mock fetch error
export const mockFetchError = (error = 'Network error') => {
  return vi.fn().mockRejectedValue(new Error(error))
}

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }