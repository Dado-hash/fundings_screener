import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useFundingRates } from './useFundingRates'

// Create wrapper for QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useFundingRates', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    vi.resetAllMocks()
    // Clear all timers
    vi.clearAllTimers()
  })

  it('should start with loading state', () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        data: [],
        lastUpdate: '2024-01-15T10:30:00Z',
        totalMarkets: 0
      }),
    })
    
    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    expect(result.current.loading).toBe(true)
    expect(result.current.data).toEqual([])
    expect(result.current.error).toBeNull()
    expect(result.current.lastUpdate).toBeNull()
  })

  it('should fetch funding rates successfully', async () => {
    const mockResponse = {
      data: [
        {
          market: 'ETH-USD',
          dexRates: [
            { dex: 'GMX', rate: 45.2 },
            { dex: 'dYdX', rate: -12.8 }
          ],
          volume24h: 125000000,
          openInterest: 890000000,
          lastUpdate: '2024-01-15T10:30:00Z'
        }
      ],
      lastUpdate: '2024-01-15T10:30:00Z',
      totalMarkets: 1
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    })

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    // Wait for the fetch to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockResponse.data)
    expect(result.current.lastUpdate).toBe(mockResponse.lastUpdate)
    expect(result.current.error).toBeNull()
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/funding-rates')
  })

  it('should handle API errors gracefully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    })

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual([])
    expect(result.current.error).toBe('HTTP error! status: 500')
    expect(result.current.lastUpdate).toBeNull()
  })

  it('should handle network errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network connection failed'))

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual([])
    expect(result.current.error).toBe('Network connection failed')
    expect(result.current.lastUpdate).toBeNull()
  })

  it('should handle non-Error objects in catch', async () => {
    global.fetch = vi.fn().mockRejectedValue('String error')

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Unknown error occurred')
  })

  it('should use correct API URL based on environment', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        data: [],
        lastUpdate: '2024-01-15T10:30:00Z',
        totalMarkets: 0
      }),
    })

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // In test environment, it should use localhost
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/funding-rates')
  })

  it('should handle empty response data', async () => {
    const emptyResponse = {
      data: [],
      lastUpdate: '2024-01-15T10:30:00Z',
      totalMarkets: 0
    }
    
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    })

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual([])
    expect(result.current.lastUpdate).toBe(emptyResponse.lastUpdate)
    expect(result.current.error).toBeNull()
  })

  it('should handle malformed JSON response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => {
        throw new Error('Invalid JSON')
      },
    })

    const { result } = renderHook(() => useFundingRates(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Invalid JSON')
    expect(result.current.data).toEqual([])
  })
})