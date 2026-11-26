
document.addEventListener('DOMContentLoaded', () => {
    const orders = document.getElementById('orders');
    const feedback = document.getElementById('feedbackList');

    const filter = document.getElementById('statusFilter');
    const statistics = document.getElementById('statistics');

    function makeStatusBadge(status) {
        const badge = document.createElement('span');

        const colors = {
            'Нове': 'bg-sky-100 text-sky-800',
            'В обробці': 'bg-amber-100 text-amber-800',
            'Відправлено': 'bg-violet-100 text-violet-800',
            'Доставлено': 'bg-emerald-100 text-emerald-800',
            'Скасовано': 'bg-red-100 text-red-800'
        };

        badge.textContent = status;

        badge.className =
        `inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${
            colors[status] || 'bg-gray-100 text-gray-800'
        }`;

        return badge;
    }

    function updateStatistics(orderCount, feedbackCount) {
        statistics.replaceChildren();

        [
            ['Замовлень', orderCount],
            ['Відгуків', feedbackCount]
        ].forEach(([label, count]) => {
            const card = document.createElement('div');

            card.className =
            'rounded-2xl border border-line bg-surface p-5 shadow-[var(--shadow-sm)]';

            const title = document.createElement('p');
            title.textContent = label;
            title.className = 'text-sm text-ink/55';

            const value = document.createElement('p');
            value.textContent = count;
            value.className = 'mt-2 text-3xl font-bold tracking-tight';

            card.append(title, value);
            statistics.append(card);
        });
    }

    async function loadOrders() {
        const query = filter.value
        ? `?status=${encodeURIComponent(filter.value)}`
        : '';

        const data = await apiFetch(
            `/api/v1/orders${query}`
        );

        orders.replaceChildren();

        if (!data.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');

            cell.colSpan = 6;
            cell.textContent = 'Замовлень не знайдено.';
            cell.className = 'px-4 py-10 text-center text-ink/55';

            row.append(cell);
            orders.append(row);
        }

        data.forEach(order => {
            const row = document.createElement('tr');

            row.className = 'border-b border-line last:border-0';

            const values = [
                order.id,
                order.email,
                `${order.total_price} грн`,
                null,
                order.date
            ];

            values.forEach((value, index) => {
                const cell = document.createElement('td');

                cell.className = 'px-4 py-3.5';

                if (index === 3) {
                    cell.append(makeStatusBadge(order.status));
                } else {
                    cell.textContent = value;
                }

                row.append(cell);
            });

            const actions = document.createElement('td');
            actions.className = 'px-4 py-3.5';

            const details = document.createElement('a');

            details.href = `/admin/order/${order.id}`;
            details.textContent = 'Деталі';
            details.className = 'mr-3 rounded-lg border border-line px-3 py-1.5 text-xs font-bold text-accent transition hover:bg-[#fff7f9]';

            const remove = document.createElement('button');

            remove.textContent = 'Видалити';
            remove.className = 'rounded-lg border border-red-200 px-3 py-1.5 text-xs font-bold text-red-700 transition hover:bg-red-50';

            remove.onclick = async () => {
                if (!confirm(
                    `Видалити замовлення №${order.id}?`
                )) return;

                try {
                    await apiFetch(
                        `/api/v1/orders/${order.id}`,
                        { method: 'DELETE' }
                    );

                    row.remove();

                    await refreshStatistics();

                    showToast(
                        'Замовлення видалено',
                        'success'
                    );

                } catch (error) {
                    if (error.status === 404) {
                        row.remove();
                        await refreshStatistics();
                    } else {
                        showToast(error.message, 'error');
                    }
                }
            };

            actions.append(details, remove);
            row.append(actions);

            orders.append(row);
        });
    }

    async function loadFeedback() {
        const data = await apiFetch('/api/v1/feedback');

        feedback.replaceChildren();

        if (!data.length) {
            const empty = document.createElement('p');
            empty.textContent = 'Відгуків поки немає.';
            empty.className =
                'rounded-2xl border border-dashed border-line bg-surface/50 px-5 py-10 text-center text-sm text-ink/55 lg:col-span-2';
            feedback.append(empty);
        }

        data.forEach(item => {
            const card = document.createElement('article');

            card.className =
            'rounded-2xl border border-line bg-surface p-5 shadow-[var(--shadow-sm)]';

            const name = document.createElement('h3');

            name.textContent = item.name;
            name.className = 'font-bold';

            const email = document.createElement('p');

            email.textContent = item.email;
            email.className = 'mt-1 text-sm text-accent';

            const message = document.createElement('p');

            message.textContent = item.message;
            message.className = 'my-4 whitespace-pre-wrap leading-6 text-ink/80';

            const date = document.createElement('p');

            date.textContent = item.created_at;
            date.className = 'text-xs text-ink/60';

            const remove = document.createElement('button');

            remove.textContent = 'Видалити';
            remove.className = 'mt-4 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-bold text-red-700 transition hover:bg-red-50';

            remove.onclick = async () => {
                if (!confirm('Видалити відгук?')) return;

                try {
                    await apiFetch(
                        `/api/v1/feedback/${item.id}`,
                        { method: 'DELETE' }
                    );

                    card.remove();

                    await refreshStatistics();

                } catch (error) {
                    if (error.status === 404) {
                        card.remove();
                        await refreshStatistics();
                    } else {
                        showToast(error.message, 'error');
                    }
                }
            };

            card.append(
                name,
                email,
                message,
                date,
                remove
            );

            feedback.append(card);
        });
    }

    async function refreshStatistics() {
        const results = await Promise.allSettled([
            apiFetch('/api/v1/orders'),
                                                 apiFetch('/api/v1/feedback')
        ]);

        updateStatistics(
            results[0].status === 'fulfilled'
            ? results[0].value.length
            : '—',

            results[1].status === 'fulfilled'
            ? results[1].value.length
            : '—'
        );
    }

    function renderError(container, error, retry) {
        container.replaceChildren();

        const message = document.createElement('p');
        message.textContent = error.message;
        message.className = 'text-sm text-red-700';

        const button = document.createElement('button');

        button.textContent = 'Повторити';
        button.className = 'ml-3 underline text-accent';

        button.onclick = retry;

        container.append(message, button);
    }

    async function initialize() {
        const results = await Promise.allSettled([
            loadOrders(),
                                                 loadFeedback()
        ]);

        if (results[0].status === 'rejected') {
            renderError(
                orders,
                results[0].reason,
                loadOrders
            );
        }

        if (results[1].status === 'rejected') {
            renderError(
                feedback,
                results[1].reason,
                loadFeedback
            );
        }

        await refreshStatistics();
    }

    filter.addEventListener('change', () => {
        loadOrders().catch(error => {
            renderError(orders, error, loadOrders);
        });
    });

    initialize();
});
