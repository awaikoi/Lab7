
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('productForm');

    const id = form.dataset.productId;

    const category = form.elements.category_id;
    const preview = document.getElementById('imagePreview');
    const previewPlaceholder = document.getElementById('imagePreviewPlaceholder');
    const imageInput = form.elements.image;
    const fileInput = form.elements.image_file;
    const errors = document.getElementById('formErrors');
    let existingImageUrl = '';
    let previewObjectUrl = '';

    function showPreview(source) {
        if (previewObjectUrl) {
            URL.revokeObjectURL(previewObjectUrl);
            previewObjectUrl = '';
        }

        preview.hidden = true;
        preview.removeAttribute('src');

        if (!source) {
            previewPlaceholder.textContent = 'Зображення з’явиться тут';
            previewPlaceholder.hidden = false;
            return;
        }

        previewPlaceholder.textContent = 'Завантаження зображення…';
        previewPlaceholder.hidden = false;

        preview.onload = () => {
            preview.hidden = false;
            previewPlaceholder.hidden = true;
        };

        preview.onerror = () => {
            preview.hidden = true;
            previewPlaceholder.textContent =
                'Не вдалося завантажити зображення. Перевірте файл або URL.';
            previewPlaceholder.hidden = false;
        };

        preview.src = source;
    }

    function updatePreview() {
        const file = fileInput.files[0];

        if (file) {
            if (file.size > 5 * 1024 * 1024 ||
                !['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
                showPreview('');
                previewPlaceholder.textContent =
                    'Виберіть JPG, PNG, GIF або WEBP до 5 МБ.';
                return;
            }

            const objectUrl = URL.createObjectURL(file);
            showPreview(objectUrl);
            previewObjectUrl = objectUrl;
            return;
        }

        showPreview(imageInput.value.trim() || existingImageUrl);
    }

    async function initialize() {
        const response = await apiFetch(
            '/api/v2/categories'
        );

        response.data.forEach(item => {
            category.add(
                new Option(
                    '— '.repeat(item.level) + item.name,
                    item.id
                )
            );
        });

        if (!id) return;

        const product = await apiFetch(
            `/api/v1/products/${id}`
        );

        form.elements.name.value = product.name;
        form.elements.price.value = product.price;

        form.elements.discount_percent.value =
            product.discount_percent;

        form.elements.image.value = product.image || '';
        existingImageUrl = product.image_url || '';

        category.value = product.category_id || '';

        updatePreview();
    }

    imageInput.addEventListener('input', updatePreview);
    fileInput.addEventListener('change', updatePreview);

    form.addEventListener('submit', async event => {
        event.preventDefault();

        errors.textContent = '';

        const fields = form.elements;

        const name = fields.name.value.trim();
        const price = Number(fields.price.value);
        const discount = Number(
            fields.discount_percent.value || 0
        );

        const image = fields.image.value.trim();
        const file = fields.image_file.files[0];

        if (!name || name.length > 100) {
            errors.textContent = 'Назва має містити до 100 символів.';
            return;
        }

        if (!Number.isFinite(price) || price < 0) {
            errors.textContent = 'Некоректна ціна.';
            return;
        }

        if (discount < 0 || discount > 100) {
            errors.textContent = 'Знижка має бути від 0 до 100%.';
            return;
        }

        if (image.length > 500) {
            errors.textContent = 'URL надто довгий.';
            return;
        }

        if (file) {
            const allowed = [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp'
            ];

            if (!allowed.includes(file.type) ||
                file.size > 5 * 1024 * 1024) {
                errors.textContent =
                    'Дозволені JPG, PNG, GIF, WEBP до 5 МБ.';

                return;
            }
        }

        const body = {
            name,
            price,
            image,
            discount_percent: discount,
            category_id: category.value
                ? Number(category.value)
                : null
        };

        const button = form.querySelector('[type="submit"]');

        button.disabled = true;

        try {
            const product = await apiFetch(
                id
                    ? `/api/v1/products/${id}`
                    : '/api/v1/products',
                {
                    method: id ? 'PUT' : 'POST',
                    body
                }
            );

            if (file) {
                const formData = new FormData();

                formData.append('image_file', file);

                try {
                    await apiFetch(
                        `/api/v1/products/${product.id}/image`,
                        {
                            method: 'POST',
                            body: formData
                        }
                    );
                } catch (error) {
                    showToast(
                        `Товар збережено, але зображення не завантажено: ${error.message}`,
                        'error'
                    );

                    return;
                }
            }

            flashNext('Товар успішно збережено');

            location.href = '/admin/products';

        } catch (error) {
            errors.textContent = error.message;

        } finally {
            button.disabled = false;
        }
    });

    initialize().catch(error => {
        if (error.status === 404) {
            errors.textContent = 'Товар не знайдено.';
        } else {
            errors.textContent = error.message;
        }
    });
});
