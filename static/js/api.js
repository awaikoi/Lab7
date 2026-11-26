async function apiFetch(url, options = {}) {
    const { body, headers = {}, ...rest } = options;

    const config = {
        ...rest,
        headers: { ...headers }
    };

    if (body instanceof FormData) {
        config.body = body;
    } else if (body !== undefined) {
        config.headers['Content-Type'] = 'application/json';
        config.body = JSON.stringify(body);
    }

    let response;

    try {
        response = await fetch(url, config);
    } catch {
        const error = new Error(
            'Не вдалося з’єднатися із сервером.'
        );

        error.network = true;
        throw error;
    }

    if (response.status === 204) {
        return null;
    }

    const contentType =
        response.headers.get('Content-Type') || '';

    const data = contentType.includes('application/json')
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        const error = new Error(
            data?.error?.message ||
            data?.message ||
            `HTTP ${response.status}`
        );

        error.status = response.status;
        error.details = data?.error?.details || {};

        throw error;
    }

    return data;
}
