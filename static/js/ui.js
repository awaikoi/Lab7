function showToast(message, type = 'info') {
    const container = document.getElementById('toasts');

    const toast = document.createElement('div');

    const styles = {
        success: {
            iconClass: 'bg-accent/10 text-accent',
            icon: '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z" fill="currentColor" stroke="none"/>'
        },
        error: {
            iconClass: 'bg-red-100 text-red-700',
            icon: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6"/><path d="M12 16.5h.01"/>'
        },
        info: {
            iconClass: 'bg-[#ffd1df] text-ink',
            icon: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>'
        }
    };

    const style = styles[type] || styles.info;
    toast.className =
        'mb-3 flex items-start gap-3 rounded-2xl border border-line bg-surface p-4 text-sm font-medium text-ink shadow-[var(--shadow-md)]';
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

    const icon = document.createElement('span');
    icon.className =
        `flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${style.iconClass}`;
    icon.setAttribute('aria-hidden', 'true');

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('class', 'h-5 w-5');
    svg.innerHTML = style.icon;
    icon.append(svg);

    const text = document.createElement('p');
    text.className = 'pt-1 leading-5';
    text.textContent = message;

    toast.append(icon, text);

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'transition-opacity', 'duration-300');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function flashNext(message, type = 'success') {
    sessionStorage.setItem(
        'flashNext',
        JSON.stringify({ message, type })
    );
}

function setLoading(value) {
    const bar = document.getElementById('loading-bar');

    if (!bar) return;

    bar.style.width = value ? '70%' : '0';
}

document.addEventListener('DOMContentLoaded', () => {
    const saved = sessionStorage.getItem('flashNext');

    if (!saved) return;

    sessionStorage.removeItem('flashNext');

    try {
        const data = JSON.parse(saved);

        showToast(data.message, data.type);
    } catch {
    }
});

