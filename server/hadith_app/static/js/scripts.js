document.addEventListener('DOMContentLoaded', () => {
    detectBrowser();
    const copy_button = document.querySelector('#copyButton');
    if (copy_button) {
        copy_button.addEventListener('click', copyToClipboard);
    }
    const show_new_hadith_button = document.querySelector('#showNewHadith');
    if (show_new_hadith_button) {
        show_new_hadith_button.addEventListener('click', fetchNewHadith);
    }
});

async function fetchNewHadith() {
    const url = window.location.href + `/api/fetch-hadith?fetch-mode=random`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const hadith = await response.json();
        if (hadith) {
            const quoteEnglish = hadith.hadithEnglish || 'English version not available';
            const quoteArabic = hadith.hadithArabic || 'Arabic version not available';
            const bookName = hadith.book?.bookName || 'Book name not available';
            const writerName = hadith.book?.writerName || 'Writer name not available';
            const source = `Source: ${bookName} by ${writerName}`;
            document.getElementById('quoteEnglish').textContent = quoteEnglish;
            document.getElementById('quoteArabic').textContent = quoteArabic;
            document.getElementById('source').textContent = source;

            // Show the copy button after successful fetch
            document.getElementById('copyButton').style.display = 'flex';
        } else {
            document.getElementById('quoteEnglish').textContent = 'No hadith found.';
            document.getElementById('quoteArabic').textContent = '';
            document.getElementById('source').textContent = '';
        }
    } catch (error) {
        console.error('Failed to fetch the hadith:', error);
        document.getElementById('quoteEnglish').textContent = 'Failed to fetch hadith. Please try again later.';
        document.getElementById('quoteArabic').textContent = '';
        document.getElementById('source').textContent = '';
    }
}

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
