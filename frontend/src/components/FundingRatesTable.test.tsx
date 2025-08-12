import { describe, it, expect } from 'vitest'
import { render, screen } from '../test/test-utils'
import { FundingRatesTable } from './FundingRatesTable'
import { FundingRateData } from '../data/mockFundingData'

const mockData: FundingRateData[] = [
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
]

describe('FundingRatesTable', () => {
  it('should render table title correctly', () => {
    render(<FundingRatesTable data={mockData} />)
    
    expect(screen.getByText(/Funding Rates Comparison/)).toBeInTheDocument()
  })

  it('should render all markets', () => {
    render(<FundingRatesTable data={mockData} />)
    
    expect(screen.getAllByText('ETH-USD')).toHaveLength(2) // Desktop + Mobile view
    expect(screen.getAllByText('BTC-USD')).toHaveLength(2) // Desktop + Mobile view
  })

  it('should display DEX names in the table', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // Check that DEX names appear (each appears multiple times across desktop and mobile views)
    expect(screen.getAllByText(/GMX/)).toHaveLength(4) // 2 markets × 2 views
    expect(screen.getAllByText(/dYdX/)).toHaveLength(4)
    expect(screen.getAllByText(/Hyperliquid/).length).toBeGreaterThanOrEqual(4)
    expect(screen.getAllByText(/Vertex/).length).toBeGreaterThanOrEqual(4)
  })

  it('should display rate values', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // Check that specific rate values appear (they appear in both desktop and mobile)
    expect(screen.getAllByText('+45.2')).toHaveLength(2)
    expect(screen.getAllByText('-12.8')).toHaveLength(2)
    expect(screen.getAllByText('+78.5')).toHaveLength(2)
  })

  it('should calculate and display max spread correctly', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // ETH-USD: max spread should be between Hyperliquid (78.5) and Vertex (-23.1) = 101.6
    expect(screen.getAllByText('101.6')).toHaveLength(2) // Desktop + Mobile
    
    // BTC-USD: max spread should be between Vertex (67.8) and Hyperliquid (-45.6) = 113.4
    expect(screen.getAllByText('113.4')).toHaveLength(2) // Desktop + Mobile
  })

  it('should display spread unit as bps', () => {
    render(<FundingRatesTable data={mockData} />)
    
    const bpsElements = screen.getAllByText('bps')
    expect(bpsElements.length).toBeGreaterThan(0)
  })

  it('should show arbitrage pairs with vs separator', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // Check for "vs" text that separates high and low DEX in pairs
    const vsElements = screen.getAllByText('vs')
    expect(vsElements.length).toBe(mockData.length) // One per market in desktop view
  })

  it('should display opportunity indicators', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // Should have opportunity badges for each market
    expect(screen.getAllByText('Best Arbitrage')).toHaveLength(4) // 2 markets × 2 views
  })

  it('should format positive rates with + prefix', () => {
    render(<FundingRatesTable data={mockData} />)
    
    expect(screen.getAllByText('+45.2')).toHaveLength(2)
    expect(screen.getAllByText('+23.7')).toHaveLength(2)
    expect(screen.getAllByText('+78.5')).toHaveLength(2)
  })

  it('should format negative rates without + prefix', () => {
    render(<FundingRatesTable data={mockData} />)
    
    expect(screen.getAllByText('-12.8')).toHaveLength(2)
    expect(screen.getAllByText('-23.1')).toHaveLength(2)
    expect(screen.getAllByText('-45.6')).toHaveLength(2)
  })

  it('should handle empty data gracefully', () => {
    render(<FundingRatesTable data={[]} />)
    
    // Should still render the table structure
    expect(screen.getByText(/Funding Rates Comparison/)).toBeInTheDocument()
  })

  it('should handle single DEX data', () => {
    const singleDexData: FundingRateData[] = [
      {
        market: 'TEST-USD',
        dexRates: [{ dex: 'GMX', rate: 45.2 }],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      }
    ]
    
    render(<FundingRatesTable data={singleDexData} />)
    
    expect(screen.getAllByText('TEST-USD')).toHaveLength(2) // Desktop + Mobile
    expect(screen.getAllByText(/GMX/)).toHaveLength(2) // Desktop "GMX:" and Mobile "GMX"
    // Max spread should be 0 for single DEX
    expect(screen.getAllByText('0.0')).toHaveLength(2) // Desktop + Mobile
  })

  it('should display trending icons for rates', () => {
    const { container } = render(<FundingRatesTable data={mockData} />)
    
    // Check that trending icons are rendered (they are SVG elements)
    const svgElements = container.querySelectorAll('svg')
    expect(svgElements.length).toBeGreaterThan(0)
  })

  it('should show different opportunity types correctly', () => {
    const mixedData: FundingRateData[] = [
      {
        market: 'ARBITRAGE-USD',
        dexRates: [
          { dex: 'GMX', rate: 100.0 },
          { dex: 'dYdX', rate: -50.0 }
        ],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      },
      {
        market: 'HIGH-SPREAD-USD',
        dexRates: [
          { dex: 'GMX', rate: 200.0 },
          { dex: 'dYdX', rate: 50.0 }
        ],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      },
      {
        market: 'LOW-SPREAD-USD',
        dexRates: [
          { dex: 'GMX', rate: 50.0 },
          { dex: 'dYdX', rate: 40.0 }
        ],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      }
    ]
    
    render(<FundingRatesTable data={mixedData} />)
    
    expect(screen.getAllByText('Best Arbitrage')).toHaveLength(2) // Desktop + Mobile
    expect(screen.getAllByText('High Spread')).toHaveLength(2) // Desktop + Mobile
    expect(screen.getAllByText('Low Spread')).toHaveLength(2) // Desktop + Mobile
  })

  it('should handle zero rates correctly', () => {
    const zeroRateData: FundingRateData[] = [
      {
        market: 'ZERO-USD',
        dexRates: [
          { dex: 'GMX', rate: 0.0 },
          { dex: 'dYdX', rate: 25.0 }
        ],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      }
    ]
    
    render(<FundingRatesTable data={zeroRateData} />)
    
    // For zero rate, it appears as "0.0" (without plus sign in desktop view) and "+0.0" in mobile
    expect(screen.getAllByText(/0\.0/)).toHaveLength(4) // Both 0.0 and +0.0 formats, plus spread value
    expect(screen.getAllByText('+25.0')).toHaveLength(2)
  })

  it('should round spread values to 1 decimal place', () => {
    const precisionData: FundingRateData[] = [
      {
        market: 'PRECISION-USD',
        dexRates: [
          { dex: 'GMX', rate: 45.123 },
          { dex: 'dYdX', rate: -12.456 }
        ],
        volume24h: 1000000,
        openInterest: 5000000,
        lastUpdate: '2024-01-15T10:30:00Z'
      }
    ]
    
    render(<FundingRatesTable data={precisionData} />)
    
    // Max spread should be 57.579, rounded to 57.6
    expect(screen.getAllByText('57.6')).toHaveLength(2)
  })

  it('should render responsive design elements', () => {
    const { container } = render(<FundingRatesTable data={mockData} />)
    
    // Check for responsive classes (desktop table and mobile cards)
    const desktopTable = container.querySelector('.hidden')
    const mobileCards = container.querySelector('.lg\\:hidden')
    
    expect(desktopTable).toBeInTheDocument()
    expect(mobileCards).toBeInTheDocument()
  })

  it('should display market names in mobile view', () => {
    render(<FundingRatesTable data={mockData} />)
    
    // In mobile view, markets should be displayed as card headers
    expect(screen.getAllByText('ETH-USD').length).toBeGreaterThanOrEqual(2) 
    expect(screen.getAllByText('BTC-USD').length).toBeGreaterThanOrEqual(2)
  })
})