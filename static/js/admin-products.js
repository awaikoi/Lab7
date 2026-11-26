
document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('adminProducts');

    async function loadProducts() {
        try {
            const products = await apiFetch('/api/v1/products');

            root.replaceChildren();

            if (!products.length) {
                const empty = document.createElement('p');
                empty.textContent = 'Товарів поки немає.';
                empty.className =
                    'rounded-2xl border border-dashed border-line bg-surface/50 px-5 py-10 text-center text-sm text-ink/55 md:col-span-3';
                root.append(empty);
                return;
            }

            products.forEach(product => {
                const card = document.createElement('article');

                card.className =
                    'overflow-hidden rounded-2xl border border-line bg-surface p-3 shadow-[var(--shadow-sm)]';

                const image = document.createElement('img');

                image.src = product.image_url || '';
                image.alt = product.name;

                image.className =
                    'mb-3 h-44 w-full rounded-xl bg-[#fff7f9] object-cover';
                if (!product.image_url) {
                    image.classList.add('hidden');
                }

                const name = document.createElement('h2');

                name.textContent = product.name;
                name.className = 'font-bold';

                const category = document.createElement('p');

                category.textContent =
                    product.category_name || 'Без категорії';
                category.className = 'mt-1 text-sm text-ink/55';

                const price = document.createElement('p');

                price.textContent =
                    `${product.final_price} грн`;
                price.className = 'mt-3 text-lg font-bold';

                const edit = document.createElement('a');

                edit.href =
                    `/admin/products/${product.id}/edit`;

                edit.textContent = 'Редагувати';

                edit.className =
                    'rounded-lg border border-accent/20 px-3 py-2 text-sm font-bold text-accent transition hover:bg-[#fff7f9]';

                const remove = document.createElement('button');

                remove.textContent = 'Видалити';
                remove.className =
                    'rounded-lg border border-red-200 px-3 py-2 text-sm font-bold text-red-700 transition hover:bg-red-50';

                remove.onclick = async () => {
                    if (!confirm('Видалити товар?')) return;

                    try {
                        await apiFetch(
                            `/api/v1/products/${product.id}`,
                            { method: 'DELETE' }
                        );

                        card.remove();

                        if (!root.children.length) {
                            const empty = document.createElement('p');
                            empty.textContent = 'Товарів поки немає.';
                            empty.className =
                                'rounded-2xl border border-dashed border-line bg-surface/50 px-5 py-10 text-center text-sm text-ink/55 md:col-span-3';
                            root.append(empty);
                        }

                        showToast('Товар видалено', 'success');

                    } catch (error) {
                        if (error.status === 404) {
                            card.remove();
                        } else {
                            showToast(error.message, 'error');
                        }
                    }
                };

                const actions = document.createElement('div');
                actions.className = 'mt-4 flex flex-wrap gap-2';
                actions.append(edit, remove);
                card.append(image, name, category, price, actions);

                root.append(card);
            });

        } catch (error) {
            root.replaceChildren();

            const message = document.createElement('p');
            message.textContent = error.message;

            const retry = document.createElement('button');
            retry.textContent = 'Повторити';
            retry.onclick = loadProducts;

            root.append(message, retry);
        }
    }

    loadProducts();
});
