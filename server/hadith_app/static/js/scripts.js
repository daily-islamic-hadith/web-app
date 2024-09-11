document.addEventListener('DOMContentLoaded', () => {
    const copy_button = document.querySelector('#copyButton');
    if (copy_button) {
        copy_button.addEventListener('click', copyToClipboard);
    }
});

async function copyToClipboard() {
    const quoteEnglish = document.getElementById('quoteEnglish').textContent;
    const quoteArabic = document.getElementById('quoteArabic').textContent;
    const source = document.getElementById('source').textContent;
    const textToCopy = `${quoteEnglish}\n\n${quoteArabic}\n\n${source}`;

    try {
        await navigator.clipboard.writeText(textToCopy);
        showNotification();
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
}

function showNotification() {
    const notification = document.getElementById('notification');
    notification.className = 'show';
    setTimeout(() => {
        notification.className = notification.className.replace('show', '');
    }, 3000);
}
