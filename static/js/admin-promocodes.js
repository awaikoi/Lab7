
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('promocodeForm');
    const list = document.getElementById('promocodes');

    async function loadPromocodes() {
        const rows = await apiFetch('/api/v1/promocodes');

        list.replaceChildren();

        if (!rows.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 6;
            cell.textContent = 'Промокодів поки немає.';
            cell.className = 'px-4 py-10 text-center text-ink/55';
            row.append(cell);
            list.append(row);
        }

        rows.forEach(promo => {
            const row = document.createElement('tr');
            row.className = 'border-b border-line last:border-0';

            const code = document.createElement('td');
            code.textContent = promo.code;
            code.className = 'px-4 py-3 font-bold';
            row.append(code);

            const discount = document.createElement('td');
            discount.textContent = promo.discount_percent > 0
                ? `${promo.discount_percent}%`
                : `${promo.discount_amount} грн`;
            discount.className = 'px-4 py-3';
            row.append(discount);

            [promo.min_order, promo.expires_at || 'Безстроково'].forEach(value => {
                const cell = document.createElement('td');
                cell.textContent = value;
                cell.className = 'px-4 py-3';
                row.append(cell);
            });

            const active = document.createElement('td');
            const badge = document.createElement('span');
            badge.textContent = promo.active ? 'Так' : 'Ні';
            badge.className = promo.active
                ? 'rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-bold text-emerald-800'
                : 'rounded-full bg-gray-100 px-2.5 py-1 text-xs font-bold text-gray-600';
            active.className = 'px-4 py-3';
            active.append(badge);
            row.append(active);

            const actions = document.createElement('td');
            actions.className = 'px-4 py-3';
            const button = document.createElement('button');

            button.textContent = 'Видалити';
            button.className =
                'rounded-lg border border-red-200 px-3 py-1.5 text-sm font-semibold text-red-700 transition hover:bg-red-50';

            button.onclick = async () => {
                if (!confirm('Видалити промокод?')) return;

                try {
                    await apiFetch(
                        `/api/v1/promocodes/${promo.id}`,
                        { method: 'DELETE' }
                    );

                    row.remove();
                    if (!list.children.length) {
                        await loadPromocodes();
                    }

                    showToast('Промокод видалено', 'success');

                } catch (error) {
                    showToast(error.message, 'error');
                }
            };

            actions.append(button);
            row.append(actions);

            list.append(row);
        });
    }

    form.addEventListener('submit', async event => {
        event.preventDefault();

        const fields = form.elements;

        const code = fields.code.value.trim();
        const percent = Number(fields.discount_percent.value || 0);
        const amount = Number(fields.discount_amount.value || 0);
        const minimum = Number(fields.min_order.value || 0);
        const date = fields.expires_at.value || null;

        if (!code || code.length > 50) {
            showToast('Перевірте код промокоду', 'error');
            return;
        }

        if (percent < 0 || percent > 100 ||
            amount < 0 || minimum < 0 ||
            (percent === 0 && amount === 0)) {
            showToast('Перевірте розмір знижки', 'error');
            return;
        }

        const button = form.querySelector('[type="submit"]');
        button.disabled = true;

        try {
            await apiFetch('/api/v1/promocodes', {
                method: 'POST',
                body: {
                    code,
                    discount_percent: percent,
                    discount_amount: amount,
                    min_order: minimum,
                    active: fields.active.checked,
                    expires_at: date
                }
            });

            form.reset();

            showToast('Промокод створено', 'success');

            await loadPromocodes();

        } catch (error) {
            if (error.status === 409) {
                showToast('Такий промокод вже існує', 'error');
            } else {
                showToast(error.message, 'error');
            }
        } finally {
            button.disabled = false;
        }
    });

    loadPromocodes().catch(error => {
        showToast(error.message, 'error');
    });
});
