// api/supervisorAgentApi.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function simulateFatigue(fatigueLevel: number): Promise<any> {
    const res = await fetch(`${API_URL}/supervisor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fatigue_level: fatigueLevel }),
    });
    return res.json();
}
