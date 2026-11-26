
document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('categories');
    const form = document.getElementById('categoryForm');

    const parent = form.elements.parent_id;

    async function loadCategories() {
        const response = await apiFetch(
            '/api/v2/categories'
        );

        root.replaceChildren();

        parent.replaceChildren(
            new Option('Коренева категорія', '')
        );

        if (!response.data.length) {
            root.textContent = 'Категорій ще немає.';
            root.className =
                'divide-y divide-line px-4 py-10 text-center text-sm text-ink/55';
        } else {
            root.className = 'divide-y divide-line';
        }

        response.data.forEach(category => {
            const row = document.createElement('div');

            row.className =
            'flex items-center justify-between gap-3 px-4 py-3.5';

            const name = document.createElement('span');

            name.textContent =
            '— '.repeat(category.level) + category.name;

            const remove = document.createElement('button');

            remove.textContent = 'Видалити';

            remove.className =
            'shrink-0 rounded-lg border border-red-200 px-3 py-1.5 text-sm font-semibold text-red-700 transition hover:bg-red-50';

            remove.onclick = async () => {
                if (!confirm(
                    'Товари та підкатегорії залишаться без категорії. Видалити?'
                )) return;

                try {
                    await apiFetch(
                        `/api/v1/categories/${category.id}`,
                        { method: 'DELETE' }
                    );

                    showToast(
                        'Категорію видалено',
                        'success'
                    );

                    await loadCategories();

                } catch (error) {
                    showToast(error.message, 'error');
                }
            };

            row.append(name, remove);

            root.append(row);

            parent.add(
                new Option(
                    '— '.repeat(category.level) + category.name,
                           category.id
                )
            );
        });
    }

    form.addEventListener('submit', async event => {
        event.preventDefault();

        const name = form.elements.name.value.trim();

        if (!name || name.length > 100) {
            showToast(
                'Назва має містити від 1 до 100 символів',
                'error'
            );
            return;
        }

        const button = form.querySelector('[type="submit"]');

        button.disabled = true;

        try {
            await apiFetch('/api/v1/categories', {
                method: 'POST',
                body: {
                    name,
                    parent_id: parent.value
                    ? Number(parent.value)
                    : null
                }
            });

            form.reset();

                          showToast(
                              'Категорію додано',
                              'success'
                          );

            await loadCategories();

        } catch (error) {
            showToast(error.message, 'error');

        } finally {
            button.disabled = false;
        }
    });

    loadCategories().catch(error => {
        showToast(error.message, 'error');
    });
});
