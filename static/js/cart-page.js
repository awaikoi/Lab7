
document.addEventListener('DOMContentLoaded', () => {
    const lines = document.getElementById('cartLines');
    const summary = document.getElementById('summary');
    const empty = document.getElementById('emptyCart');
    const orderSuccess = document.getElementById('orderSuccess');
    const orderSuccessMessage = document.getElementById('orderSuccessMessage');

    const promoForm = document.getElementById('promoForm');
    const checkoutForm = document.getElementById('checkoutForm');
    const cartLayout = document.getElementById('cartLayout');

    let products = [];
    let promo = Cart.getPromo();

    function element(tag, text) {
        const node = document.createElement(tag);

        if (text !== undefined) {
            node.textContent = text;
        }

        return node;
    }

    function subtotal() {
        return products.reduce(
            (sum, item) =>
                sum + Number(item.product.final_price) *
                item.quantity,
            0
        );
    }

    function calculateTotal() {
        return Math.max(
            0,
            subtotal() - Number(promo?.discount || 0)
        );
    }

    function render() {
        lines.replaceChildren();

        if (!products.length) {
            empty.hidden = false;
            orderSuccess.hidden = true;
            cartLayout.hidden = true;
            promoForm.hidden = true;
            checkoutForm.hidden = true;
            summary.textContent = '';
            return;
        }

        empty.hidden = true;
        orderSuccess.hidden = true;
        cartLayout.hidden = false;
        promoForm.hidden = false;
        checkoutForm.hidden = false;

        products.forEach(item => {
            const product = item.product;

            const row = element('div');

            row.className =
                'grid items-center gap-3 py-4 sm:grid-cols-[88px_1fr_120px_80px_100px]';

            const image = element('img');
            image.src = product.image_url || '';
            image.alt = product.name;
            image.className =
                'h-20 w-20 rounded-xl border border-line bg-[#fff7f9] object-cover';
            if (!product.image_url) {
                image.classList.add('hidden');
            }

            const name = element('strong', product.name);
            name.className = 'leading-5';

            const price = element(
                'span',
                `${product.final_price} грн / шт.`
            );

            const quantity = element('input');

            quantity.type = 'number';
            quantity.min = 1;
            quantity.max = 99;
            quantity.value = item.quantity;

            quantity.className =
                'w-20 rounded-xl border border-line bg-[#fbfaf8] px-3 py-2';

            quantity.addEventListener('change', () => {
                Cart.set(product.id, quantity.value);
            });

            const total = element(
                'strong',
                `${(
                    Number(product.final_price) *
                    item.quantity
                ).toFixed(2)} грн`
            );

            const remove = element('button', 'Видалити');

            remove.className = 'justify-self-start text-sm font-semibold text-red-700 hover:underline sm:justify-self-end';

            remove.onclick = () => {
                Cart.remove(product.id);
            };

            row.append(
                image,
                name,
                price,
                quantity,
                total,
                remove
            );

            lines.append(row);
        });

        summary.textContent =
            `Разом: ${calculateTotal().toFixed(2)} грн`;
    }

    async function loadCart() {
        const items = Cart.items();

        if (!items.length) {
            products = [];
            render();
            return;
        }

        const results = await Promise.all(
            items.map(async item => {
                try {
                    const product = await apiFetch(
                        `/api/v1/products/${item.id}`
                    );

                    return {
                        product,
                        quantity: item.quantity
                    };

                } catch (error) {
                    if (error.status === 404) {
                        Cart.remove(item.id);

                        showToast(
                            'Видалений товар прибрано з кошика',
                            'info'
                        );

                        return null;
                    }

                    throw error;
                }
            })
        );

        products = results.filter(Boolean);

        render();
    }

    async function validatePromo() {
        const code = promoForm.elements.code.value.trim();

        if (!code) {
            promo = null;
            Cart.clearPromo();
            render();
            return;
        }

        try {
            const response = await apiFetch(
                `/api/v1/promocodes/${encodeURIComponent(code)}` +
                `/validate?subtotal=${subtotal()}`
            );

            if (!response.valid) {
                promo = null;
                Cart.clearPromo();

                showToast(
                    response.reason || 'Промокод недійсний',
                    'error'
                );

                render();
                return;
            }

            promo = {
                code,
                discount: Number(response.discount)
            };

            Cart.setPromo(code, response.discount);

            showToast(
                `Знижка ${response.discount} грн застосована`,
                'success'
            );

            render();

        } catch (error) {
            showToast(
                error.status === 404
                    ? 'Промокод не існує'
                    : error.message,
                'error'
            );
        }
    }

    promoForm.addEventListener('submit', event => {
        event.preventDefault();
        validatePromo();
    });

    checkoutForm.addEventListener('submit', async event => {
        event.preventDefault();

        const fields = checkoutForm.elements;

        const email = fields.email.value.trim();
        const address = fields.address.value.trim();

        document.querySelectorAll('[data-error]').forEach(node => {
            node.textContent = '';
        });

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            document.querySelector('[data-error="email"]').textContent =
                'Вкажіть коректний email';

            return;
        }

        if (!address || address.length > 300) {
            document.querySelector('[data-error="address"]').textContent =
                'Перевірте адресу';

            return;
        }

        const button = checkoutForm.querySelector(
            '[type="submit"]'
        );

        button.disabled = true;

        try {
            const order = await apiFetch('/api/v1/orders', {
                method: 'POST',

                body: {
                    email,
                    address,
                    promo_code: promo?.code || null,

                    items: products.map(item => ({
                        product_id: item.product.id,
                        quantity: item.quantity
                    }))
                }
            });

            Cart.clear();
            Cart.clearPromo();

            promo = null;
            products = [];
            orderSuccessMessage.textContent =
                `Номер замовлення: ${order.id}. Сума: ${order.total_price} грн. Дякуємо за покупку!`;
            orderSuccess.hidden = false;
            summary.textContent = '';

            promoForm.hidden = true;
            checkoutForm.hidden = true;
            empty.hidden = true;
            cartLayout.hidden = true;

        } catch (error) {
            const details = error.details || {};

            if (details.email) {
                document.querySelector('[data-error="email"]').textContent =
                    details.email;
            }

            if (details.address) {
                document.querySelector('[data-error="address"]').textContent =
                    details.address;
            }

            showToast(error.message, 'error');

        } finally {
            button.disabled = false;
        }
    });

    window.addEventListener('cart:changed', () => {
        loadCart().catch(error => {
            showToast(error.message, 'error');
        });
    });

    loadCart().catch(error => {
        showToast(error.message, 'error');
    });
});
