// chat api - supports multiple agents

export type AgentType = 'wellness' | 'productivity' | 'supervisor';

export async function sendChatMessage(
    message: string,
    port: string = '8000',
    agent: AgentType = 'supervisor',
    email?: string | null,
    threadId?: string | null
): Promise<any> {
    // each agent has its own endpoint
    const endpoints: Record<AgentType, string> = {
        wellness: '/api/chat/wellness',
        productivity: '/supervisor',  // abhyajit's endpoint
        supervisor: '/supervisor'
    };

    const endpoint = endpoints[agent] || endpoints.wellness;

    const res = await fetch(`http://localhost:${port}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, email, thread_id: threadId })
    });

    if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
    }

    return res.json();
}

export async function saveThread(
    email: string,
    threadId: string,
    messages: { text: string; sender: string; id: number }[],
    title: string = "New Conversation",
    port: string = '8000'
): Promise<any> {
    const res = await fetch(`http://localhost:${port}/api/history/${email}/${threadId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages,
            title
        })
    });

    if (!res.ok) {
        console.error('Failed to save thread');
    }
    return res.json();
}

export async function getThread(
    email: string,
    threadId: string,
    port: string = '8000'
): Promise<any> {
    const res = await fetch(`http://localhost:${port}/api/history/${email}/${threadId}`);
    if (!res.ok) {
        throw new Error('Thread not found');
    }
    return res.json();
}
