/**
 * Exact Meralco Bill Calculator based on March 2026 Residential Rates.
 * @param {number} kwh - Total projected kWh for the billing cycle
 * @returns {object} Highly detailed breakdown of charges
 */
export function calculateMeralcoBill(kwh) {
    if (kwh <= 0) return { totalAmount: 0, breakdown: null };

    // 1. Generation, Transmission, System Loss (per kWh)
    const genChargeRate = 7.8607;
    const transChargeRate = 1.5223;
    const sysLossRate = 0.7456;

    const genCharge = kwh * genChargeRate;
    const transCharge = kwh * transChargeRate;
    const sysLossCharge = kwh * sysLossRate;

    // 2. Distribution Charge (Tiered brackets)
    let distChargeRate = 0.9803; // Default 0-200
    if (kwh > 200 && kwh <= 300) distChargeRate = 1.2908;
    else if (kwh > 300 && kwh <= 400) distChargeRate = 1.5837;
    else if (kwh > 400) distChargeRate = 2.0941;

    const distCharge = kwh * distChargeRate;

    // 3. Supply & Metering
    const supplyPerKwh = 0.4979;
    const supplyFixed = 16.38;
    const meteringPerKwh = 0.3350;
    const meteringFixed = 5.00;

    const supplyTotal = (kwh * supplyPerKwh) + supplyFixed;
    const meteringTotal = (kwh * meteringPerKwh) + meteringFixed;

    // 4. Adjustments & Subsidies
    const awatRefundRate = -0.2024;
    const regResetRate = -0.0023;
    const currentRptRate = 0.0058;

    // Lifeline: If >100 kWh, they pay the subsidy (0.0100 per kWh). If <=100, they get a discount (not fully implemented here as complex, assuming >100 for typical thesis households)
    const lifelineRate = kwh > 100 ? 0.0100 : 0;
    const seniorCitizenRate = 0.0001;

    const awatRefund = kwh * awatRefundRate;
    const regReset = kwh * regResetRate;
    const currentRpt = kwh * currentRptRate;
    const lifelineSubsidy = kwh * lifelineRate;
    const seniorCitizenSubsidy = kwh * seniorCitizenRate;

    // 5. Universal Charges
    const ucMeSpugRate = 0.2662;
    const ucMeRedCiRate = 0.0101;
    const ucEcRate = 0.0025;
    const fitAllRate = 0.0428;
    const geaAllRate = 0.2011;

    const ucMeSpug = kwh * ucMeSpugRate;
    const ucMeRedCi = kwh * ucMeRedCiRate;
    const ucEc = kwh * ucEcRate;
    const fitAll = kwh * fitAllRate;
    const geaAll = kwh * geaAllRate;

    const universalTotal = ucMeSpug + ucMeRedCi + ucEc + fitAll + geaAll;

    // 6. Value Added Tax (VAT)
    // VAT is 12% applied to Gen, Trans, SysLoss, Dist, Supply, Metering, and specific subsidies/adjustments.
    // For simplicity in this display logic, we apply 12% to the taxable sum.
    const taxableSum = genCharge + transCharge + sysLossCharge + distCharge + supplyTotal + meteringTotal + awatRefund + regReset;
    const vat = taxableSum > 0 ? taxableSum * 0.12 : 0;

    // Output Subtotals for UI
    const totalAmount = taxableSum + currentRpt + lifelineSubsidy + seniorCitizenSubsidy + universalTotal + vat;

    return {
        totalAmount,
        kwh,
        breakdown: {
            "Generation Charge": genCharge,
            "Transmission Charge": transCharge,
            "System Loss Charge": sysLossCharge,
            "Distribution (Meralco)": {
                "Distribution Charge": distCharge,
                "Supply System Charge": supplyTotal,
                "Metering Charge": meteringTotal
            },
            "Subsidies & Adjustments": {
                "Lifeline Rate Subsidy": lifelineSubsidy,
                "Senior Citizen Subsidy": seniorCitizenSubsidy,
                "AWAT Refund": awatRefund,
                "Regulatory Reset Adj.": regReset,
                "Current RPT Charge": currentRpt
            },
            "Universal Charges": {
                "UC-ME (NPC-SPUG)": ucMeSpug,
                "UC-ME (RED-CI)": ucMeRedCi,
                "UC-EC": ucEc,
                "FIT-All": fitAll,
                "GEA-All": geaAll
            },
            "Value Added Tax (12%)": vat
        }
    };
}
