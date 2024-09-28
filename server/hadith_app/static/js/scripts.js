document.addEventListener('DOMContentLoaded', () => {
    detectBrowser();
    const copy_button = document.querySelector('#copyButton');
    if (copy_button) {
        copy_button.addEventListener('click', copyToClipboard);
    }
});

function detectBrowser() {
    const userAgent = navigator.userAgent;
    const isMobileOrTablet = /Mobi|Android|iPhone|iPad|Tablet|Mobile/i.test(userAgent);

    if (!isMobileOrTablet) {
        if (userAgent.includes("Chrome") && !userAgent.includes("Edg") && !userAgent.includes("OPR")) {
            document.getElementById('chrome-btn').style.display = 'inline-block';
        } else if (userAgent.includes("Firefox")) {
            document.getElementById('firefox-btn').style.display = 'inline-block';
        }
    }
}

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
