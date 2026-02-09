// utils/api.ts
export async function fetchTransactions() {
  const response = await fetch('/transactions');
  if (!response.ok) {
    throw new Error('Failed to fetch transactions');
  }
  return response.json();
}

export async function uploadTransactions(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/transactions/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload transactions');
  }

  return response.json();
}

export async function previewTransactions(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/transactions/preview', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to preview transactions');
  }

  return response.json();
}

export async function confirmUpload(previewId: string, mapping: Record<string, string>) {
  const response = await fetch('/transactions/confirm', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      preview_id: previewId,
      mapping,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to confirm upload');
  }

  return response.json();
}

export async function analyzeTransactions(query: string, conversationId?: string) {
  const response = await fetch('/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      conversation_id: conversationId || undefined,
      debug: false,
    }),
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
}
