const Cart = (() => {
    const CART_KEY = 'lab6-cart';
    const PROMO_KEY = 'lab6-promo';

    function read() {
        try {
            return JSON.parse(
                localStorage.getItem(CART_KEY) || '[]'
            );
        } catch {
            return [];
        }
    }

    function write(items) {
        localStorage.setItem(
            CART_KEY,
            JSON.stringify(items)
        );

        window.dispatchEvent(
            new Event('cart:changed')
        );
    }

    return {
        items: read,

        add(id) {
            const items = read();

            const existing = items.find(
                item => Number(item.id) === Number(id)
            );

            if (existing) {
                existing.quantity = Math.min(
                    existing.quantity + 1,
                    99
                );
            } else {
                items.push({
                    id: Number(id),
                    quantity: 1
                });
            }

            write(items);
        },

        set(id, quantity) {
            const items = read();

            const item = items.find(
                x => Number(x.id) === Number(id)
            );

            if (!item) return;

            item.quantity = Math.max(
                1,
                Math.min(99, Number(quantity) || 1)
            );

            write(items);
        },

        remove(id) {
            write(
                read().filter(
                    x => Number(x.id) !== Number(id)
                )
            );
        },

        count() {
            return read().reduce(
                (sum, item) => sum + item.quantity,
                0
            );
        },

        clear() {
            write([]);
        },

        setPromo(code, discount) {
            localStorage.setItem(
                PROMO_KEY,
                JSON.stringify({ code, discount })
            );
        },

        getPromo() {
            try {
                return JSON.parse(
                    localStorage.getItem(PROMO_KEY) || 'null'
                );
            } catch {
                return null;
            }
        },

        clearPromo() {
            localStorage.removeItem(PROMO_KEY);
        }
    };
})();

document.addEventListener('DOMContentLoaded', () => {
    const badge = document.getElementById('cart-badge');

    function updateBadge() {
        if (badge) {
            badge.textContent = Cart.count();
        }
    }

    updateBadge();

    window.addEventListener(
        'cart:changed',
        updateBadge
    );
});

