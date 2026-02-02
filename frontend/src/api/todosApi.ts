export interface Todo {
    id: string;
    user_email: string;
    text: string;
    completed: boolean;
    due_date?: string;
    created_at?: string;
}

export async function fetchTodos(user_email: string): Promise<Todo[]> {
    const res = await fetch(`http://localhost:8000/todos/${user_email}`);
    if (!res.ok) {
        throw new Error(`Failed to fetch todos: ${res.status}`);
    }
    return res.json();
}

export async function addTodo(todo: { user_email: string; text: string; due_date?: string }): Promise<Todo> {
    const res = await fetch(`http://localhost:8000/todos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(todo),
    });
    if (!res.ok) {
        const errorText = await res.text();
        console.error('Server error:', errorText);
        throw new Error(`Failed to add todo: ${res.status}`);
    }
    return res.json();
}

export async function updateTodo(todoId: string, updates: { text?: string; completed?: boolean; due_date?: string }): Promise<Todo> {
    const res = await fetch(`http://localhost:8000/todos/${todoId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
    });
    if (!res.ok) {
        throw new Error(`Failed to update todo: ${res.status}`);
    }
    return res.json();
}

export async function deleteTodo(todoId: string): Promise<void> {
    const res = await fetch(`http://localhost:8000/todos/${todoId}`, {
        method: 'DELETE',
    });
    if (!res.ok) {
        throw new Error(`Failed to delete todo: ${res.status}`);
    }
}
