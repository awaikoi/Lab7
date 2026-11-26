
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('filterForm');
    const products = document.getElementById('products');
    const pagination = document.getElementById('pagination');

    let page = 1;
    let requestNumber = 0;
    let searchTimer;

    async function loadCategories() {
        const response = await apiFetch(
            '/api/v2/categories'
        );

        const select = form.elements.category;

        response.data.forEach(category => {
            select.add(
                new Option(
                    '— '.repeat(category.level) + category.name,
                    category.id
                )
            );
        });
    }

    function createProductCard(product) {
        const card = document.createElement('article');

        card.className =
            'product-card group flex min-h-[390px] flex-col overflow-hidden rounded-2xl border border-line bg-surface p-3';

        const image = document.createElement('img');

        image.src = product.image_url || '';
        image.alt = product.name;

        image.className =
            'h-52 w-full rounded-xl bg-[#f5f2ed] object-cover';

        if (!product.image_url) {
            image.classList.add('hidden');
        }

        const name = document.createElement('h2');
        name.textContent = product.name;
        name.className = 'mt-4 px-1 text-base font-bold leading-6';

        const category = document.createElement('p');
        category.textContent =
            product.category_name || 'Без категорії';

        category.className = 'mt-1 px-1 text-xs text-ink/50';

        card.append(image);

        const discountWrap = document.createElement('div');
        discountWrap.className = 'mt-3 flex min-h-7 items-center px-1';

        if (Number(product.discount_percent) > 0) {
            const oldPrice = document.createElement('p');

            oldPrice.textContent =
                `${product.price} грн`;

            oldPrice.className =
                'mr-2 text-sm text-ink/40 line-through';

            const discount = document.createElement('span');

            discount.textContent =
                `-${product.discount_percent}%`;

            discount.className =
                'rounded-md bg-accent px-2 py-1 text-[11px] font-bold text-white';

            discountWrap.append(oldPrice, discount);
        }

        card.append(name, category, discountWrap);

        const price = document.createElement('p');

        price.textContent =
            `${product.final_price} грн`;

        price.className = 'mt-auto px-1 pb-3 text-xl font-bold';

        const button = document.createElement('button');

        button.type = 'button';
        button.textContent = 'В кошик';

        button.className =
            'mt-1 w-full rounded-xl bg-accent px-4 py-3 text-sm font-bold text-white shadow-[0_6px_16px_rgba(136,19,55,.12)] hover:bg-[#9f1239]';

        button.addEventListener('click', () => {
            Cart.add(product.id);

            showToast(
                `«${product.name}» додано до кошика`,
                'success'
            );
        });

        card.append(price, button);

        return card;
    }

    function renderPagination(meta) {
        pagination.replaceChildren();

        pagination.className =
            'mt-8 flex flex-wrap items-center justify-center gap-2';

        const previous = document.createElement('button');
        previous.textContent = '←';
        previous.disabled = page <= 1;
        previous.className =
            'h-10 min-w-10 rounded-xl border border-line bg-surface px-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-40';

        previous.onclick = () => {
            page--;
            loadProducts();
        };

        pagination.append(previous);

        for (let i = 1; i <= meta.pages; i++) {
            const button = document.createElement('button');

            button.textContent = i;
            button.disabled = i === page;

            button.className =
                `h-10 min-w-10 rounded-xl border px-3 text-sm font-semibold transition ${
                    i === page
                        ? 'border-accent bg-accent text-white'
                        : 'border-line bg-surface text-ink/70 hover:border-accent/30 hover:text-accent'
                }`;

            button.onclick = () => {
                page = i;
                loadProducts();
            };

            pagination.append(button);
        }

        const next = document.createElement('button');

        next.textContent = '→';
        next.disabled = page >= meta.pages;
        next.className =
            'h-10 min-w-10 rounded-xl border border-line bg-surface px-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-40';

        next.onclick = () => {
            page++;
            loadProducts();
        };

        pagination.append(next);
    }

    async function loadProducts() {
        const currentRequest = ++requestNumber;

        const min = form.elements.min_price.value;
        const max = form.elements.max_price.value;

        if (min && max && Number(min) > Number(max)) {
            showToast(
                'Мінімальна ціна більша за максимальну.',
                'error'
            );
            return;
        }

        const params = new URLSearchParams();

        params.set('page', page);
        params.set('per_page', 12);

        const fields = [
            ['q', 'q'],
            ['category', 'category_id'],
            ['min_price', 'min_price'],
            ['max_price', 'max_price'],
            ['sort', 'sort']
        ];

        fields.forEach(([field, parameter]) => {
            const value = form.elements[field].value;

            if (value) {
                params.set(parameter, value);
            }
        });

        if (form.elements.on_sale.checked) {
            params.set('on_sale', 'true');
        }

        try {
            setLoading(true);

            const response = await apiFetch(
                `/api/v2/products?${params}`
            );

            if (currentRequest !== requestNumber) return;

            products.replaceChildren();

            if (!response.data.length) {
                products.textContent = 'Товарів не знайдено.';
            }

            response.data.forEach(product => {
                products.append(
                    createProductCard(product)
                );
            });

            renderPagination(response.meta);

        } catch (error) {
            products.replaceChildren();

            const message = document.createElement('p');
            message.textContent = error.message;

            const retry = document.createElement('button');
            retry.textContent = 'Повторити';
            retry.onclick = loadProducts;

            products.append(message, retry);

        } finally {
            setLoading(false);
        }
    }

    form.addEventListener('input', event => {
        page = 1;

        if (event.target.name === 'q') {
            clearTimeout(searchTimer);

            searchTimer = setTimeout(
                loadProducts,
                400
            );
        } else {
            loadProducts();
        }
    });

    form.addEventListener('change', () => {
        page = 1;
        loadProducts();
    });

    form.addEventListener('reset', () => {
        setTimeout(() => {
            page = 1;
            loadProducts();
        }, 0);
    });

    loadCategories()
        .then(loadProducts)
        .catch(error => showToast(error.message, 'error'));
});
