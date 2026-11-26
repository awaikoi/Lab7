
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('feedbackForm');

    if (!form) return;

    form.addEventListener('submit', async event => {
        event.preventDefault();

        const fields = form.elements;

        const name = fields.name.value.trim();
        const email = fields.email.value.trim();
        const message = fields.message.value.trim();

        document.querySelectorAll('[data-error]').forEach(node => {
            node.textContent = '';
        });

        let valid = true;

        if (!name || name.length > 100) {
            document.querySelector('[data-error="name"]').textContent =
                'Вкажіть ім’я (до 100 символів)';

            valid = false;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            document.querySelector('[data-error="email"]').textContent =
                'Некоректний email';

            valid = false;
        }

        if (!message || message.length > 2000) {
            document.querySelector('[data-error="message"]').textContent =
                'Повідомлення має містити до 2000 символів';

            valid = false;
        }

        if (!valid) return;

        const button = form.querySelector('[type="submit"]');

        button.disabled = true;

        try {
            await apiFetch('/api/v1/feedback', {
                method: 'POST',
                body: { name, email, message }
            });

            form.reset();

            showToast(
                'Дякуємо за ваш відгук!',
                'success'
            );

        } catch (error) {
            const details = error.details || {};

            ['name', 'email', 'message'].forEach(field => {
                if (details[field]) {
                    document.querySelector(
                        `[data-error="${field}"]`
                    ).textContent = details[field];
                }
            });

            showToast(error.message, 'error');

        } finally {
            button.disabled = false;
        }
    });
});
