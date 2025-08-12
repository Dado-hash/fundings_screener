import { describe, it, expect } from 'vitest'
import { calculateMaxSpread, getOpportunityType } from './spreadCalculator'
import { DexFundingRate } from '../data/mockFundingData'

describe('calculateMaxSpread', () => {
  it('should return zero spread for empty array', () => {
    const result = calculateMaxSpread([])
    
    expect(result).toEqual({
      spread: 0,
      highDex: '',
      lowDex: '',
      highRate: 0,
      lowRate: 0
    })
  })

  it('should return zero spread for single DEX', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 45.2 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result).toEqual({
      spread: 0,
      highDex: '',
      lowDex: '',
      highRate: 0,
      lowRate: 0
    })
  })

  it('should calculate spread between two DEXs correctly', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 45.2 },
      { dex: 'dYdX', rate: -12.8 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result).toEqual({
      spread: 58.0, // Math.abs(45.2 - (-12.8))
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 45.2,
      lowRate: -12.8
    })
  })

  it('should find maximum spread among multiple DEXs', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 45.2 },
      { dex: 'dYdX', rate: -12.8 },
      { dex: 'Hyperliquid', rate: 78.5 },
      { dex: 'Vertex', rate: -23.1 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBeCloseTo(101.6) // 78.5 - (-23.1)
    expect(result.highDex).toBe('Hyperliquid')
    expect(result.lowDex).toBe('Vertex')
    expect(result.highRate).toBe(78.5)
    expect(result.lowRate).toBe(-23.1)
  })

  it('should handle all positive rates', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 10.0 },
      { dex: 'dYdX', rate: 50.0 },
      { dex: 'Hyperliquid', rate: 25.0 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBe(40.0) // 50.0 - 10.0
    expect(result.highDex).toBe('dYdX')
    expect(result.lowDex).toBe('GMX')
    expect(result.highRate).toBe(50.0)
    expect(result.lowRate).toBe(10.0)
  })

  it('should handle all negative rates', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: -10.0 },
      { dex: 'dYdX', rate: -50.0 },
      { dex: 'Hyperliquid', rate: -25.0 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBe(40.0) // Math.abs(-10.0 - (-50.0))
    expect(result.highDex).toBe('GMX')
    expect(result.lowDex).toBe('dYdX')
    expect(result.highRate).toBe(-10.0)
    expect(result.lowRate).toBe(-50.0)
  })

  it('should handle identical rates', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 25.0 },
      { dex: 'dYdX', rate: 25.0 },
      { dex: 'Hyperliquid', rate: 25.0 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBe(0.0)
    // When spread is 0, the function returns initial values (0) for high/low rates
    expect(result.highRate).toBe(0)
    expect(result.lowRate).toBe(0)
  })

  it('should handle zero rates', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 0.0 },
      { dex: 'dYdX', rate: 45.2 },
      { dex: 'Hyperliquid', rate: -23.1 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBeCloseTo(68.3) // 45.2 - (-23.1)
    expect(result.highDex).toBe('dYdX')
    expect(result.lowDex).toBe('Hyperliquid')
  })

  it('should handle very large numbers', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 1000000.0 },
      { dex: 'dYdX', rate: -1000000.0 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBe(2000000.0)
    expect(result.highDex).toBe('GMX')
    expect(result.lowDex).toBe('dYdX')
  })

  it('should handle decimal precision correctly', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'GMX', rate: 45.123 },
      { dex: 'dYdX', rate: -12.456 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBeCloseTo(57.579)
    expect(result.highRate).toBe(45.123)
    expect(result.lowRate).toBe(-12.456)
  })
})

describe('getOpportunityType', () => {
  it('should return "arbitrage" for opposite signs with significant spread', () => {
    const maxSpread = {
      spread: 150.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 100.0,
      lowRate: -50.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('arbitrage')
  })

  it('should return "arbitrage" for negative high rate and positive low rate', () => {
    const maxSpread = {
      spread: 75.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: -25.0,
      lowRate: 50.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('arbitrage')
  })

  it('should return "high-spread" for same positive signs with high spread', () => {
    const maxSpread = {
      spread: 150.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 175.0,
      lowRate: 25.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('high-spread')
  })

  it('should return "high-spread" for same negative signs with high spread', () => {
    const maxSpread = {
      spread: 120.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: -25.0,
      lowRate: -145.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('high-spread')
  })

  it('should return "low-spread" for same signs with low spread', () => {
    const maxSpread = {
      spread: 50.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 75.0,
      lowRate: 25.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('low-spread')
  })

  it('should return "high-spread" for spread exactly at boundary (100)', () => {
    const maxSpread = {
      spread: 100.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 125.0,
      lowRate: 25.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('high-spread')
  })

  it('should return "high-spread" for spread just above boundary (100.1)', () => {
    const maxSpread = {
      spread: 100.1,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 125.1,
      lowRate: 25.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('high-spread')
  })

  it('should return "low-spread" for zero spread', () => {
    const maxSpread = {
      spread: 0.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 25.0,
      lowRate: 25.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('low-spread')
  })

  it('should prioritize arbitrage over high-spread for opposite signs', () => {
    const maxSpread = {
      spread: 200.0, // High spread
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 150.0, // Positive
      lowRate: -50.0   // Negative
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('arbitrage') // Should be arbitrage, not high-spread
  })

  it('should handle edge case with zero rates', () => {
    const maxSpread = {
      spread: 50.0,
      highDex: 'GMX',
      lowDex: 'dYdX',
      highRate: 50.0,
      lowRate: 0.0
    }
    
    const result = getOpportunityType(maxSpread)
    
    expect(result).toBe('low-spread')
  })
})

describe('calculateMaxSpread with selectedDexes', () => {
  it('should filter by selected DEXes', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'dYdX', rate: 10.0 },
      { dex: 'Hyperliquid', rate: 50.0 },
      { dex: 'Paradex', rate: 80.0 },
      { dex: 'Extended', rate: 20.0 }
    ]
    
    // Only select dYdX and Paradex
    const selectedDexes = ['dYdX', 'Paradex']
    
    const result = calculateMaxSpread(dexRates, selectedDexes)
    
    // Should calculate spread only between dYdX (10.0) and Paradex (80.0)
    expect(result.spread).toBe(70.0) // 80.0 - 10.0
    expect(result.highDex).toBe('Paradex')
    expect(result.lowDex).toBe('dYdX')
    expect(result.highRate).toBe(80.0)
    expect(result.lowRate).toBe(10.0)
  })

  it('should return zero spread if less than 2 DEXes selected', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'dYdX', rate: 10.0 },
      { dex: 'Hyperliquid', rate: 50.0 },
      { dex: 'Paradex', rate: 80.0 }
    ]
    
    // Only select one DEX
    const selectedDexes = ['dYdX']
    
    const result = calculateMaxSpread(dexRates, selectedDexes)
    
    expect(result.spread).toBe(0)
    expect(result.highDex).toBe('')
    expect(result.lowDex).toBe('')
  })

  it('should work without selectedDexes parameter (backwards compatibility)', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'dYdX', rate: 10.0 },
      { dex: 'Hyperliquid', rate: 50.0 }
    ]
    
    const result = calculateMaxSpread(dexRates)
    
    expect(result.spread).toBe(40.0) // 50.0 - 10.0
    expect(result.highDex).toBe('Hyperliquid')
    expect(result.lowDex).toBe('dYdX')
  })

  it('should filter out non-existing DEXes gracefully', () => {
    const dexRates: DexFundingRate[] = [
      { dex: 'dYdX', rate: 10.0 },
      { dex: 'Hyperliquid', rate: 50.0 }
    ]
    
    // Select a DEX that doesn't exist in the data + one that does
    const selectedDexes = ['dYdX', 'NonExistentDEX']
    
    const result = calculateMaxSpread(dexRates, selectedDexes)
    
    // Should return zero spread because only 1 matching DEX found
    expect(result.spread).toBe(0)
  })
})