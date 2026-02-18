// =============================================================================
// CORE DATA MODELS — Scenario Simulator Energy Monitoring App
// =============================================================================

// ─── Device & Verification ──────────────────────────────────
export type ApplianceProfile =
    | 'refrigerator'
    | 'air_conditioner'
    | 'washing_machine'
    | 'electric_fan'
    | 'water_heater'
    | 'other';

export interface VerificationStatus {
    state: 'unverified' | 'verifying' | 'verified' | 'failed';
    verifiedAt?: Date;
    method?: string; // e.g., "door_open_spike"
    // future: lastCalibrationDate, confidenceScore
}

export interface Device {
    id: string;
    name: string; // User-given name (e.g., "Kitchen Fridge")
    profile: ApplianceProfile;
    verificationStatus: VerificationStatus;
    pairedAt: Date;
    // future: firmwareVersion, connectionType
}

// ─── Usage & Cost ───────────────────────────────────────────
export interface Reading {
    deviceId: string;
    timestamp: Date;
    kWh: number;
    // future: voltage, current, powerFactor
}

export interface DailySummary {
    deviceId: string;
    date: string; // "YYYY-MM-DD"
    totalKwh: number;
    totalCost: number;
    peakKw: number;
    // future: avgTemperature, runHours
}

export interface TariffRate {
    id: string;
    ratePerKwh: number; // e.g., 13.47 PHP
    currency: string; // "PHP"
    effectiveFrom: Date;
    // future: tieredRates, timeOfUse
}

// ─── Forecast ───────────────────────────────────────────────
export interface ForecastPoint {
    timestamp: Date;
    predictedKwh: number;
    // future: lowerBound, upperBound
}

export interface ForecastResult {
    deviceId: string;
    generatedAt: Date;
    horizon: '6h' | '12h' | '24h';
    predictions: ForecastPoint[];
    // future: modelVersion, confidenceInterval
}

// ─── Budget ─────────────────────────────────────────────────
export interface BudgetRange {
    id: string;
    deviceId: string;
    minKwh: number; // System-suggested lower bound
    maxKwh: number; // System-suggested upper bound
    userAdjustedMin?: number;
    userAdjustedMax?: number;
    period: 'daily' | 'weekly' | 'monthly';
    // future: seasonalAdjustment
}

export type BudgetStatus = 'within_range' | 'approaching_limit' | 'exceeded';

// ─── Scenario ───────────────────────────────────────────────
export interface ScenarioAdjustment {
    deviceId: string;
    type: 'usage_change' | 'tariff_change' | 'schedule_change';
    value: number; // Percent change or absolute value
}

export interface ScenarioInput {
    id: string;
    name: string;
    templateId?: string;
    adjustments: ScenarioAdjustment[];
    // future: scheduledActions
}

export interface ScenarioResult {
    scenarioId: string;
    projectedKwh: number;
    projectedCost: number;
    deltaKwh: number;
    deltaCost: number;
    projectedMonthEnd: number;
    // future: impactBreakdownByDevice
}

// ─── App State ──────────────────────────────────────────────
export type AppPhase = 'no_data' | 'learning' | 'active';

export interface AppState {
    onboardingComplete: boolean;
    appPhase: AppPhase;
    baselineDaysCollected: number;
    budgetUnlocked: boolean; // Derived: baselineDaysCollected >= 30
}
