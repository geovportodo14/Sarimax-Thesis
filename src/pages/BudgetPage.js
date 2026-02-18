import React, { useState } from 'react';
import { useDashboard } from '../context/DashboardContext';
import DashboardHeader from '../components/DashboardHeader';
import DateNavigator from '../components/DateNavigator';
import RangeSlider from '../features/budget/RangeSlider';
import BudgetStatusCard from '../features/budget/BudgetStatusCard';
import BudgetRangeRecommendationCard from '../features/budget/BudgetRangeRecommendationCard';
import LockedBudgetCard from '../features/dashboard/LockedBudgetCard';
import { Card, CardBody } from '../components/ui';

export default function BudgetPage() {
    const {
        budget, setBudget, // Context budget is single value, adapt here
        currentDate, setCurrentDate,
        handlePrevDate, handleNextDate,
        budgetUnlocked, baselineDays,
        dummyData
    } = useDashboard();

    // Local state for range (since context only has 'budget' which is max cap)
    const [minBudget, setMinBudget] = useState(budget * 0.8);
    const [maxBudget, setMaxBudget] = useState(budget);

    // Mock current cost based on dummy data or random
    const currentCost = dummyData?.sampleData?.['24hours']?.actualTotal
        ? dummyData.sampleData['24hours'].actualTotal.reduce((a, b) => a + b, 0) * 13.47
        : 150.00; // Mock default

    // Sync back to context when max changes
    const handleMaxChange = (val) => {
        setMaxBudget(val);
        setBudget(val);
    };

    return (
        <div className="min-h-screen bg-surface-50">
            <DashboardHeader
                notifications={[]}
                settings={{}}
                onSaveSettings={() => { }}
            />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-display-sm text-surface-900">Budget Management</h1>
                    <DateNavigator
                        selectedDate={currentDate}
                        onDateChange={setCurrentDate}
                        onPrevClick={handlePrevDate}
                        onNextClick={handleNextDate}
                    />
                </div>

                {!budgetUnlocked ? (
                    <div className="max-w-2xl mx-auto mt-12">
                        <LockedBudgetCard daysLeft={30 - baselineDays} />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div>
                            <BudgetRangeRecommendationCard
                                recommendedMin={250}
                                recommendedMax={350}
                            />
                            <RangeSlider
                                minValue={minBudget}
                                maxValue={maxBudget}
                                onChangeMin={setMinBudget}
                                onChangeMax={handleMaxChange}
                            />
                        </div>

                        <div>
                            <BudgetStatusCard
                                currentCost={currentCost}
                                minBudget={minBudget}
                                maxBudget={maxBudget}
                            />

                            <Card className="mt-6">
                                <CardBody>
                                    <h3 className="text-lg font-bold text-surface-900 mb-2">Tips</h3>
                                    <ul className="list-disc list-inside text-sm text-surface-600 space-y-2">
                                        <li>Adjust your AC temperature by 1°C to save ~3%.</li>
                                        <li>Unplug unused devices to reduce phantom load.</li>
                                        <li>Use "Eco Mode" on your washing machine.</li>
                                    </ul>
                                </CardBody>
                            </Card>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
